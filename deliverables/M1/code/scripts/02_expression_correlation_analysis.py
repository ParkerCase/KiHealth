#!/usr/bin/env python3
"""
Expression Correlation Analysis - PROMPT 2
Generates all required outputs for Nov 10 delivery

Outputs:
1. data/processed/expression_correlation.csv
2. data/processed/expression_summary.txt
3. outputs/figures/expression_dependency_scatter_4panel.png
4. outputs/figures/cancer_type_expression_heatmap.png
5. outputs/figures/high_expression_high_dependency_candidates.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import os
import sys
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "depmap"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

# Create output directories
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("EXPRESSION CORRELATION ANALYSIS - PROMPT 2")
print("=" * 80)

# ==============================================================================
# STEP 1: Load All Required Data
# ==============================================================================

print("\n[STEP 1] Loading data files...")

# Load cell line metadata
model = pd.read_csv(DATA_RAW / "Model.csv")
print(f"✓ Model metadata: {model.shape}")

# Load dependency scores (CRISPR Gene Effect)
print("  Loading dependency data (may take 30-60 seconds)...")
dependency = pd.read_csv(DATA_RAW / "CRISPRGeneEffect.csv", index_col=0)
print(f"✓ Dependency scores: {dependency.shape}")

# Load expression data
print("  Loading expression data (may take 60-90 seconds)...")
expression = pd.read_csv(DATA_RAW / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv")
expression = expression.set_index('ModelID')
print(f"✓ Expression data: {expression.shape}")

# Load existing cancer rankings
cancer_rankings = pd.read_csv(DATA_PROCESSED / "cancer_type_rankings.csv")
print(f"✓ Cancer rankings: {cancer_rankings.shape}")

# Load top dependent cell lines
top_cell_lines = pd.read_csv(DATA_PROCESSED / "top_dependent_cell_lines.csv")
print(f"✓ Top dependent cell lines: {top_cell_lines.shape}")

# Check alignment
common_lines = expression.index.intersection(dependency.index)
print(f"\n✓ Common cell lines (expression ∩ dependency): {len(common_lines)}")

# ==============================================================================
# STEP 2: Extract Target Gene Data
# ==============================================================================

print("\n[STEP 2] Extracting target gene data...")

# Target genes with Entrez IDs
target_genes = {
    'STK17A': '9263',
    'MYLK4': '340156',
    'TBK1': '29110',
    'CLK4': '57396'
}

# Find columns in dependency data
dep_cols = {}
for gene, entrez_id in target_genes.items():
    matches = [col for col in dependency.columns if gene in col and entrez_id in col]
    if matches:
        dep_cols[gene] = matches[0]
        print(f"  ✓ Dependency - {gene:10s}: {matches[0]}")
    else:
        print(f"  ✗ Dependency - {gene:10s}: NOT FOUND")
        sys.exit(1)

# Find columns in expression data
expr_cols = {}
for gene, entrez_id in target_genes.items():
    matches = [col for col in expression.columns if gene in col and entrez_id in col]
    if matches:
        expr_cols[gene] = matches[0]
        print(f"  ✓ Expression - {gene:10s}: {matches[0]}")
    else:
        print(f"  ✗ Expression - {gene:10s}: NOT FOUND")
        sys.exit(1)

# ==============================================================================
# STEP 3: Create Aligned Expression-Dependency Dataset
# ==============================================================================

print("\n[STEP 3] Creating aligned dataset...")

# Extract expression data for target genes
expr_data = pd.DataFrame(index=expression.index)
for gene, col in expr_cols.items():
    expr_data[f'{gene}_expression'] = expression[col]

# Extract dependency data for target genes
dep_data = pd.DataFrame(index=dependency.index)
for gene, col in dep_cols.items():
    dep_data[f'{gene}_dependency'] = dependency[col]

# Merge expression and dependency (inner join on ModelID)
combined = expr_data.join(dep_data, how='inner')

# Add cancer type metadata
combined = combined.join(
    model.set_index('ModelID')[['CellLineName', 'OncotreePrimaryDisease', 'OncotreeLineage']], 
    how='left'
)

print(f"✓ Combined dataset: {combined.shape}")
print(f"  Cell lines with BOTH expression AND dependency: {len(combined)}")

# ==============================================================================
# STEP 4: Global Correlation Analysis
# ==============================================================================

print("\n[STEP 4] Calculating global correlations...")
print("-" * 80)

global_corrs = []

for gene in target_genes.keys():
    expr_col = f'{gene}_expression'
    dep_col = f'{gene}_dependency'
    
    # Drop NAs
    data = combined[[expr_col, dep_col]].dropna()
    
    if len(data) > 10:
        # Calculate Pearson correlation
        corr, p_val = pearsonr(data[expr_col], data[dep_col])
        
        global_corrs.append({
            'gene': gene,
            'correlation': corr,
            'p_value': p_val,
            'n_cells': len(data),
            'significant': p_val < 0.05
        })
        
        print(f"\n{gene}:")
        print(f"  Correlation (r): {corr:.4f}")
        print(f"  P-value: {p_val:.2e}")
        print(f"  N cell lines: {len(data)}")
        
        if p_val < 0.05:
            if corr > 0:
                print(f"  ✅ SIGNIFICANT: Higher expression → Higher dependency")
            else:
                print(f"  ⚠️  SIGNIFICANT but NEGATIVE: Higher expression → Lower dependency")
        else:
            print(f"  ❌ NOT SIGNIFICANT")

global_corr_df = pd.DataFrame(global_corrs)

# ==============================================================================
# STEP 5: Per-Cancer-Type Correlation Analysis
# ==============================================================================

print("\n" + "=" * 80)
print("[STEP 5] Per-cancer-type correlation analysis...")
print("=" * 80)

cancer_corrs = []

for cancer_type in combined['OncotreePrimaryDisease'].dropna().unique():
    cancer_data = combined[combined['OncotreePrimaryDisease'] == cancer_type]
    
    # Need at least 3 cell lines for correlation
    if len(cancer_data) < 3:
        continue
    
    cancer_result = {
        'cancer_type': cancer_type,
        'n_cell_lines': len(cancer_data)
    }
    
    # Calculate correlation for each gene
    sig_corrs = []
    for gene in target_genes.keys():
        expr_col = f'{gene}_expression'
        dep_col = f'{gene}_dependency'
        
        data = cancer_data[[expr_col, dep_col]].dropna()
        
        if len(data) >= 3:
            try:
                corr, p_val = pearsonr(data[expr_col], data[dep_col])
                cancer_result[f'{gene}_corr'] = corr
                cancer_result[f'{gene}_corr_pval'] = p_val
                cancer_result[f'{gene}_expression_mean'] = data[expr_col].mean()
                cancer_result[f'{gene}_expression_std'] = data[expr_col].std()
                
                # Count significant positive correlations
                if p_val < 0.10 and corr > 0:
                    sig_corrs.append(corr)
            except:
                cancer_result[f'{gene}_corr'] = np.nan
                cancer_result[f'{gene}_corr_pval'] = np.nan
                cancer_result[f'{gene}_expression_mean'] = np.nan
                cancer_result[f'{gene}_expression_std'] = np.nan
        else:
            cancer_result[f'{gene}_corr'] = np.nan
            cancer_result[f'{gene}_corr_pval'] = np.nan
            cancer_result[f'{gene}_expression_mean'] = np.nan
            cancer_result[f'{gene}_expression_std'] = np.nan
    
    # Calculate high expression + high dependency count
    high_expr_high_dep = 0
    for gene in target_genes.keys():
        expr_col = f'{gene}_expression'
        dep_col = f'{gene}_dependency'
        
        # High expression = >75th percentile, High dependency = < -0.3
        expr_threshold = combined[expr_col].quantile(0.75)
        dep_threshold = -0.3
        
        mask = (cancer_data[expr_col] > expr_threshold) & (cancer_data[dep_col] < dep_threshold)
        high_expr_high_dep += mask.sum()
    
    cancer_result['high_expr_high_dep_count'] = high_expr_high_dep
    
    # Expression correlation score (0-1, based on avg of significant positive correlations)
    if len(sig_corrs) > 0:
        cancer_result['expression_correlation_score'] = min(1.0, max(0.0, np.mean(sig_corrs)))
    else:
        cancer_result['expression_correlation_score'] = 0.0
    
    cancer_corrs.append(cancer_result)

# Create DataFrame
cancer_corr_df = pd.DataFrame(cancer_corrs)
cancer_corr_df = cancer_corr_df.sort_values('expression_correlation_score', ascending=False)

print(f"\n✓ Analyzed {len(cancer_corr_df)} cancer types with ≥3 cell lines")
print(f"\nTop 10 by expression_correlation_score:")
top_10 = cancer_corr_df[['cancer_type', 'n_cell_lines', 'expression_correlation_score', 'high_expr_high_dep_count']].head(10)
print(top_10.to_string(index=False))

# ==============================================================================
# STEP 6: SAVE expression_correlation.csv (REQUIRED OUTPUT #1)
# ==============================================================================

print("\n[STEP 6] Saving expression_correlation.csv...")

# Prepare final output with all required columns
expression_correlation = cancer_corr_df.copy()

# Ensure all required columns are present
required_cols = ['cancer_type', 'n_cell_lines']
for gene in target_genes.keys():
    required_cols.extend([
        f'{gene}_expression_mean',
        f'{gene}_expression_std',
        f'{gene}_corr',
        f'{gene}_corr_pval'
    ])
required_cols.extend(['high_expr_high_dep_count', 'expression_correlation_score'])

expression_correlation = expression_correlation[required_cols]

# Save
output_file = DATA_PROCESSED / "expression_correlation.csv"
expression_correlation.to_csv(output_file, index=False)
print(f"✓ Saved: {output_file}")
print(f"  Rows: {len(expression_correlation)}")
print(f"  Columns: {len(expression_correlation.columns)}")

# ==============================================================================
# STEP 7: SAVE expression_summary.txt (REQUIRED OUTPUT #2)
# ==============================================================================

print("\n[STEP 7] Creating expression_summary.txt...")

summary_file = DATA_PROCESSED / "expression_summary.txt"

with open(summary_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("EXPRESSION CORRELATION ANALYSIS SUMMARY\n")
    f.write("Generated: 2025-10-30\n")
    f.write("=" * 80 + "\n\n")
    
    # Global correlations
    f.write("GLOBAL CORRELATIONS (All Cell Lines)\n")
    f.write("-" * 80 + "\n")
    for _, row in global_corr_df.iterrows():
        f.write(f"\n{row['gene']}:\n")
        f.write(f"  Correlation: r={row['correlation']:.4f}\n")
        f.write(f"  P-value: {row['p_value']:.2e}\n")
        f.write(f"  N cell lines: {row['n_cells']}\n")
        f.write(f"  Significant: {row['significant']}\n")
        
        if row['significant']:
            if row['correlation'] > 0:
                f.write(f"  ✅ Positive correlation: High expression → High dependency\n")
            else:
                f.write(f"  ⚠️  Negative correlation: High expression → Low dependency\n")
    
    # Top cancers by expression correlation
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("TOP 10 CANCER TYPES BY EXPRESSION CORRELATION SCORE\n")
    f.write("=" * 80 + "\n\n")
    
    top_10 = expression_correlation.head(10)
    for idx, row in top_10.iterrows():
        f.write(f"\n{idx + 1}. {row['cancer_type']}\n")
        f.write(f"   Score: {row['expression_correlation_score']:.3f}\n")
        f.write(f"   Cell lines: {row['n_cell_lines']}\n")
        f.write(f"   High expr + high dep: {row['high_expr_high_dep_count']}\n")
        
        # List correlations
        for gene in target_genes.keys():
            corr = row[f'{gene}_corr']
            pval = row[f'{gene}_corr_pval']
            if not np.isnan(corr):
                f.write(f"   {gene}: r={corr:.3f} (p={pval:.3f})\n")
    
    # Key findings
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("KEY FINDINGS\n")
    f.write("=" * 80 + "\n\n")
    
    # Which genes show positive correlation?
    pos_corr_genes = global_corr_df[
        (global_corr_df['significant']) & 
        (global_corr_df['correlation'] > 0)
    ]['gene'].tolist()
    
    if pos_corr_genes:
        f.write(f"Genes with positive expression-dependency correlation:\n")
        for gene in pos_corr_genes:
            f.write(f"  • {gene}\n")
    else:
        f.write("No genes show significant positive correlation globally.\n")
    
    f.write(f"\nCancer types with high expression correlation: {(expression_correlation['expression_correlation_score'] > 0.5).sum()}\n")
    f.write(f"Cancer types with high expr + high dep cells: {(expression_correlation['high_expr_high_dep_count'] > 5).sum()}\n")
    
    # Overall assessment
    f.write("\n\nOVERALL ASSESSMENT:\n")
    if len(pos_corr_genes) >= 2:
        f.write("Expression correlation supports biological relevance for multiple targets.\n")
        f.write("Cancer types with high expression AND high dependency represent optimal contexts.\n")
    elif len(pos_corr_genes) == 1:
        f.write("Modest expression-dependency correlation. Expression may be a biomarker for some targets.\n")
    else:
        f.write("Weak expression-dependency correlation overall. Dependency may be context-dependent\n")
        f.write("rather than driven by expression levels. Focus on mutation context and other factors.\n")

print(f"✓ Saved: {summary_file}")

# ==============================================================================
# STEP 8: FIGURE 1 - expression_dependency_scatter_4panel.png (REQUIRED OUTPUT #3)
# ==============================================================================

print("\n[STEP 8] Creating scatter plots (4-panel)...")

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.ravel()

# Get top 10 cancer types by combined_score_mean for coloring
top_cancers = cancer_rankings.head(10)['OncotreePrimaryDisease'].tolist()

for idx, gene in enumerate(target_genes.keys()):
    ax = axes[idx]
    
    expr_col = f'{gene}_expression'
    dep_col = f'{gene}_dependency'
    
    # Prepare data
    plot_data = combined[[expr_col, dep_col, 'OncotreePrimaryDisease']].dropna()
    
    # Color: top 10 cancers vs others
    colors = plot_data['OncotreePrimaryDisease'].apply(
        lambda x: '#E74C3C' if x in top_cancers else '#BDC3C7'
    )
    alphas = plot_data['OncotreePrimaryDisease'].apply(
        lambda x: 0.7 if x in top_cancers else 0.3
    )
    sizes = plot_data['OncotreePrimaryDisease'].apply(
        lambda x: 40 if x in top_cancers else 15
    )
    
    # Scatter plot
    for i in range(len(plot_data)):
        ax.scatter(
            plot_data.iloc[i][expr_col],
            plot_data.iloc[i][dep_col],
            color=colors.iloc[i],
            alpha=alphas.iloc[i],
            s=sizes.iloc[i],
            edgecolors='none'
        )
    
    # Regression line
    if len(plot_data) > 10:
        z = np.polyfit(plot_data[expr_col], plot_data[dep_col], 1)
        p = np.poly1d(z)
        x_sorted = np.sort(plot_data[expr_col])
        ax.plot(x_sorted, p(x_sorted), "k--", alpha=0.8, linewidth=2, label='Trend')
    
    # Get correlation
    corr, p_val = pearsonr(plot_data[expr_col], plot_data[dep_col])
    
    # Labels and title
    ax.set_xlabel(f'{gene} Expression (log2 TPM+1)', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'{gene} Dependency Score', fontsize=12, fontweight='bold')
    ax.set_title(f'{gene}\nr = {corr:.3f}, p = {p_val:.2e}', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3, linestyle='--')
    
    # Reference lines
    ax.axhline(y=-0.5, color='red', linestyle=':', alpha=0.5, linewidth=1.5, label='Strong dependency')
    ax.axhline(y=-0.3, color='orange', linestyle=':', alpha=0.5, linewidth=1.5, label='Moderate dependency')
    
    if idx == 0:
        # Create custom legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#E74C3C', alpha=0.7, label='Top 10 cancers'),
            Patch(facecolor='#BDC3C7', alpha=0.3, label='Other cancers'),
            plt.Line2D([0], [0], color='k', linestyle='--', linewidth=2, label='Trend'),
            plt.Line2D([0], [0], color='red', linestyle=':', linewidth=1.5, label='Strong dep'),
            plt.Line2D([0], [0], color='orange', linestyle=':', linewidth=1.5, label='Moderate dep')
        ]
        ax.legend(handles=legend_elements, fontsize=9, loc='best')

plt.suptitle('Expression vs Dependency Correlation - 4 Target Genes', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()

output_fig = FIGURES / "expression_dependency_scatter_4panel.png"
plt.savefig(output_fig, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ Saved: {output_fig}")

# ==============================================================================
# STEP 9: FIGURE 2 - cancer_type_expression_heatmap.png (REQUIRED OUTPUT #4)
# ==============================================================================

print("\n[STEP 9] Creating expression heatmap...")

# Get top 20 cancer types by combined_score_mean
top_20_cancers = cancer_rankings.head(20)['OncotreePrimaryDisease'].tolist()

# Filter expression data for these cancers
heatmap_data = expression_correlation[
    expression_correlation['cancer_type'].isin(top_20_cancers)
].copy()

# Sort by expression_correlation_score
heatmap_data = heatmap_data.sort_values('expression_correlation_score', ascending=False)

# Prepare matrix for heatmap
expr_matrix = []
for _, row in heatmap_data.iterrows():
    expr_values = [row[f'{gene}_expression_mean'] for gene in target_genes.keys()]
    expr_matrix.append(expr_values)

expr_matrix = np.array(expr_matrix)

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10), gridspec_kw={'width_ratios': [4, 1]})

# Heatmap
im = ax1.imshow(expr_matrix, cmap='YlOrRd', aspect='auto')

# Set ticks and labels
ax1.set_xticks(np.arange(len(target_genes)))
ax1.set_yticks(np.arange(len(heatmap_data)))
ax1.set_xticklabels(target_genes.keys(), fontsize=11, fontweight='bold')
ax1.set_yticklabels(heatmap_data['cancer_type'], fontsize=9)

# Add dependency scores as text overlays
for i, (_, row) in enumerate(heatmap_data.iterrows()):
    for j, gene in enumerate(target_genes.keys()):
        # Get dependency mean from cancer_rankings
        cancer_dep = cancer_rankings[
            cancer_rankings['OncotreePrimaryDisease'] == row['cancer_type']
        ]
        if len(cancer_dep) > 0:
            dep_val = cancer_dep[f'{gene}_dependency_mean'].values[0]
            text_color = 'white' if expr_matrix[i, j] > expr_matrix.mean() else 'black'
            ax1.text(j, i, f'{dep_val:.2f}', 
                    ha="center", va="center", color=text_color, fontsize=8)

ax1.set_title('Expression Levels (color) with Dependency Scores (text)\nTop 20 Cancer Types', 
             fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Target Genes', fontsize=12, fontweight='bold')
ax1.set_ylabel('Cancer Types (ranked by expression correlation)', fontsize=12, fontweight='bold')

# Colorbar
cbar = plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
cbar.set_label('Expression Level (log2 TPM+1)', fontsize=11, fontweight='bold')

# Second panel: Expression correlation scores
scores = heatmap_data['expression_correlation_score'].values
ax2.barh(np.arange(len(scores)), scores, color='steelblue', alpha=0.7)
ax2.set_yticks(np.arange(len(scores)))
ax2.set_yticklabels([])  # Hide labels (already shown in heatmap)
ax2.set_xlabel('Expression\nCorrelation Score', fontsize=11, fontweight='bold')
ax2.set_title('Correlation\nScore', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 1)
ax2.grid(axis='x', alpha=0.3)
ax2.invert_yaxis()

plt.tight_layout()

output_fig = FIGURES / "cancer_type_expression_heatmap.png"
plt.savefig(output_fig, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ Saved: {output_fig}")

# ==============================================================================
# STEP 10: FIGURE 3 - high_expression_high_dependency_candidates.png (REQUIRED OUTPUT #5)
# ==============================================================================

print("\n[STEP 10] Creating high expression + high dependency bar chart...")

# Sort by high_expr_high_dep_count
top_candidates = expression_correlation.sort_values('high_expr_high_dep_count', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(12, 8))

# Bar chart
bars = ax.barh(range(len(top_candidates)), top_candidates['high_expr_high_dep_count'], 
               color='#27AE60', alpha=0.7, edgecolor='darkgreen', linewidth=1.5)

# Add value labels
for i, (idx, row) in enumerate(top_candidates.iterrows()):
    ax.text(row['high_expr_high_dep_count'] + 0.3, i, 
           f"{int(row['high_expr_high_dep_count'])} cells", 
           va='center', fontsize=10)

ax.set_yticks(range(len(top_candidates)))
ax.set_yticklabels(top_candidates['cancer_type'], fontsize=10)
ax.set_xlabel('Cell Lines with High Expression + High Dependency', fontsize=12, fontweight='bold')
ax.set_title('Cancer Types with Most High Expression + High Dependency Cell Lines\n(Expression >75th percentile AND Dependency < -0.3)', 
            fontsize=14, fontweight='bold', pad=15)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.invert_yaxis()

# Add note about cell line counts
for i, (idx, row) in enumerate(top_candidates.iterrows()):
    n_cells = row['n_cell_lines']
    ax.text(0.5, i, f"(n={n_cells})", 
           va='center', ha='left', fontsize=8, color='gray', style='italic')

plt.tight_layout()

output_fig = FIGURES / "high_expression_high_dependency_candidates.png"
plt.savefig(output_fig, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ Saved: {output_fig}")

# ==============================================================================
# COMPLETION SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("✅ PROMPT 2 COMPLETE: Expression Correlation Analysis")
print("=" * 80)

print("\nOUTPUTS GENERATED:")
print("  1. ✓ data/processed/expression_correlation.csv")
print("  2. ✓ data/processed/expression_summary.txt")
print("  3. ✓ outputs/figures/expression_dependency_scatter_4panel.png")
print("  4. ✓ outputs/figures/cancer_type_expression_heatmap.png")
print("  5. ✓ outputs/figures/high_expression_high_dependency_candidates.png")

print("\nKEY RESULTS:")
print(f"  • Cancer types analyzed: {len(expression_correlation)}")
print(f"  • Top cancer by expression correlation: {expression_correlation.iloc[0]['cancer_type']}")
print(f"  • Genes with significant positive correlation: {len(global_corr_df[global_corr_df['significant'] & (global_corr_df['correlation'] > 0)])}/4")

print("\n" + "=" * 80)
print("READY FOR CURSOR VALIDATION")
print("=" * 80)
print("\nNext: Run Cursor validation, then proceed to PROMPT 2.5 (Copy Number Analysis)")
