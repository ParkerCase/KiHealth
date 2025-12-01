"""
PHASE 3: Complete Copy Number Analysis
Analyze gene amplifications/deletions and their impact on dependency
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("PHASE 3: COMPLETE COPY NUMBER ANALYSIS")
print("="*80)

# Load DepMap dependency data
print("\nLoading dependency data...")
depmap = pd.read_csv('data/raw/depmap/CRISPRGeneDependency.csv', index_col=0)
depmap = depmap.reset_index()
depmap.columns.values[0] = 'ModelID'

targets = {
    'STK17A': [col for col in depmap.columns if 'STK17A' in col and 'STK17B' not in col][0],
    'MYLK4': [col for col in depmap.columns if 'MYLK4' in col][0],
    'TBK1': [col for col in depmap.columns if 'TBK1' in col][0],
    'CLK4': [col for col in depmap.columns if 'CLK4' in col][0]
}

dep_clean = depmap[['ModelID'] + list(targets.values())].copy()
dep_clean.columns = ['ModelID', 'STK17A_dep', 'MYLK4_dep', 'TBK1_dep', 'CLK4_dep']

print(f"Dependency data: {len(dep_clean)} cell lines")

# Load copy number data
print("\nLoading copy number data...")
cn = pd.read_csv('data/raw/depmap/OmicsCNGeneWGS.csv')

# Find target gene columns in CN data
cn_targets = {}
for gene in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
    matching = [col for col in cn.columns if gene in col]
    if matching:
        cn_targets[gene] = matching[0]
        print(f"  {gene}: {matching[0]}")
    else:
        print(f"  {gene}: NOT FOUND")

cn_clean = cn[['ModelID'] + list(cn_targets.values())].copy()
cn_clean.columns = ['ModelID'] + [f'{g}_cn' for g in cn_targets.keys()]

print(f"Copy number data: {len(cn_clean)} cell lines")

# Merge dependency and copy number
print("\nMerging datasets...")
merged = dep_clean.merge(cn_clean, on='ModelID', how='inner')
print(f"Merged data: {len(merged)} cell lines")

# Load model info for cancer types
print("\nLoading cancer type info...")
model = pd.read_csv('data/raw/depmap/Model.csv')
merged = merged.merge(
    model[['ModelID', 'OncotreePrimaryDisease', 'OncotreeLineage']],
    on='ModelID',
    how='left'
)

print(f"Final dataset: {len(merged)} cell lines with cancer type info")

# Classify copy number status
print("\n" + "="*80)
print("CLASSIFYING COPY NUMBER STATUS")
print("="*80)

for gene in cn_targets.keys():
    cn_col = f'{gene}_cn'
    
    # Classify: Amplified (CN > 0.5), Normal (-0.5 to 0.5), Deleted (CN < -0.5)
    merged[f'{gene}_amp'] = (merged[cn_col] > 0.5).astype(int)
    merged[f'{gene}_del'] = (merged[cn_col] < -0.5).astype(int)
    merged[f'{gene}_normal'] = ((merged[cn_col] >= -0.5) & (merged[cn_col] <= 0.5)).astype(int)
    
    n_amp = merged[f'{gene}_amp'].sum()
    n_del = merged[f'{gene}_del'].sum()
    n_normal = merged[f'{gene}_normal'].sum()
    
    print(f"\n{gene}:")
    print(f"  Amplified: {n_amp} ({n_amp/len(merged)*100:.1f}%)")
    print(f"  Normal: {n_normal} ({n_normal/len(merged)*100:.1f}%)")
    print(f"  Deleted: {n_del} ({n_del/len(merged)*100:.1f}%)")

# Analyze impact of copy number on dependency
print("\n" + "="*80)
print("COPY NUMBER IMPACT ON DEPENDENCY")
print("="*80)

cn_impact_results = []

for gene in cn_targets.keys():
    dep_col = f'{gene}_dep'
    amp_col = f'{gene}_amp'
    del_col = f'{gene}_del'
    normal_col = f'{gene}_normal'
    
    print(f"\n{gene}:")
    
    # Amplified vs Normal
    amp_data = merged[merged[amp_col] == 1][dep_col].dropna()
    normal_data = merged[merged[normal_col] == 1][dep_col].dropna()
    
    if len(amp_data) >= 3 and len(normal_data) >= 10:
        amp_mean = amp_data.mean()
        normal_mean = normal_data.mean()
        
        t_stat, p_val = stats.ttest_ind(amp_data, normal_data, equal_var=False)
        
        print(f"  Amplified (n={len(amp_data)}): mean={amp_mean:.4f}")
        print(f"  Normal (n={len(normal_data)}): mean={normal_mean:.4f}")
        print(f"  Difference: {amp_mean - normal_mean:.4f}")
        print(f"  p-value: {p_val:.4e}")
        
        cn_impact_results.append({
            'gene': gene,
            'comparison': 'Amplified vs Normal',
            'n_amp': len(amp_data),
            'n_normal': len(normal_data),
            'amp_mean': amp_mean,
            'normal_mean': normal_mean,
            'mean_diff': amp_mean - normal_mean,
            'p_value': p_val
        })
    
    # Deleted vs Normal
    del_data = merged[merged[del_col] == 1][dep_col].dropna()
    
    if len(del_data) >= 3 and len(normal_data) >= 10:
        del_mean = del_data.mean()
        
        t_stat, p_val = stats.ttest_ind(del_data, normal_data, equal_var=False)
        
        print(f"  Deleted (n={len(del_data)}): mean={del_mean:.4f}")
        print(f"  Normal (n={len(normal_data)}): mean={normal_mean:.4f}")
        print(f"  Difference: {del_mean - normal_mean:.4f}")
        print(f"  p-value: {p_val:.4e}")
        
        cn_impact_results.append({
            'gene': gene,
            'comparison': 'Deleted vs Normal',
            'n_deleted': len(del_data),
            'n_normal': len(normal_data),
            'deleted_mean': del_mean,
            'normal_mean': normal_mean,
            'mean_diff': del_mean - normal_mean,
            'p_value': p_val
        })

# Save CN impact results
cn_impact_df = pd.DataFrame(cn_impact_results)
cn_impact_df.to_csv('data/processed/copy_number_impact.csv', index=False)
print(f"\n✅ Saved: data/processed/copy_number_impact.csv")

# Per-cancer-type copy number analysis
print("\n" + "="*80)
print("PER-CANCER-TYPE COPY NUMBER ANALYSIS")
print("="*80)

cancer_cn_results = []

for cancer in merged['OncotreePrimaryDisease'].dropna().unique():
    cancer_data = merged[merged['OncotreePrimaryDisease'] == cancer]
    
    if len(cancer_data) < 3:
        continue
    
    cancer_result = {
        'cancer_type': cancer,
        'n_cell_lines': len(cancer_data)
    }
    
    for gene in cn_targets.keys():
        amp_col = f'{gene}_amp'
        del_col = f'{gene}_del'
        cn_col = f'{gene}_cn'
        
        # Amplification frequency
        amp_freq = cancer_data[amp_col].sum() / len(cancer_data) * 100
        del_freq = cancer_data[del_col].sum() / len(cancer_data) * 100
        
        cancer_result[f'{gene}_amp_pct'] = amp_freq
        cancer_result[f'{gene}_del_pct'] = del_freq
        cancer_result[f'{gene}_cn_mean'] = cancer_data[cn_col].mean()
        cancer_result[f'{gene}_cn_std'] = cancer_data[cn_col].std()
    
    # Any target amplified
    any_amp = (cancer_data[[f'{g}_amp' for g in cn_targets.keys()]].sum(axis=1) > 0).sum()
    cancer_result['any_target_amp_pct'] = any_amp / len(cancer_data) * 100
    
    cancer_cn_results.append(cancer_result)

# Convert to DataFrame
cancer_cn_df = pd.DataFrame(cancer_cn_results)

# Calculate copy_number_score for integration
def calculate_cn_score(row):
    # Score based on amplification frequency across all 4 targets
    amp_scores = []
    for gene in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
        amp_pct = row[f'{gene}_amp_pct']
        if not pd.isna(amp_pct):
            # Higher amplification = higher score
            amp_scores.append(amp_pct / 100.0)
    
    return np.mean(amp_scores) if amp_scores else 0.0

cancer_cn_df['copy_number_score'] = cancer_cn_df.apply(calculate_cn_score, axis=1)

# Save results
cancer_cn_df.to_csv('data/processed/copy_number_analysis_COMPLETE.csv', index=False)
print(f"\n✅ Saved: data/processed/copy_number_analysis_COMPLETE.csv")

# Show top cancer types by amplification
print("\n" + "="*80)
print("TOP 20 CANCER TYPES BY AMPLIFICATION FREQUENCY")
print("="*80)

top20 = cancer_cn_df.nsmallest(20, 'any_target_amp_pct')  # Changed to nsmallest for lowest amp

print(f"\n{'Rank':<6}{'Cancer Type':<45}{'N':<6}{'Any Amp %':<12}{'CN Score':<12}")
print("-" * 85)

for rank, (idx, row) in enumerate(top20.iterrows(), 1):
    cancer = row['cancer_type'][:44]
    n = int(row['n_cell_lines'])
    amp_pct = row['any_target_amp_pct']
    cn_score = row['copy_number_score']
    print(f"{rank:<6}{cancer:<45}{n:<6}{amp_pct:>10.1f}%   {cn_score:.4f}")

print("\n" + "="*80)
print("PHASE 3 COMPLETE")
print("="*80)
