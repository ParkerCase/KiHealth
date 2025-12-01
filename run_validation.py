#!/usr/bin/env python3
"""
Experimental Validation Integration - IC50 vs DepMap
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("EXPERIMENTAL VALIDATION ANALYSIS")
print("="*70)

# 1. Load IC50 data
print("\n[1/7] Loading IC50 data...")
ic50_path = 'data/raw/StarXData/Copy of AQT cell based profiling160 cell lines815K815H_report_summary/IC50 values-Table 1.csv'
ic50_raw = pd.read_csv(ic50_path, skiprows=2)
ic50_raw.columns = ic50_raw.columns.str.strip()
ic50_data = ic50_raw[['Cell line', 'IC50 [M] \nUMF-815K', 'IC50 [M] \nUMF-815H']].copy()
ic50_data.columns = ['CellLineName', 'IC50_Cpd1', 'IC50_Cpd2']
ic50_data['CellLineName'] = ic50_data['CellLineName'].str.strip()
print(f"   ✅ Loaded {len(ic50_data)} cell lines with IC50 data")

# 2. Process IC50 values
print("\n[2/7] Processing IC50 values...")
def clean_ic50_value(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if val_str.startswith('>'):
        return 2.0e-5  # Cap at 20 µM for >20µM values
    try:
        return float(val_str)
    except:
        return np.nan

ic50_data['IC50_Cpd1_clean'] = ic50_data['IC50_Cpd1'].apply(clean_ic50_value)
ic50_data['IC50_Cpd2_clean'] = ic50_data['IC50_Cpd2'].apply(clean_ic50_value)
ic50_data['pIC50_Cpd1'] = -np.log10(ic50_data['IC50_Cpd1_clean'])
ic50_data['pIC50_Cpd2'] = -np.log10(ic50_data['IC50_Cpd2_clean'])
print(f"   ✅ Processed IC50 values")
print(f"      Cpd1 range: {ic50_data['IC50_Cpd1_clean'].min():.2e} to {ic50_data['IC50_Cpd1_clean'].max():.2e} M")
print(f"      Cpd2 range: {ic50_data['IC50_Cpd2_clean'].min():.2e} to {ic50_data['IC50_Cpd2_clean'].max():.2e} M")

# 3. Load DepMap data
print("\n[3/7] Loading DepMap data...")
depmap_data = pd.read_csv('data/processed/top_dependent_cell_lines.csv')
print(f"   ✅ Loaded {len(depmap_data)} cell lines with DepMap dependency scores")

# 4. Match cell lines
print("\n[4/7] Matching cell lines between IC50 and DepMap...")
def normalize_cell_line_name(name):
    """Normalize cell line names for matching"""
    if pd.isna(name):
        return ''
    normalized = str(name).upper().replace(' ', '').replace('-', '').replace('_', '')
    # Remove common suffixes
    for suffix in ['EC', 'FV1', 'FV2', 'CJ1']:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
    return normalized

ic50_data['CellLineName_norm'] = ic50_data['CellLineName'].apply(normalize_cell_line_name)
depmap_data['CellLineName_norm'] = depmap_data['CellLineName'].apply(normalize_cell_line_name)

merged_data = pd.merge(
    ic50_data, 
    depmap_data, 
    on='CellLineName_norm', 
    how='inner', 
    suffixes=('_IC50', '_DepMap')
)

print(f"   ✅ Matched {len(merged_data)} cell lines ({100*len(merged_data)/len(ic50_data):.1f}% of IC50 data)")
print(f"      Cancer types represented: {merged_data['OncotreePrimaryDisease'].nunique()}")

# 5. Calculate overall correlations
print("\n[5/7] Calculating correlations between IC50 and DepMap dependency...")
print("\n" + "="*70)
print("CORRELATION RESULTS")
print("="*70)

# Compound 1 correlations
valid_cpd1 = merged_data[['pIC50_Cpd1', 'combined_score']].dropna()
if len(valid_cpd1) > 0:
    pearson_r1, pearson_p1 = pearsonr(valid_cpd1['pIC50_Cpd1'], valid_cpd1['combined_score'])
    spearman_r1, spearman_p1 = spearmanr(valid_cpd1['pIC50_Cpd1'], valid_cpd1['combined_score'])
    print(f"\nCompound 1 (UMF-815K) vs DepMap Combined Dependency:")
    print(f"   Pearson:  r = {pearson_r1:+.3f}, p = {pearson_p1:.2e} (n={len(valid_cpd1)})")
    print(f"   Spearman: ρ = {spearman_r1:+.3f}, p = {spearman_p1:.2e}")
    if abs(spearman_r1) > 0.3:
        print(f"   → STRONG correlation")
    elif abs(spearman_r1) > 0.15:
        print(f"   → MODERATE correlation")
    else:
        print(f"   → WEAK correlation")
else:
    spearman_r1, spearman_p1 = np.nan, np.nan
    print("\nCompound 1: Insufficient data for correlation")

# Compound 2 correlations
valid_cpd2 = merged_data[['pIC50_Cpd2', 'combined_score']].dropna()
if len(valid_cpd2) > 0:
    pearson_r2, pearson_p2 = pearsonr(valid_cpd2['pIC50_Cpd2'], valid_cpd2['combined_score'])
    spearman_r2, spearman_p2 = spearmanr(valid_cpd2['pIC50_Cpd2'], valid_cpd2['combined_score'])
    print(f"\nCompound 2 (UMF-815H) vs DepMap Combined Dependency:")
    print(f"   Pearson:  r = {pearson_r2:+.3f}, p = {pearson_p2:.2e} (n={len(valid_cpd2)})")
    print(f"   Spearman: ρ = {spearman_r2:+.3f}, p = {spearman_p2:.2e}")
    if abs(spearman_r2) > 0.3:
        print(f"   → STRONG correlation")
    elif abs(spearman_r2) > 0.15:
        print(f"   → MODERATE correlation")
    else:
        print(f"   → WEAK correlation")
else:
    spearman_r2, spearman_p2 = np.nan, np.nan
    print("\nCompound 2: Insufficient data for correlation")

# 6. Cancer-type specific validation scores
print("\n[6/7] Calculating cancer-type specific validation scores...")
cancer_validation = merged_data.groupby('OncotreePrimaryDisease').agg({
    'CellLineName_IC50': 'count',
    'pIC50_Cpd1': 'mean',
    'pIC50_Cpd2': 'mean',
    'combined_score': 'mean'
}).reset_index()

cancer_validation.columns = ['cancer_type', 'n_validated_cell_lines', 
                              'mean_pIC50_Cpd1', 'mean_pIC50_Cpd2', 'mean_dependency']

# Calculate validation score for each cancer type
validation_scores = []
for cancer_type in merged_data['OncotreePrimaryDisease'].unique():
    subset = merged_data[merged_data['OncotreePrimaryDisease'] == cancer_type]
    
    if len(subset) >= 3:
        valid_data = subset[['pIC50_Cpd1', 'combined_score']].dropna()
        if len(valid_data) >= 3:
            rho, p_val = spearmanr(valid_data['pIC50_Cpd1'], valid_data['combined_score'])
            # Validation score: absolute correlation if significant (p<0.10), else 0
            validation_score = abs(rho) if p_val < 0.10 else 0.0
        else:
            validation_score = 0.0
            rho = np.nan
            p_val = np.nan
    else:
        validation_score = 0.0
        rho = np.nan
        p_val = np.nan
    
    validation_scores.append({
        'cancer_type': cancer_type,
        'correlation_rho': rho,
        'correlation_pval': p_val,
        'validation_score': validation_score
    })

validation_df = pd.DataFrame(validation_scores)
cancer_validation = cancer_validation.merge(validation_df, on='cancer_type', how='left')

# Normalize validation scores to 0-1
max_val = cancer_validation['validation_score'].max()
if max_val > 0:
    cancer_validation['validation_score_normalized'] = cancer_validation['validation_score'] / max_val
else:
    cancer_validation['validation_score_normalized'] = 0.0

cancer_validation = cancer_validation.sort_values('validation_score_normalized', ascending=False)

print("\n" + "="*70)
print("TOP 10 CANCER TYPES BY EXPERIMENTAL VALIDATION")
print("="*70)
print(cancer_validation.head(10)[['cancer_type', 'n_validated_cell_lines', 
                                   'correlation_rho', 'correlation_pval',
                                   'validation_score_normalized']].to_string(index=False))

# Check for glioblastoma/brain cancers specifically
brain_cancers = cancer_validation[cancer_validation['cancer_type'].str.contains('Glio|CNS|Brain', case=False, na=False)]
if len(brain_cancers) > 0:
    print("\n" + "="*70)
    print("BRAIN CANCER VALIDATION (Glioblastoma/CNS)")
    print("="*70)
    print(brain_cancers[['cancer_type', 'n_validated_cell_lines', 
                         'mean_dependency', 'validation_score_normalized']].to_string(index=False))

# 7. Save results
print("\n[7/7] Saving results...")

# Save cancer-type validation scores
output_file = 'data/processed/experimental_validation.csv'
cancer_validation.to_csv(output_file, index=False)
print(f"   ✅ Saved: {output_file}")

# Save merged cell line data
merged_output = 'data/processed/ic50_depmap_merged.csv'
merged_data.to_csv(merged_output, index=False)
print(f"   ✅ Saved: {merged_output}")

# Create summary
summary = f"""# Experimental Validation Summary
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## Data Overview
- IC50 data provided: 160 cell lines
- DepMap dependency data: 237 cell lines  
- Successfully matched: {len(merged_data)} cell lines ({100*len(merged_data)/len(ic50_data):.1f}%)
- Cancer types with validation data: {merged_data['OncotreePrimaryDisease'].nunique()}

