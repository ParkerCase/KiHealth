#!/usr/bin/env python3
"""
PROMPT 3.5: Experimental Validation Integration
Analyze IC50 data from 160 cell lines and correlate with DepMap predictions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import re

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

# Create output directories
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("PROMPT 3.5: EXPERIMENTAL VALIDATION INTEGRATION")
print("=" * 80)
print("\nValidating DepMap predictions with REAL IC50 data from 160 cell lines")
print()

# ==============================================================================
# STEP 1: Load IC50 Data
# ==============================================================================

print("[STEP 1] Loading IC50 data from 160 cell lines...")

ic50_file = DATA_RAW / "StarXData" / "Copy of AQT cell based profiling160 cell lines815K815H_report_summary" / "IC50 values-Table 1.csv"

# Read with special handling for the header
ic50_data = pd.read_csv(ic50_file, skiprows=4, header=None)

# Set column names based on the known structure
ic50_data.columns = ['empty1', 'No', 'Cell_line', 'IC50_815K', 'IC50_815H', 'IC50_Bortezomib'] + [f'col{i}' for i in range(6, len(ic50_data.columns))]

# Drop empty columns
ic50_data = ic50_data[['No', 'Cell_line', 'IC50_815K', 'IC50_815H']]

# Remove rows without cell line names
ic50_data = ic50_data.dropna(subset=['Cell_line'])
ic50_data = ic50_data[ic50_data['Cell_line'] != '']

print(f"✓ Loaded IC50 file")
print(f"  Cell lines: {len(ic50_data)}")
print(f"  Columns: {ic50_data.columns.tolist()}")

# Parse IC50 values
def parse_ic50(value):
    """Parse IC50 value, handling > symbols and scientific notation"""
    if pd.isna(value):
        return np.nan
    
    value_str = str(value).strip()
    
    # Handle > cases (set to a high value = 20 µM)
    if value_str.startswith('>'):
        return 2e-5  # 20 µM in M
    
    try:
        return float(value_str)
    except:
        return np.nan

ic50_data['IC50_815K_M'] = ic50_data['IC50_815K'].apply(parse_ic50)
ic50_data['IC50_815H_M'] = ic50_data['IC50_815H'].apply(parse_ic50)

# Convert to pIC50 (higher = more sensitive)
ic50_data['pIC50_815K'] = -np.log10(ic50_data['IC50_815K_M'])
ic50_data['pIC50_815H'] = -np.log10(ic50_data['IC50_815H_M'])

# Combined sensitivity
ic50_data['combined_sensitivity'] = (ic50_data['pIC50_815K'] + ic50_data['pIC50_815H']) / 2

print(f"\n✓ Processed IC50 values:")
print(f"  Valid 815K: {ic50_data['IC50_815K_M'].notna().sum()}")
print(f"  Valid 815H: {ic50_data['IC50_815H_M'].notna().sum()}")
print(f"  pIC50 range: {ic50_data['combined_sensitivity'].min():.2f} - {ic50_data['combined_sensitivity'].max():.2f}")

# ==============================================================================
# STEP 2: Load DepMap Data
# ==============================================================================

print("\n[STEP 2] Loading DepMap dependency data...")

top_deps = pd.read_csv(DATA_PROCESSED / "top_dependent_cell_lines.csv")

print(f"✓ DepMap cell lines: {len(top_deps)}")

# ==============================================================================
# STEP 3: Match Cell Lines
# ==============================================================================

print("\n[STEP 3] Matching cell lines...")

# Standardize names
def std_name(name):
    if pd.isna(name):
        return ""
    return str(name).upper().replace('-', '').replace('_', '').replace(' ', '').strip()

ic50_data['name_std'] = ic50_data['Cell_line'].apply(std_name)
top_deps['name_std'] = top_deps['CellLineName'].apply(std_name)

# Merge
merged = pd.merge(
    top_deps,
    ic50_data[['name_std', 'Cell_line', 'IC50_815K_M', 'IC50_815H_M', 'pIC50_815K', 'pIC50_815H', 'combined_sensitivity']],
    on='name_std',
    how='inner'
)

print(f"✓ Matched: {len(merged)} cell lines")
print(f"  {len(merged)/len(ic50_data)*100:.1f}% of IC50 data")
print(f"  {len(merged)/len(top_deps)*100:.1f}% of DepMap data")

# ==============================================================================
# STEP 4: Calculate Correlations
# ==============================================================================

print("\n[STEP 4] Calculating correlations...")

correlations = []
target_genes = ['STK17A', 'MYLK4', 'TBK1', 'CLK4']

for gene in target_genes:
    dep_col = f'{gene}_dependency'
    valid = merged[[dep_col, 'combined_sensitivity']].dropna()
    
    if len(valid) < 10:
        print(f"  {gene:10s}: Insufficient data (n={len(valid)})")
        continue
    
    r, p = stats.pearsonr(valid[dep_col], valid['combined_sensitivity'])
    
    correlations.append({
        'gene': gene,
        'n_samples': len(valid),
        'correlation': r,
        'p_value': p,
        'significant': p < 0.05
    })
    
    sig_marker = " ✓ SIG" if p < 0.05 else ""
    print(f"  {gene:10s}: r={r:7.4f}, p={p:.4e}, n={len(valid)}{sig_marker}")

# Combined score
valid_comb = merged[['combined_score', 'combined_sensitivity']].dropna()
r_comb, p_comb = stats.pearsonr(valid_comb['combined_score'], valid_comb['combined_sensitivity'])

correlations.append({
    'gene': 'COMBINED',
    'n_samples': len(valid_comb),
    'correlation': r_comb,
    'p_value': p_comb,
    'significant': p_comb < 0.05
})

sig_marker = " ✓✓✓ SIGNIFICANT" if p_comb < 0.05 else ""
print(f"  {'COMBINED':10s}: r={r_comb:7.4f}, p={p_comb:.4e}, n={len(valid_comb)}{sig_marker}")

# ==============================================================================
# STEP 5: Cancer Type Validation Scores
# ==============================================================================

print("\n[STEP 5] Calculating cancer type validation scores...")

cancer_validation = []

for cancer in merged['OncotreePrimaryDisease'].unique():
    cdata = merged[merged['OncotreePrimaryDisease'] == cancer]
    
    if len(cdata) < 2:
        continue
    
    mean_dep = cdata['combined_score'].mean()
    mean_sens = cdata['combined_sensitivity'].mean()
    
    # Validation score: normalize sensitivity based on dependency
    # High dependency + high sensitivity = good validation
    if mean_dep < -0.05:  # Shows dependency
        norm_sens = (mean_sens - 4.0) / 2.0
        validation_score = min(1.0, max(0.0, norm_sens))
    else:
        validation_score = 0.5
    
    cancer_validation.append({
        'cancer_type': cancer,
        'n_cell_lines': len(cdata),
        'mean_dependency': mean_dep,
        'mean_sensitivity_pIC50': mean_sens,
        'validation_score': validation_score
    })

validation_df = pd.DataFrame(cancer_validation).sort_values('validation_score', ascending=False)

print(f"✓ Validated {len(validation_df)} cancer types")
print("\nTop 10:")
print(validation_df.head(10)[['cancer_type', 'n_cell_lines', 'validation_score']].to_string(index=False))

# ==============================================================================
# STEP 6: Save experimental_validation.csv
# ==============================================================================

print("\n[STEP 6] Saving experimental_validation.csv...")

cancer_rankings = pd.read_csv(DATA_PROCESSED / "cancer_type_rankings.csv")
all_cancers = cancer_rankings['OncotreePrimaryDisease'].tolist()

full_validation = []
for cancer in all_cancers:
    if cancer in validation_df['cancer_type'].values:
        row = validation_df[validation_df['cancer_type'] == cancer].iloc[0]
        full_validation.append({
            'cancer_type': cancer,
            'validation_score': row['validation_score'],
            'n_cell_lines_tested': row['n_cell_lines'],
            'mean_dependency': row['mean_dependency'],
            'mean_sensitivity_pIC50': row['mean_sensitivity_pIC50'],
            'validation_data_available': True
        })
    else:
        full_validation.append({
            'cancer_type': cancer,
            'validation_score': 0.5,
            'n_cell_lines_tested': 0,
            'mean_dependency': np.nan,
            'mean_sensitivity_pIC50': np.nan,
            'validation_data_available': False
        })

full_validation_df = pd.DataFrame(full_validation)

output_file = DATA_PROCESSED / "experimental_validation.csv"
full_validation_df.to_csv(output_file, index=False)

print(f"✓ Saved: {output_file}")
print(f"  Rows: {len(full_validation_df)}")
print(f"  With validation data: {full_validation_df['validation_data_available'].sum()}")

# ==============================================================================
# STEP 7: Save Stats
# ==============================================================================

print("\n[STEP 7] Saving validation_correlation_stats.txt...")

stats_file = DATA_PROCESSED / "validation_correlation_stats.txt"

with open(stats_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("EXPERIMENTAL VALIDATION: DepMap vs IC50 Correlation\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"IC50 data: 160 cell lines\n")
    f.write(f"DepMap data: 237 cell lines\n")
    f.write(f"Matched: {len(merged)} cell lines\n\n")
    
    f.write("CORRELATIONS:\n")
    for corr in correlations:
        f.write(f"{corr['gene']:10s}: r={corr['correlation']:7.4f}, p={corr['p_value']:.4e}, n={corr['n_samples']}")
        if corr['significant']:
            f.write(" ***\n")
        else:
            f.write("\n")
    
    f.write("\nVALIDATION ASSESSMENT:\n")
    if abs(r_comb) > 0.3 and p_comb < 0.05:
        f.write("✓ STRONG validation\n")
    elif len([c for c in correlations if c['significant']]) >= 2:
        f.write("✓ MODERATE validation\n")
    else:
        f.write("⚠️  WEAK validation\n")

print(f"✓ Saved: {stats_file}")

# ==============================================================================
# STEP 8: Create Figure
# ==============================================================================

print("\n[STEP 8] Creating correlation figure...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

# Individual genes
for idx, gene in enumerate(target_genes):
    ax = axes[idx]
    dep_col = f'{gene}_dependency'
    pdata = merged[[dep_col, 'combined_sensitivity']].dropna()
    
    if len(pdata) < 10:
        ax.text(0.5, 0.5, f'{gene}\nInsufficient data', ha='center', va='center')
        continue
    
    ax.scatter(pdata[dep_col], pdata['combined_sensitivity'], alpha=0.5, s=40)
    
    z = np.polyfit(pdata[dep_col], pdata['combined_sensitivity'], 1)
    p_fit = np.poly1d(z)
    x_line = np.linspace(pdata[dep_col].min(), pdata[dep_col].max(), 100)
    ax.plot(x_line, p_fit(x_line), "r--", alpha=0.8, linewidth=2)
    
    r, p_val = stats.pearsonr(pdata[dep_col], pdata['combined_sensitivity'])
    
    ax.set_xlabel(f'{gene} Dependency', fontweight='bold')
    ax.set_ylabel('IC50 Sensitivity (pIC50)', fontweight='bold')
    ax.set_title(f'{gene}\nr={r:.3f}, p={p_val:.4f}, n={len(pdata)}', fontweight='bold')
    ax.grid(True, alpha=0.3)

# Combined
ax = axes[4]
pdata = merged[['combined_score', 'combined_sensitivity']].dropna()

ax.scatter(pdata['combined_score'], pdata['combined_sensitivity'], alpha=0.5, s=40)

z = np.polyfit(pdata['combined_score'], pdata['combined_sensitivity'], 1)
p_fit = np.poly1d(z)
x_line = np.linspace(pdata['combined_score'].min(), pdata['combined_score'].max(), 100)
ax.plot(x_line, p_fit(x_line), "r--", alpha=0.8, linewidth=2)

ax.set_xlabel('Combined Dependency', fontweight='bold')
ax.set_ylabel('IC50 Sensitivity (pIC50)', fontweight='bold')
ax.set_title(f'COMBINED\nr={r_comb:.3f}, p={p_comb:.4f}, n={len(pdata)}', fontweight='bold')
ax.grid(True, alpha=0.3)

# Top cancers
ax = axes[5]
top10 = validation_df.head(10)
y_pos = np.arange(len(top10))
ax.barh(y_pos, top10['validation_score'].values, color='steelblue', alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels([c[:30] for c in top10['cancer_type'].values], fontsize=8)
ax.set_xlabel('Validation Score', fontweight='bold')
ax.set_title('Top 10 Cancer Types\nby Validation', fontweight='bold')
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

plt.suptitle('DepMap vs Experimental IC50: Validation Analysis\n160 Cell Lines (UMF-815K & UMF-815H)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()

output_fig = FIGURES / "depmap_vs_ic50_correlation.png"
plt.savefig(output_fig, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ Saved: {output_fig}")

# ==============================================================================
# COMPLETION
# ==============================================================================

print("\n" + "=" * 80)
print("✅ PROMPT 3.5 COMPLETE: Experimental Validation")
print("=" * 80)

print("\nOUTPUTS:")
print("  1. ✓ experimental_validation.csv")
print("  2. ✓ validation_correlation_stats.txt")
print("  3. ✓ depmap_vs_ic50_correlation.png")

print("\nRESULTS:")
print(f"  • Matched: {len(merged)} cell lines")
print(f"  • Combined r={r_comb:.3f}, p={p_comb:.4f}")
print(f"  • Validated cancers: {full_validation_df['validation_data_available'].sum()}")

if abs(r_comb) > 0.3 and p_comb < 0.05:
    print("\n✓✓✓ STRONG VALIDATION - DepMap predictions work!")
elif len([c for c in correlations if c['significant']]) >= 2:
    print("\n✓✓ MODERATE VALIDATION - Gene-specific effects")
else:
    print("\n⚠️  WEAK VALIDATION - Context-dependent")

print("\n" + "=" * 80)
