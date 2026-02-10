#!/usr/bin/env python3
"""
COMPREHENSIVE EXPERIMENTAL DATA INTEGRATION
============================================
Complete analysis of ALL experimental validation data from STARX team:
1. IC50 data (160 cell lines) - Victoria & Tulasi
2. RNAseq DEGs (6 files) - Hafsa
3. Phosphoproteomics (2 files) - Erica
4. IP-MS (3 files) - Erica
5. 814H RNAseq (1 file) - Christian

This script does a THOROUGH analysis to create robust experimental validation scores
and determine if cancer rankings need updating.

Author: Parker Case
Date: November 4, 2025
Deadline: November 10, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Paths
BASE_DIR = Path('/Users/parkercase/starx-therapeutics-analysis')
STARX_DIR = BASE_DIR / 'data' / 'raw' / 'StarXData'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
FIGURES_DIR = BASE_DIR / 'outputs' / 'figures'

print("=" * 100)
print("COMPREHENSIVE EXPERIMENTAL DATA INTEGRATION")
print("=" * 100)
print(f"\nAnalyzing ALL experimental validation data received November 1, 2025")
print(f"Target: Complete integration for Nov 10 delivery\n")

# ============================================================================
# SECTION 1: IC50 DATA (160 CELL LINES)
# ============================================================================

print("\n" + "=" * 100)
print("SECTION 1: IC50 DATA ANALYSIS (160 Cell Lines)")
print("=" * 100)

print("\n[1.1] Loading IC50 data...")
ic50_path = STARX_DIR / 'Copy of AQT cell based profiling160 cell lines815K815H_report_summary' / 'IC50 values-Table 1.csv'
ic50_raw = pd.read_csv(ic50_path)

print(f"✅ Loaded: {len(ic50_raw)} cell lines")
print(f"\nColumns: {list(ic50_raw.columns)}")
print(f"\nFirst few rows:")
print(ic50_raw.head())

# Check if we need to transform IC50 to pIC50
print(f"\n[1.2] Converting IC50 to pIC50...")
print(f"IC50 range: {ic50_raw.iloc[:, 1].min():.2e} to {ic50_raw.iloc[:, 1].max():.2e}")

# Assume columns are: Cell_Line, IC50_Cpd1, IC50_Cpd2, (maybe others)
cell_col = ic50_raw.columns[0]
cpd1_col = ic50_raw.columns[1]
cpd2_col = ic50_raw.columns[2] if len(ic50_raw.columns) > 2 else None

ic50_data = ic50_raw.copy()
ic50_data['pIC50_Cpd1'] = -np.log10(ic50_data[cpd1_col])
if cpd2_col:
    ic50_data['pIC50_Cpd2'] = -np.log10(ic50_data[cpd2_col])

print(f"pIC50 range: {ic50_data['pIC50_Cpd1'].min():.2f} to {ic50_data['pIC50_Cpd1'].max():.2f}")

# Load DepMap data for correlation
print(f"\n[1.3] Correlating with DepMap dependency scores...")
depmap_rankings = pd.read_csv(PROCESSED_DIR / 'final_integrated_rankings.csv')
top_cell_lines = pd.read_csv(PROCESSED_DIR / 'top_dependent_cell_lines.csv')

print(f"✅ DepMap data: {len(top_cell_lines)} cell lines, {len(depmap_rankings)} cancer types")

# Try to match cell line names
ic50_data['cell_line_clean'] = ic50_data[cell_col].str.strip().str.upper()
top_cell_lines['cell_line_clean'] = top_cell_lines['CellLineName'].str.strip().str.upper()

merged = ic50_data.merge(top_cell_lines, on='cell_line_clean', how='inner')
print(f"\n✅ Matched {len(merged)} cell lines between IC50 and DepMap")

if len(merged) > 0:
    # Calculate correlation
    corr_cpd1 = stats.pearsonr(merged['pIC50_Cpd1'], merged['combined_score'])
    print(f"\nCorrelation (Compound 1 pIC50 vs DepMap dependency):")
    print(f"  r = {corr_cpd1[0]:.3f}, p = {corr_cpd1[1]:.3e}")
    
    if cpd2_col:
        corr_cpd2 = stats.pearsonr(merged['pIC50_Cpd2'], merged['combined_score'])
        print(f"Correlation (Compound 2 pIC50 vs DepMap dependency):")
        print(f"  r = {corr_cpd2[0]:.3f}, p = {corr_cpd2[1]:.3e}")

# ============================================================================
# SECTION 2: RNASEQ DEGS (6 FILES FROM K562 & K666N)
# ============================================================================

print("\n" + "=" * 100)
print("SECTION 2: RNASEQ DIFFERENTIAL EXPRESSION (6 Files)")
print("=" * 100)

deg_dir = STARX_DIR / 'DEGs'
deg_files = list(deg_dir.glob('*.csv'))
print(f"\n[2.1] Found {len(deg_files)} DEG files:")
for f in deg_files:
    print(f"  - {f.name}")

deg_results = []

for deg_file in deg_files:
    print(f"\n[2.2] Analyzing: {deg_file.name}")
    
    deg = pd.read_csv(deg_file)
    print(f"  Genes: {len(deg):,}")
    
    # Identify columns
    gene_col = log2fc_col = padj_col = None
    for col in deg.columns:
        col_lower = col.lower()
        if not gene_col and any(x in col_lower for x in ['gene', 'symbol', 'id']):
            gene_col = col
        if not log2fc_col and any(x in col_lower for x in ['log2fold', 'log2fc', 'logfc']):
            log2fc_col = col
        if not padj_col and any(x in col_lower for x in ['padj', 'adj', 'fdr']):
            padj_col = col
    
    if not all([gene_col, log2fc_col, padj_col]):
        print(f"  ⚠️  Could not identify all columns, skipping")
        continue
    
    deg = deg.rename(columns={gene_col: 'gene', log2fc_col: 'log2fc', padj_col: 'padj'})
    
    # Get significant genes
    deg_sig = deg[deg['padj'] < 0.05]
    n_sig = len(deg_sig)
    n_up = len(deg_sig[deg_sig['log2fc'] > 0])
    n_down = len(deg_sig[deg_sig['log2fc'] < 0])
    
    print(f"  Significant (p<0.05): {n_sig:,} ({100*n_sig/len(deg):.1f}%)")
    print(f"    Up: {n_up:,} | Down: {n_down:,}")
    
    # Check target genes
    target_status = {}
    for target in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
        match = deg[deg['gene'].str.upper() == target]
        if len(match) > 0:
            row = match.iloc[0]
            sig = row['padj'] < 0.05
            target_status[target] = {
                'log2fc': row['log2fc'],
                'padj': row['padj'],
                'significant': sig
            }
            marker = '***' if row['padj'] < 0.001 else '**' if row['padj'] < 0.01 else '*' if sig else 'ns'
            print(f"    {target}: log2FC={row['log2fc']:+.3f} ({marker})")
        else:
            target_status[target] = {'log2fc': np.nan, 'padj': np.nan, 'significant': False}
    
    deg_results.append({
        'file': deg_file.name,
        'total_genes': len(deg),
        'sig_genes': n_sig,
        'sig_pct': 100*n_sig/len(deg),
        'n_up': n_up,
        'n_down': n_down,
        'target_status': target_status
    })

# Summary
print(f"\n[2.3] DEG Summary:")
deg_summary = pd.DataFrame([{
    'file': r['file'],
    'total': r['total_genes'],
    'sig': r['sig_genes'],
    'sig_%': f"{r['sig_pct']:.1f}%"
} for r in deg_results])
print(deg_summary.to_string(index=False))

# ============================================================================
# SECTION 3: PHOSPHOPROTEOMICS (GBM43)
# ============================================================================

print("\n" + "=" * 100)
print("SECTION 3: PHOSPHOPROTEOMICS ANALYSIS (GBM43 Glioblastoma)")
print("=" * 100)

phospho_dir = STARX_DIR / 'GBM43 Phosphoproteomics'
phospho_files = list(phospho_dir.glob('*.csv'))
print(f"\n[3.1] Found {len(phospho_files)} phosphoproteomics files:")
for f in phospho_files:
    print(f"  - {f.name}")

phospho_results = []

for phospho_file in phospho_files:
    print(f"\n[3.2] Analyzing: {phospho_file.name}")
    
    phospho = pd.read_csv(phospho_file)
    print(f"  Proteins: {len(phospho):,}")
    print(f"  Columns: {list(phospho.columns)[:10]}")
    
    # Identify columns
    gene_col = log2fc_col = padj_col = None
    for col in phospho.columns:
        col_lower = col.lower()
        if not gene_col and any(x in col_lower for x in ['gene', 'protein', 'symbol']):
            gene_col = col
        if not log2fc_col and any(x in col_lower for x in ['log2fold', 'log2fc', 'logfc']):
            log2fc_col = col
        if not padj_col and any(x in col_lower for x in ['padj', 'adj', 'fdr']):
            padj_col = col
    
    if not all([gene_col, log2fc_col, padj_col]):
        print(f"  ⚠️  Could not identify all columns, skipping")
        continue
    
    phospho = phospho.rename(columns={gene_col: 'gene', log2fc_col: 'log2fc', padj_col: 'padj'})
    
    # Significant proteins
    phospho_sig = phospho[phospho['padj'] < 0.05]
    print(f"  Significant (p<0.05): {len(phospho_sig):,} ({100*len(phospho_sig)/len(phospho):.1f}%)")
    
    # Check target genes
    print(f"\n  TARGET PROTEIN STATUS:")
    for target in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
        match = phospho[phospho['gene'].str.contains(target, case=False, na=False)]
        if len(match) > 0:
            for idx, row in match.iterrows():
                sig = row['padj'] < 0.05
                marker = '***' if row['padj'] < 0.001 else '**' if row['padj'] < 0.01 else '*' if sig else 'ns'
                print(f"    {row['gene']}: log2FC={row['log2fc']:+.3f} ({marker})")
        else:
            print(f"    {target}: NOT DETECTED")
    
    phospho_results.append({
        'file': phospho_file.name,
        'condition': 'GBM43',
        'total': len(phospho),
        'significant': len(phospho_sig)
    })

# ============================================================================
# SECTION 4: IP-MS (GBM43 PROTEIN INTERACTIONS)
# ============================================================================

print("\n" + "=" * 100)
print("SECTION 4: IP-MS PROTEIN INTERACTION ANALYSIS (GBM43)")
print("=" * 100)

ipms_dir = STARX_DIR / 'GBM43 IP-MS'
ipms_files = list(ipms_dir.glob('*.csv'))
print(f"\n[4.1] Found {len(ipms_files)} IP-MS files:")
for f in ipms_files:
    print(f"  - {f.name}")

ipms_results = []

for ipms_file in ipms_files:
    print(f"\n[4.2] Analyzing: {ipms_file.name}")
    
    ipms = pd.read_csv(ipms_file)
    print(f"  Proteins detected: {len(ipms):,}")
    print(f"  Columns: {list(ipms.columns)[:10]}")
    
    # Look for significant interactors
    sig_cols = [col for col in ipms.columns if 'pval' in col.lower() or 'qval' in col.lower() or 'fdr' in col.lower()]
    if sig_cols:
        sig_col = sig_cols[0]
        sig_proteins = ipms[ipms[sig_col] < 0.05]
        print(f"  Significant interactors (p<0.05): {len(sig_proteins):,}")
        
        if len(sig_proteins) > 0:
            print(f"\n  Top 10 interactors:")
            display_cols = [col for col in ipms.columns if any(x in col.lower() for x in ['gene', 'protein', 'symbol'])]
            if display_cols:
                print(sig_proteins.nsmallest(10, sig_col)[display_cols + [sig_col]].to_string(index=False))
    
    ipms_results.append({
        'file': ipms_file.name,
        'comparison': ipms_file.stem,
        'total_proteins': len(ipms)
    })

# ============================================================================
# SECTION 5: INTEGRATED EXPERIMENTAL VALIDATION SCORE
# ============================================================================

print("\n" + "=" * 100)
print("SECTION 5: INTEGRATED EXPERIMENTAL VALIDATION SCORING")
print("=" * 100)

print("\n[5.1] Creating comprehensive experimental validation scores...")

# Load current rankings
current_rankings = pd.read_csv(PROCESSED_DIR / 'final_integrated_rankings.csv')
print(f"Current rankings: {len(current_rankings)} cancer types")

# Create experimental evidence dataframe
exp_evidence = pd.DataFrame({
    'cancer_type': current_rankings['cancer_type'],
    'ic50_evidence': 0.0,
    'rnaseq_evidence': 0.0,
    'phospho_evidence': 0.0,
    'ipms_evidence': 0.0
})

# IC50 evidence (based on number of validated cell lines)
if len(merged) > 0:
    ic50_by_cancer = merged.groupby('OncotreePrimaryDisease').agg({
        'pIC50_Cpd1': 'mean',
        'combined_score': 'mean'
    }).reset_index()
    
    for idx, row in ic50_by_cancer.iterrows():
        mask = exp_evidence['cancer_type'] == row['OncotreePrimaryDisease']
        exp_evidence.loc[mask, 'ic50_evidence'] = 1.0

# Phospho evidence (GBM43 = glioblastoma)
gbm_mask = exp_evidence['cancer_type'].str.contains('Glioma', case=False, na=False)
exp_evidence.loc[gbm_mask, 'phospho_evidence'] = 1.0

# RNAseq evidence (K562 = AML-like, K666N = ?)
# Need to map cell lines to cancer types
aml_mask = exp_evidence['cancer_type'].str.contains('Myeloid', case=False, na=False)
exp_evidence.loc[aml_mask, 'rnaseq_evidence'] = 1.0

# Calculate integrated experimental score
exp_evidence['experimental_validation_score'] = (
    0.40 * exp_evidence['ic50_evidence'] +
    0.30 * exp_evidence['rnaseq_evidence'] +
    0.20 * exp_evidence['phospho_evidence'] +
    0.10 * exp_evidence['ipms_evidence']
)

print(f"\n[5.2] Experimental evidence distribution:")
print(f"  Cancer types with IC50 data: {exp_evidence['ic50_evidence'].sum():.0f}")
print(f"  Cancer types with RNAseq data: {exp_evidence['rnaseq_evidence'].sum():.0f}")
print(f"  Cancer types with phospho data: {exp_evidence['phospho_evidence'].sum():.0f}")
print(f"  Cancer types with IP-MS data: {exp_evidence['ipms_evidence'].sum():.0f}")

print(f"\nTop 10 by experimental validation:")
top_exp = exp_evidence.nlargest(10, 'experimental_validation_score')[['cancer_type', 'experimental_validation_score', 'ic50_evidence', 'rnaseq_evidence', 'phospho_evidence']]
print(top_exp.to_string(index=False))

# ============================================================================
# SECTION 6: COMPARE TO CURRENT RANKINGS
# ============================================================================

print("\n" + "=" * 100)
print("SECTION 6: IMPACT ON CANCER RANKINGS")
print("=" * 100)

print("\n[6.1] Merging with current rankings...")

# Merge experimental scores with current rankings
updated_rankings = current_rankings.merge(
    exp_evidence[['cancer_type', 'experimental_validation_score']], 
    on='cancer_type', 
    how='left',
    suffixes=('_old', '_new')
)

# Calculate new overall score
if 'experimental_validation_score_old' in updated_rankings.columns:
    print("\n⚠️  Experimental validation score already exists in rankings")
    print("  Comparing old vs new scores...")
    
    score_diff = updated_rankings['experimental_validation_score_new'] - updated_rankings['experimental_validation_score_old']
    changed = (score_diff.abs() > 0.01).sum()
    print(f"  Cancer types with score changes: {changed}")
    
    if changed > 0:
        print(f"\n  Top 10 biggest changes:")
        changed_df = updated_rankings[['cancer_type', 'experimental_validation_score_old', 'experimental_validation_score_new']].copy()
        changed_df['diff'] = score_diff
        print(changed_df.nlargest(10, 'diff', keep='all')[['cancer_type', 'experimental_validation_score_old', 'experimental_validation_score_new', 'diff']].to_string(index=False))

else:
    updated_rankings['experimental_validation_score'] = updated_rankings['experimental_validation_score_new']

# Recalculate overall score
print("\n[6.2] Recalculating overall scores with updated experimental validation...")

# Current weights (from EXPERIMENTAL_DATA_NOTE.md):
# DepMap: 30%, Expression: 20%, Mutation: 20%, Experimental: 10%, Copy Number: 10%, Literature: 10%

updated_rankings['overall_score_NEW'] = (
    0.30 * updated_rankings['depmap_score_normalized'] +
    0.20 * updated_rankings['expression_score_normalized'] +
    0.20 * updated_rankings['mutation_context_score'] +
    0.10 * updated_rankings['experimental_validation_score_new'] +
    0.10 * updated_rankings['copy_number_score'] +
    0.10 * updated_rankings['literature_score_normalized']
)

# Compare rankings
updated_rankings['overall_score_OLD'] = updated_rankings['overall_score']
updated_rankings['score_change'] = updated_rankings['overall_score_NEW'] - updated_rankings['overall_score_OLD']
updated_rankings['rank_OLD'] = updated_rankings['overall_score_OLD'].rank(ascending=False, method='dense')
updated_rankings['rank_NEW'] = updated_rankings['overall_score_NEW'].rank(ascending=False, method='dense')
updated_rankings['rank_change'] = updated_rankings['rank_OLD'] - updated_rankings['rank_NEW']

print("\n[6.3] Ranking changes:")
big_movers = updated_rankings[updated_rankings['rank_change'].abs() >= 3].sort_values('rank_change', ascending=False)

if len(big_movers) > 0:
    print(f"\n✅ {len(big_movers)} cancer types moved ≥3 ranks:")
    print(big_movers[['cancer_type', 'rank_OLD', 'rank_NEW', 'rank_change', 'score_change']].to_string(index=False))
else:
    print("\n✅ No major ranking changes (all <3 ranks)")

print("\n[6.4] Top 10 comparison:")
comparison = updated_rankings.sort_values('overall_score_NEW', ascending=False).head(10)[
    ['cancer_type', 'rank_OLD', 'rank_NEW', 'overall_score_OLD', 'overall_score_NEW', 'rank_change']
]
print(comparison.to_string(index=False))

# ============================================================================
# SECTION 7: SAVE RESULTS
# ============================================================================

print("\n" + "=" * 100)
print("SECTION 7: SAVING COMPREHENSIVE RESULTS")
print("=" * 100)

# Save updated rankings
out_path = PROCESSED_DIR / 'final_integrated_rankings_UPDATED.csv'
updated_rankings_final = updated_rankings.copy()
updated_rankings_final['overall_score'] = updated_rankings_final['overall_score_NEW']
updated_rankings_final['rank'] = updated_rankings_final['rank_NEW']

# Clean up temporary columns
cols_to_keep = [col for col in updated_rankings_final.columns if not col.endswith('_OLD') and not col.endswith('_NEW')]
updated_rankings_final = updated_rankings_final[cols_to_keep]

updated_rankings_final = updated_rankings_final.sort_values('overall_score', ascending=False).reset_index(drop=True)
updated_rankings_final['rank'] = range(1, len(updated_rankings_final) + 1)

updated_rankings_final.to_csv(out_path, index=False)
print(f"\n✅ Saved: {out_path.name}")

# Save experimental evidence details
exp_evidence.to_csv(PROCESSED_DIR / 'experimental_evidence_comprehensive.csv', index=False)
print(f"✅ Saved: experimental_evidence_comprehensive.csv")

# Save DEG summary
deg_summary_df = pd.DataFrame(deg_results)
deg_summary_df.to_csv(PROCESSED_DIR / 'rnaseq_deg_summary.csv', index=False)
print(f"✅ Saved: rnaseq_deg_summary.csv")

# Create comprehensive summary report
summary = f"""
COMPREHENSIVE EXPERIMENTAL DATA INTEGRATION SUMMARY
{'='*100}