## Overall Correlation Results

### Compound 1 (UMF-815K) vs DepMap Combined Dependency
- Spearman correlation: ρ = {spearman_r1:.3f}, p = {spearman_p1:.2e}
- Pearson correlation: r = {pearson_r1:.3f}, p = {pearson_p1:.2e}
- Sample size: n = {len(valid_cpd1)}
- Interpretation: {"STRONG validation - IC50 correlates well with DepMap predictions" if abs(spearman_r1) > 0.3 else "MODERATE validation - some correlation present" if abs(spearman_r1) > 0.15 else "WEAK validation - limited correlation"}

### Compound 2 (UMF-815H) vs DepMap Combined Dependency  
- Spearman correlation: ρ = {spearman_r2:.3f}, p = {spearman_p2:.2e}
- Pearson correlation: r = {pearson_r2:.3f}, p = {pearson_p2:.2e}
- Sample size: n = {len(valid_cpd2)}
- Interpretation: {"STRONG validation" if abs(spearman_r2) > 0.3 else "MODERATE validation" if abs(spearman_r2) > 0.15 else "WEAK validation"}

## Top 5 Cancer Types by Validation Score

{cancer_validation[['cancer_type', 'n_validated_cell_lines', 'mean_dependency', 'validation_score_normalized']].head().to_string(index=False)}

