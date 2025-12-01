#!/usr/bin/env python3
"""
Copy Number Analysis - PROMPT 2.5
Quick integration of copy number data for 4 target genes

Outputs:
1. data/processed/copy_number_analysis.csv
2. data/processed/copy_number_summary.txt
3. outputs/figures/copy_number_amplifications_heatmap.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
print("COPY NUMBER ANALYSIS - PROMPT 2.5")
print("=" * 80)

# ==============================================================================
# STEP 1: Load Required Data
# ==============================================================================

print("\n[STEP 1] Loading data files...")

# Check if copy number data exists
cn_file = DATA_RAW / "OmicsCNGeneWGS.csv"
if not cn_file.exists():
    print(f"\n⚠️  WARNING: Copy number data not found at {cn_file}")
    print("   This analysis will be skipped and documented as 'data unavailable'")
    
    # Create placeholder files
    with open(DATA_PROCESSED / "copy_number_summary.txt", 'w') as f:
        f.write("COPY NUMBER ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write("STATUS: Data Not Available\n\n")
        f.write("The copy number data file (OmicsCNGeneWGS.csv) was not found.\n")
        f.write("This analysis has been deferred.\n\n")
        f.write("RECOMMENDATION:\n")
        f.write("Proceed with available evidence dimensions. Copy number data\n")
        f.write("can be integrated in Phase 2 if it becomes available.\n")
    
    print("\n✓ Created placeholder summary documenting data unavailability")
    print("\n" + "=" * 80)
    print("COPY NUMBER ANALYSIS SKIPPED - DATA NOT AVAILABLE")
    print("=" * 80)
    sys.exit(0)

# Load copy number data
print("  Loading copy number data (may take 30-60 seconds)...")
copy_number = pd.read_csv(cn_file)
copy_number = copy_number.set_index('ModelID')
print(f"✓ Copy number data: {copy_number.shape}")

# Load cell line metadata
model = pd.read_csv(DATA_RAW / "Model.csv")
print(f"✓ Model metadata: {model.shape}")

# Load existing cancer rankings
cancer_rankings = pd.read_csv(DATA_PROCESSED / "cancer_type_rankings.csv")
print(f"✓ Cancer rankings: {cancer_rankings.shape}")

# ==============================================================================
# STEP 2: Extract Target Gene Copy Number Data
# ==============================================================================

print("\n[STEP 2] Extracting target gene copy number data...")

# Target genes with Entrez IDs
target_genes = {
    'STK17A': '9263',
    'MYLK4': '340156',
    'TBK1': '29110',
    'CLK4': '57396'
}

# Find columns in copy number data
cn_cols = {}
for gene, entrez_id in target_genes.items():
    matches = [col for col in copy_number.columns if gene in col and entrez_id in col]
    if matches:
        cn_cols[gene] = matches[0]
        print(f"  ✓ Copy number - {gene:10s}: {matches[0]}")
    else:
        print(f"  ⚠️  Copy number - {gene:10s}: NOT FOUND")

if len(cn_cols) == 0:
    print("\n⚠️  WARNING: No target genes found in copy number data")
    print("   Creating placeholder outputs and documenting issue")
    
    with open(DATA_PROCESSED / "copy_number_summary.txt", 'w') as f:
        f.write("COPY NUMBER ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write("STATUS: Target Genes Not Found\n\n")
        f.write("The target genes were not found in the copy number dataset.\n")
        f.write("Available columns may use different naming conventions.\n\n")
        f.write("RECOMMENDATION:\n")
        f.write("Manual inspection of column names needed to identify correct mappings.\n")
    
    print("\n✓ Created placeholder summary documenting issue")
    sys.exit(0)

# ==============================================================================
# STEP 3: Classify Copy Number States
# ==============================================================================

print("\n[STEP 3] Classifying copy number states...")

# Extract copy number data for target genes
cn_data = pd.DataFrame(index=copy_number.index)

for gene, col in cn_cols.items():
    cn_data[f'{gene}_CN'] = copy_number[col]
    
    # Classify states
    # Amplified: CN > 0.5
    # Normal: -0.5 <= CN <= 0.5
    # Deleted: CN < -0.5
    cn_data[f'{gene}_amplified'] = (cn_data[f'{gene}_CN'] > 0.5).astype(int)
    cn_data[f'{gene}_deleted'] = (cn_data[f'{gene}_CN'] < -0.5).astype(int)
    cn_data[f'{gene}_normal'] = ((cn_data[f'{gene}_CN'] >= -0.5) & (cn_data[f'{gene}_CN'] <= 0.5)).astype(int)

print(f"✓ Classified copy number states for {len(cn_cols)} genes")

# Add cancer type metadata
cn_data = cn_data.join(
    model.set_index('ModelID')[['CellLineName', 'OncotreePrimaryDisease', 'OncotreeLineage']], 
    how='left'
)

print(f"✓ Added metadata to {len(cn_data)} cell lines")

# ==============================================================================
# STEP 4: Calculate Per-Cancer-Type Statistics
# ==============================================================================

print("\n[STEP 4] Calculating per-cancer-type statistics...")

cancer_cn_stats = []

for cancer_type in cn_data['OncotreePrimaryDisease'].dropna().unique():
    cancer_data = cn_data[cn_data['OncotreePrimaryDisease'] == cancer_type]
    
    # Need at least 3 cell lines
    if len(cancer_data) < 3:
        continue
    
    cancer_result = {
        'cancer_type': cancer_type,
        'n_cell_lines': len(cancer_data)
    }
    
    # Calculate statistics for each gene
    total_amplified = 0
    for gene in cn_cols.keys():
        # Amplification statistics
        n_amplified = cancer_data[f'{gene}_amplified'].sum()
        pct_amplified = 100 * n_amplified / len(cancer_data)
        
        cancer_result[f'{gene}_amplified_pct'] = pct_amplified
        cancer_result[f'{gene}_amplified_count'] = n_amplified
        
        # Deletion statistics
        n_deleted = cancer_data[f'{gene}_deleted'].sum()
        cancer_result[f'{gene}_deleted_count'] = n_deleted
        
        # Mean copy number
        cancer_result[f'{gene}_CN_mean'] = cancer_data[f'{gene}_CN'].mean()
        
        total_amplified += n_amplified
    
    # Overall statistics
    cancer_result['any_target_amplified_pct'] = 100 * (cancer_data[[f'{gene}_amplified' for gene in cn_cols.keys()]].sum(axis=1) > 0).sum() / len(cancer_data)
    cancer_result['total_amplifications'] = total_amplified
    
    # Copy number score (0-1): based on frequency of amplifications
    # Higher = more cell lines with amplifications
    cancer_result['copy_number_score'] = min(1.0, cancer_result['any_target_amplified_pct'] / 50)  # Normalize: 50% = score of 1.0
    
    cancer_cn_stats.append(cancer_result)

# Create DataFrame
cancer_cn_df = pd.DataFrame(cancer_cn_stats)
cancer_cn_df = cancer_cn_df.sort_values('copy_number_score', ascending=False)

print(f"\n✓ Analyzed {len(cancer_cn_df)} cancer types with ≥3 cell lines")

# Show top 10
print(f"\nTop 10 by copy_number_score:")
top_10 = cancer_cn_df[['cancer_type', 'n_cell_lines', 'copy_number_score', 'any_target_amplified_pct', 'total_amplifications']].head(10)
print(top_10.to_string(index=False))

# ==============================================================================
# STEP 5: SAVE copy_number_analysis.csv (REQUIRED OUTPUT #1)
# ==============================================================================

print("\n[STEP 5] Saving copy_number_analysis.csv...")

# Select columns for output
output_cols = ['cancer_type', 'n_cell_lines']
for gene in cn_cols.keys():
    output_cols.extend([
        f'{gene}_amplified_pct',
        f'{gene}_amplified_count',
        f'{gene}_CN_mean'
    ])
output_cols.extend(['any_target_amplified_pct', 'total_amplifications', 'copy_number_score'])

copy_number_analysis = cancer_cn_df[output_cols].copy()

output_file = DATA_PROCESSED / "copy_number_analysis.csv"
copy_number_analysis.to_csv(output_file, index=False)
print(f"✓ Saved: {output_file}")
print(f"  Rows: {len(copy_number_analysis)}")
print(f"  Columns: {len(copy_number_analysis.columns)}")

# ==============================================================================
# STEP 6: SAVE copy_number_summary.txt (REQUIRED OUTPUT #2)
# ==============================================================================

print("\n[STEP 6] Creating copy_number_summary.txt...")

summary_file = DATA_PROCESSED / "copy_number_summary.txt"

with open(summary_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("COPY NUMBER ANALYSIS SUMMARY\n")
    f.write("Generated: 2025-10-30\n")
    f.write("=" * 80 + "\n\n")
    
    # Overall statistics
    f.write("OVERALL STATISTICS\n")
    f.write("-" * 80 + "\n")
    f.write(f"Cell lines analyzed: {len(cn_data)}\n")
    f.write(f"Cancer types analyzed: {len(cancer_cn_df)}\n")
    f.write(f"Target genes analyzed: {len(cn_cols)}\n\n")
    
    # Per-gene amplification frequency
    f.write("AMPLIFICATION FREQUENCY BY GENE (Across All Cell Lines)\n")
    f.write("-" * 80 + "\n")
    for gene in cn_cols.keys():
        n_amp = cn_data[f'{gene}_amplified'].sum()
        pct_amp = 100 * n_amp / len(cn_data)
        f.write(f"{gene:10s}: {n_amp:4d} cell lines ({pct_amp:5.1f}%)\n")
    
    # Top cancers by amplification
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("TOP 10 CANCER TYPES BY AMPLIFICATION FREQUENCY\n")
    f.write("=" * 80 + "\n\n")
    
    top_10 = copy_number_analysis.head(10)
    for idx, row in top_10.iterrows():
        f.write(f"\n{idx + 1}. {row['cancer_type']}\n")
        f.write(f"   Score: {row['copy_number_score']:.3f}\n")
        f.write(f"   Cell lines: {row['n_cell_lines']}\n")
        f.write(f"   Any target amplified: {row['any_target_amplified_pct']:.1f}%\n")
        f.write(f"   Total amplifications: {row['total_amplifications']}\n")
        
        # Per-gene amplification percentages
        f.write(f"   Gene-specific amplifications:\n")
        for gene in cn_cols.keys():
            pct = row[f'{gene}_amplified_pct']
            count = row[f'{gene}_amplified_count']
            if pct > 0:
                f.write(f"     • {gene}: {pct:.1f}% ({int(count)} cell lines)\n")
    
    # Clinical relevance
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("CLINICAL RELEVANCE\n")
    f.write("=" * 80 + "\n\n")
    
    # Count cancers with high amplification
    high_amp = (cancer_cn_df['any_target_amplified_pct'] > 20).sum()
    f.write(f"Cancer types with >20% amplification: {high_amp}\n")
    
    moderate_amp = ((cancer_cn_df['any_target_amplified_pct'] > 10) & (cancer_cn_df['any_target_amplified_pct'] <= 20)).sum()
    f.write(f"Cancer types with 10-20% amplification: {moderate_amp}\n")
    
    low_amp = (cancer_cn_df['any_target_amplified_pct'] <= 10).sum()
    f.write(f"Cancer types with <10% amplification: {low_amp}\n\n")
    
    f.write("INTERPRETATION:\n")
    if high_amp > 0:
        f.write("Gene amplifications present in select cancer types suggest potential\n")
        f.write("biomarker-driven patient selection opportunities. Amplification may\n")
        f.write("indicate oncogene addiction and enhanced therapeutic vulnerability.\n")
    else:
        f.write("Limited amplification across target genes suggests copy number\n")
        f.write("alterations are not a primary driver for these targets. Focus on\n")
        f.write("other evidence dimensions (dependency, expression, mutation context).\n")
    
    # Genes with most frequent amplifications
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("GENES WITH MOST FREQUENT AMPLIFICATIONS\n")
    f.write("=" * 80 + "\n\n")
    
    gene_amp_freq = []
    for gene in cn_cols.keys():
        n_cancers_with_amp = (cancer_cn_df[f'{gene}_amplified_pct'] > 10).sum()
        avg_amp_pct = cancer_cn_df[f'{gene}_amplified_pct'].mean()
        gene_amp_freq.append((gene, avg_amp_pct, n_cancers_with_amp))
    
    gene_amp_freq.sort(key=lambda x: x[1], reverse=True)
    
    for gene, avg_pct, n_cancers in gene_amp_freq:
        f.write(f"{gene:10s}: Average {avg_pct:5.1f}% amplified, {n_cancers} cancer types >10%\n")
    
    # Overall assessment
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("OVERALL ASSESSMENT\n")
    f.write("=" * 80 + "\n\n")
    
    max_amp_pct = cancer_cn_df['any_target_amplified_pct'].max()
    if max_amp_pct > 30:
        f.write("✅ Strong amplification signals in select cancer types.\n")
        f.write("   Copy number can serve as a biomarker for patient stratification.\n")
    elif max_amp_pct > 15:
        f.write("⚠️  Moderate amplification signals.\n")
        f.write("   Copy number may be a supplementary biomarker in some contexts.\n")
    else:
        f.write("❌ Weak amplification signals overall.\n")
        f.write("   Copy number is likely not a primary biomarker for these targets.\n")
        f.write("   Prioritize dependency, expression, and mutation context evidence.\n")

print(f"✓ Saved: {summary_file}")

# ==============================================================================
# STEP 7: FIGURE - copy_number_amplifications_heatmap.png (REQUIRED OUTPUT #3)
# ==============================================================================

print("\n[STEP 7] Creating amplification heatmap...")

# Get top 20 cancer types by amplification frequency
top_20_cancers = copy_number_analysis.head(20)

# Prepare matrix for heatmap
amp_matrix = []
cancer_labels = []

for _, row in top_20_cancers.iterrows():
    amp_values = [row[f'{gene}_amplified_pct'] for gene in cn_cols.keys()]
    amp_matrix.append(amp_values)
    
    # Create label with sample size
    label = f"{row['cancer_type'][:45]} (n={row['n_cell_lines']})"
    cancer_labels.append(label)

amp_matrix = np.array(amp_matrix)

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 10), gridspec_kw={'width_ratios': [4, 1]})

# Heatmap
im = ax1.imshow(amp_matrix, cmap='Reds', aspect='auto', vmin=0, vmax=50)

# Set ticks and labels
ax1.set_xticks(np.arange(len(cn_cols)))
ax1.set_yticks(np.arange(len(top_20_cancers)))
ax1.set_xticklabels(cn_cols.keys(), fontsize=12, fontweight='bold', rotation=0)
ax1.set_yticklabels(cancer_labels, fontsize=8)

# Add percentage text overlays
for i in range(len(top_20_cancers)):
    for j in range(len(cn_cols)):
        value = amp_matrix[i, j]
        if value > 0:
            text_color = 'white' if value > 25 else 'black'
            ax1.text(j, i, f'{value:.0f}%', 
                    ha="center", va="center", color=text_color, 
                    fontsize=9, fontweight='bold')

ax1.set_title('Gene Amplification Frequency\nTop 20 Cancer Types', 
             fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Target Genes', fontsize=12, fontweight='bold')
ax1.set_ylabel('Cancer Types (ranked by amplification frequency)', fontsize=12, fontweight='bold')

# Colorbar
cbar = plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
cbar.set_label('Amplification Frequency (%)', fontsize=11, fontweight='bold')

# Second panel: Copy number scores
scores = top_20_cancers['copy_number_score'].values
ax2.barh(np.arange(len(scores)), scores, color='#E74C3C', alpha=0.7, edgecolor='darkred')
ax2.set_yticks(np.arange(len(scores)))
ax2.set_yticklabels([])  # Hide labels (already shown in heatmap)
ax2.set_xlabel('Copy Number\nScore', fontsize=11, fontweight='bold')
ax2.set_title('CN Score', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 1)
ax2.grid(axis='x', alpha=0.3)
ax2.invert_yaxis()

# Add score values
for i, score in enumerate(scores):
    ax2.text(score + 0.02, i, f'{score:.2f}', va='center', fontsize=8)

plt.tight_layout()

output_fig = FIGURES / "copy_number_amplifications_heatmap.png"
plt.savefig(output_fig, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ Saved: {output_fig}")

# ==============================================================================
# COMPLETION SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("✅ PROMPT 2.5 COMPLETE: Copy Number Analysis")
print("=" * 80)

print("\nOUTPUTS GENERATED:")
print("  1. ✓ data/processed/copy_number_analysis.csv")
print("  2. ✓ data/processed/copy_number_summary.txt")
print("  3. ✓ outputs/figures/copy_number_amplifications_heatmap.png")

print("\nKEY RESULTS:")
print(f"  • Cancer types analyzed: {len(cancer_cn_df)}")
print(f"  • Top cancer by amplification: {copy_number_analysis.iloc[0]['cancer_type']}")
print(f"  • Max amplification frequency: {cancer_cn_df['any_target_amplified_pct'].max():.1f}%")
print(f"  • Genes analyzed: {', '.join(cn_cols.keys())}")

print("\n" + "=" * 80)
print("READY FOR CURSOR VALIDATION")
print("=" * 80)
print("\nNext: Run Cursor validation, then proceed to PROMPT 3 (Literature Review)")
