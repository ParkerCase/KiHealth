#!/usr/bin/env python3
"""Christian's 814H RNAseq Analysis - Quick Impact Assessment"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path('/Users/parkercase/starx-therapeutics-analysis')
CHRISTIAN_DIR = BASE_DIR / 'data' / 'raw' / 'StarXData' / 'RNAseq from 814H and the new proteomics'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
FIGURES_DIR = BASE_DIR / 'outputs' / 'figures'

print("="*80)
print("CHRISTIAN'S 814H RNASEQ ANALYSIS")
print("="*80)

# Load data
print("\n[1/6] Loading data...")
deg_path = CHRISTIAN_DIR / 'Differential_expression_analysis_table.csv'
deg = pd.read_csv(deg_path)
print(f"✅ Loaded: {len(deg):,} genes")

# Identify columns
print("\n[2/6] Identifying columns...")
print("\nColumns:", list(deg.columns))

gene_col = log2fc_col = padj_col = None
for col in deg.columns:
    col_lower = col.lower()
    if not gene_col and any(x in col_lower for x in ['gene', 'symbol']):
        gene_col = col
    if not log2fc_col and any(x in col_lower for x in ['log2fold', 'log2fc', 'logfc']):
        log2fc_col = col
    if not padj_col and any(x in col_lower for x in ['padj', 'adj', 'fdr', 'qval']):
        padj_col = col

deg = deg.rename(columns={gene_col: 'gene', log2fc_col: 'log2fc', padj_col: 'padj'})

# Statistics
print("\n[3/6] Statistics...")
deg_sig = deg[deg['padj'] < 0.05]
print(f"Significant genes (p<0.05): {len(deg_sig):,}")
print(f"  Up: {len(deg_sig[deg_sig['log2fc'] > 0]):,}")
print(f"  Down: {len(deg_sig[deg_sig['log2fc'] < 0]):,}")

# Target genes
print("\n[4/6] Target genes...")
target_genes = ['STK17A', 'MYLK4', 'TBK1', 'CLK4']
target_results = []

for target in target_genes:
    match = deg[deg['gene'].str.upper() == target.upper()]
    if len(match) > 0:
        row = match.iloc[0]
        print(f"✅ {target}: log2FC={row['log2fc']:.3f}, p_adj={row['padj']:.2e}")
        target_results.append({
            'target': target, 'log2fc': row['log2fc'], 
            'padj': row['padj'], 'significant': row['padj'] < 0.05
        })
    else:
        print(f"❌ {target}: NOT FOUND")
        target_results.append({
            'target': target, 'log2fc': np.nan, 
            'padj': np.nan, 'significant': False
        })

target_df = pd.DataFrame(target_results)

# Impact
print("\n[5/6] Impact assessment...")
n_sig = target_df['significant'].sum()
print(f"Target genes significant: {n_sig}/4")

if n_sig >= 2:
    rec = "HIGH_IMPACT - Integrate into report (4-6 hrs)"
elif n_sig == 1:
    rec = "MODERATE_IMPACT - Add section (2-3 hrs)"
else:
    rec = "LOW_IMPACT - Brief mention (30 min)"

print(f"\nRECOMMENDATION: {rec}")

# Save
print("\n[6/6] Saving...")
target_df.to_csv(PROCESSED_DIR / 'christian_target_genes_analysis.csv', index=False)
if len(deg_sig) > 0:
    deg_sig.to_csv(PROCESSED_DIR / 'christian_deg_significant.csv', index=False)

with open(PROCESSED_DIR / 'christian_rnaseq_summary.txt', 'w') as f:
    f.write(f"CHRISTIAN 814H RNASEQ SUMMARY\n\n")
    f.write(f"Significant genes: {len(deg_sig):,}\n")
    f.write(f"Targets affected: {n_sig}/4\n")
    f.write(f"RECOMMENDATION: {rec}\n\n")
    f.write(target_df.to_string(index=False))

print("\n✅ DONE! Check:")
print("  - christian_target_genes_analysis.csv")
print("  - christian_rnaseq_summary.txt")
print(f"\n{rec}")