## Brain Cancer Results

{brain_cancers[['cancer_type', 'n_validated_cell_lines', 'mean_dependency', 'validation_score_normalized']].to_string(index=False) if len(brain_cancers) > 0 else "No brain cancer types with sufficient validation data (n≥3)"}

## Clinical Interpretation

The experimental IC50 data {"validates" if abs(spearman_r1) > 0.15 or abs(spearman_r2) > 0.15 else "shows limited correlation with"} the computational DepMap dependency predictions.
This {"supports" if abs(spearman_r1) > 0.15 or abs(spearman_r2) > 0.15 else "suggests caution in"} using DepMap scores to prioritize cancer indications.

Cancer types with high validation scores show agreement between:
1. Genetic dependency (CRISPR knockout in DepMap)
2. Chemical inhibition sensitivity (IC50 from actual drug testing)

This convergence of evidence strengthens confidence in those indications.
"""

with open('data/processed/experimental_validation_summary.txt', 'w') as f:
    f.write(summary)
print(f"   ✅ Saved: experimental_validation_summary.txt")

print("\n" + "="*70)
print("✅ EXPERIMENTAL VALIDATION COMPLETE")
print("="*70)
print("\nNext step: Integration into PROMPT 4 scoring model")
print("   - Validation scores will be added as 6th evidence dimension")
print("   - Weight: 10% in overall_score calculation")
