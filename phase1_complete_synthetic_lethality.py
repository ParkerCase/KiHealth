"""
PHASE 1: Complete Synthetic Lethality Analysis
Using ALL DepMap data - no filtering
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("PHASE 1: COMPLETE SYNTHETIC LETHALITY ANALYSIS")
print("="*80)

# Load FULL DepMap dependency data (all cell lines)
print("\nLoading DepMap dependency data...")
depmap = pd.read_csv('data/raw/depmap/CRISPRGeneDependency.csv', index_col=0)
depmap = depmap.reset_index()
depmap.columns.values[0] = 'ModelID'  # Rename first column
print(f"Total cell lines in DepMap: {len(depmap)}")

# Get our target gene columns
targets = {
    'STK17A': [col for col in depmap.columns if 'STK17A' in col and 'STK17B' not in col][0],
    'MYLK4': [col for col in depmap.columns if 'MYLK4' in col][0],
    'TBK1': [col for col in depmap.columns if 'TBK1' in col][0],
    'CLK4': [col for col in depmap.columns if 'CLK4' in col][0]
}

print("\nTarget gene columns found:")
for gene, col in targets.items():
    print(f"  {gene}: {col}")

# Create clean dataframe
dep_clean = depmap[['ModelID'] + list(targets.values())].copy()
dep_clean.columns = ['ModelID', 'STK17A', 'MYLK4', 'TBK1', 'CLK4']

print(f"\nDependency data shape: {dep_clean.shape}")
print(f"Missing values per gene:")
for gene in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
    missing = dep_clean[gene].isna().sum()
    print(f"  {gene}: {missing} ({missing/len(dep_clean)*100:.1f}%)")

# Load HOTSPOT mutations
print("\n" + "="*80)
print("Loading HOTSPOT mutations...")
mutations_hotspot = pd.read_csv('data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv')
print(f"Cell lines with hotspot data: {len(mutations_hotspot)}")

# Find mutation columns
mutation_genes = ['PTEN', 'KRAS', 'PIK3CA', 'EGFR', 'NRAS', 'HRAS', 
                  'BRAF', 'TP53', 'STK11', 'NFE2L2', 'KEAP1']

hotspot_cols = {}
for gene in mutation_genes:
    matching = [col for col in mutations_hotspot.columns if gene in col and 'mutation' not in col.lower()]
    if matching:
        hotspot_cols[gene] = matching[0]

print(f"Hotspot mutations found: {len(hotspot_cols)}")
for gene, col in hotspot_cols.items():
    n_mutant = (mutations_hotspot[col] == 1).sum()
    print(f"  {gene}: {n_mutant} mutant cell lines")

# Load DAMAGING mutations
print("\n" + "="*80)
print("Loading DAMAGING mutations...")
try:
    mutations_damaging = pd.read_csv('data/raw/depmap/OmicsSomaticMutationsMatrixDamaging.csv')
    print(f"Cell lines with damaging mutation data: {len(mutations_damaging)}")
    
    damaging_cols = {}
    for gene in mutation_genes:
        matching = [col for col in mutations_damaging.columns if gene in col and 'mutation' not in col.lower()]
        if matching:
            damaging_cols[gene] = matching[0]
    
    print(f"Damaging mutations found: {len(damaging_cols)}")
    for gene, col in damaging_cols.items():
        n_mutant = (mutations_damaging[col] == 1).sum()
        print(f"  {gene}: {n_mutant} mutant cell lines")
    
    has_damaging = True
except FileNotFoundError:
    print("⚠️  Damaging mutations file not found - using hotspot only")
    has_damaging = False

# Run synthetic lethality analysis
print("\n" + "="*80)
print("Running Synthetic Lethality Analysis...")
print("="*80)

results = []

# For each mutation type
mutation_types = ['hotspot']
if has_damaging:
    mutation_types.append('damaging')

for mut_type in mutation_types:
    print(f"\nAnalyzing {mut_type.upper()} mutations...")
    
    if mut_type == 'hotspot':
        mut_data = mutations_hotspot
        mut_cols = hotspot_cols
    else:
        mut_data = mutations_damaging
        mut_cols = damaging_cols
    
    # For each mutation gene
    for mut_gene, mut_col in mut_cols.items():
        
        # Merge mutation data with dependency
        merged = dep_clean.merge(
            mut_data[['ModelID', mut_col]],
            on='ModelID',
            how='left'
        )
        
        # Fill missing mutations as wild-type (0)
        merged[mut_col] = merged[mut_col].fillna(0)
        
        # For each target gene
        for target_gene in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
            
            # Split into mutant and wild-type groups
            mutant = merged[merged[mut_col] == 1][target_gene].dropna()
            wt = merged[merged[mut_col] == 0][target_gene].dropna()
            
            if len(mutant) < 3 or len(wt) < 10:
                continue  # Need minimum sample sizes
            
            # Calculate statistics
            mutant_mean = mutant.mean()
            wt_mean = wt.mean()
            mean_diff = mutant_mean - wt_mean
            
            # Welch's t-test
            t_stat, p_val = stats.ttest_ind(mutant, wt, equal_var=False)
            
            # Store result
            results.append({
                'mutation_type': mut_type,
                'mutation': mut_gene,
                'target': target_gene,
                'n_mutant': len(mutant),
                'n_wt': len(wt),
                'mutant_mean': mutant_mean,
                'wt_mean': wt_mean,
                'mean_diff': mean_diff,
                't_statistic': t_stat,
                'p_value': p_val,
                'is_synthetic_lethal': mean_diff < 0,  # NEGATIVE = SL
                'significant': p_val < 0.10
            })

# Convert to DataFrame
results_df = pd.DataFrame(results)

print(f"\nTotal combinations tested: {len(results_df)}")
print(f"Significant results (p < 0.10): {(results_df['p_value'] < 0.10).sum()}")
print(f"True synthetic lethality (Δ < 0, p < 0.10): {((results_df['mean_diff'] < 0) & (results_df['p_value'] < 0.10)).sum()}")

# Save complete results
results_df.to_csv('data/processed/synthetic_lethality_COMPLETE.csv', index=False)
print(f"\n✅ Saved: data/processed/synthetic_lethality_COMPLETE.csv")

# Show TRUE synthetic lethality candidates
print("\n" + "="*80)
print("TRUE SYNTHETIC LETHALITY CANDIDATES")
print("(Negative Δ = mutants MORE dependent, p < 0.10)")
print("="*80)

true_sl = results_df[(results_df['mean_diff'] < 0) & (results_df['p_value'] < 0.10)].sort_values('p_value')

if len(true_sl) > 0:
    for idx, row in true_sl.iterrows():
        print(f"\n{row['mutation']} × {row['target']} ({row['mutation_type']})")
        print(f"  Effect size (Δ): {row['mean_diff']:.4f} (NEGATIVE = SL)")
        print(f"  Mutant cells: {row['mutant_mean']:.4f} (n={row['n_mutant']})")
        print(f"  Wild-type cells: {row['wt_mean']:.4f} (n={row['n_wt']})")
        print(f"  p-value: {row['p_value']:.4e}")
        print(f"  ✅ TRUE SYNTHETIC LETHALITY")
else:
    print("\n⚠️  NO significant synthetic lethality found with p < 0.10")
    print("\nMost promising (lowest p-value, negative Δ):")
    
    sl_candidates = results_df[results_df['mean_diff'] < 0].sort_values('p_value').head(10)
    for idx, row in sl_candidates.iterrows():
        print(f"\n{row['mutation']} × {row['target']} ({row['mutation_type']})")
        print(f"  Effect size (Δ): {row['mean_diff']:.4f}")
        print(f"  p-value: {row['p_value']:.4e}")

# Show suppressor interactions (for comparison)
print("\n" + "="*80)
print("SUPPRESSOR INTERACTIONS (NOT therapeutic targets)")
print("(Positive Δ = mutants LESS dependent, p < 0.10)")
print("="*80)

suppressors = results_df[(results_df['mean_diff'] > 0) & (results_df['p_value'] < 0.10)].sort_values('p_value').head(10)

for idx, row in suppressors.iterrows():
    print(f"\n{row['mutation']} × {row['target']} ({row['mutation_type']})")
    print(f"  Effect size (Δ): {row['mean_diff']:.4f} (POSITIVE = NOT SL)")
    print(f"  p-value: {row['p_value']:.4e}")
    print(f"  ⚠️  This is suppressor/compensatory, not synthetic lethality")

print("\n" + "="*80)
print("PHASE 1 COMPLETE")
print("="*80)