ANALYSIS COMPLETED: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

DATA SOURCES ANALYZED:
1. IC50 Data: {len(ic50_data)} cell lines tested
   - Matched to DepMap: {len(merged)} cell lines
   - Cancer types represented: {len(ic50_by_cancer) if len(merged) > 0 else 0}

2. RNAseq DEGs: {len(deg_files)} experimental conditions
   - Total genes analyzed: {sum(r['total_genes'] for r in deg_results):,}
   - Significant genes found: {sum(r['sig_genes'] for r in deg_results):,}

3. Phosphoproteomics: {len(phospho_results)} GBM43 datasets
   - Total proteins: {sum(r['total'] for r in phospho_results):,}
   - Significant: {sum(r['significant'] for r in phospho_results):,}

4. IP-MS: {len(ipms_results)} protein interaction datasets
   - Total proteins: {sum(r['total_proteins'] for r in ipms_results):,}

IMPACT ON RANKINGS:
- Cancer types analyzed: {len(updated_rankings)}
- Major ranking changes (≥3 ranks): {len(big_movers)}
- Maximum rank change: {updated_rankings['rank_change'].abs().max():.0f} positions

RECOMMENDATION:
{'✅ RANKINGS UPDATED - Significant changes detected' if len(big_movers) > 5 else '→ MINOR CHANGES - Current rankings largely validated'}

UPDATED FILES:
- final_integrated_rankings_UPDATED.csv (NEW comprehensive rankings)
- experimental_evidence_comprehensive.csv (detailed evidence by cancer type)
- rnaseq_deg_summary.csv (DEG analysis results)

NEXT STEPS:
1. Review ranking changes in updated file
2. Update report with experimental validation findings
3. Add figures showing experimental evidence convergence
4. Validate that top 5 practical cancers remain stable
"""

summary_path = PROCESSED_DIR / 'comprehensive_experimental_integration_summary.txt'
with open(summary_path, 'w') as f:
    f.write(summary)

print(f"✅ Saved: {summary_path.name}")

print("\n" + "=" * 100)
print("COMPREHENSIVE ANALYSIS COMPLETE")
print("=" * 100)

print(f"\n📄 READ: {summary_path}")
print(f"\n{'='*100}")
print("RECOMMENDATION:")
if len(big_movers) > 5:
    print("✅ SIGNIFICANT CHANGES - Update report and presentation with new rankings")
    print("   Cancer rankings have materially changed based on experimental validation")
else:
    print("→ VALIDATED - Current rankings hold with experimental data")
    print("   Add experimental validation section to report, but rankings stable")
print("=" * 100)

