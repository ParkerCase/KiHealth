#!/usr/bin/env python3
"""COMPLETE EXPERIMENTAL INTEGRATION - Add all missing experimental data"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path('/Users/parkercase/starx-therapeutics-analysis')
STARX_DIR = BASE_DIR / 'data' / 'raw' / 'StarXData'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

print("="*100)
print("COMPLETE EXPERIMENTAL INTEGRATION")
print("="*100)

# Load existing IC50 validation
print("\n[1/4] Loading existing IC50 validation...")
exp_val = pd.read_csv(PROCESSED_DIR / 'experimental_validation.csv')
print(f"✓ {len(exp_val)} cancer types")
print(f"  Columns: {list(exp_val.columns)}")

# Initialize new evidence columns
exp_val['deg_evidence'] = 0.0
exp_val['phospho_evidence'] = 0.0
exp_val['ipms_evidence'] = 0.0

# ===========================================================================
# RNASEQ DEGS
# ===========================================================================

print("\n[2/4] Processing RNAseq DEGs...")
deg_dir = STARX_DIR / 'DEGs'
deg_files = list(deg_dir.glob('*.csv'))
print(f"  Found {len(deg_files)} files")

for deg_file in deg_files:
    try:
        deg = pd.read_csv(deg_file)
        
        # Find columns
        gene_col = next((c for c in deg.columns if any(x in c.lower() for x in ['gene', 'symbol'])), None)
        if not gene_col:
            continue
        
        deg_sig = deg[deg.iloc[:, -2] < 0.05] if len(deg.columns) > 2 else deg[:100]  # Assume last col is padj
        
        # K562/K666N = AML-like
        if 'K562' in deg_file.name or 'K666' in deg_file.name:
            aml_mask = exp_val['cancer_type'].str.contains('Myeloid', case=False, na=False)
            exp_val.loc[aml_mask, 'deg_evidence'] = 1.0
            print(f"  ✓ {deg_file.name}: {len(deg_sig)} genes → AML")
        
    except Exception as e:
        print(f"  ⚠️  {deg_file.name}: {str(e)}")

# ===========================================================================
# PHOSPHOPROTEOMICS
# ===========================================================================

print("\n[3/4] Processing Phosphoproteomics...")
phospho_dir = STARX_DIR / 'GBM43 Phosphoproteomics'
phospho_files = list(phospho_dir.glob('*.csv'))
print(f"  Found {len(phospho_files)} files")

for phospho_file in phospho_files:
    try:
        phospho = pd.read_csv(phospho_file)
        
        # GBM43 = Glioblastoma
        gbm_mask = exp_val['cancer_type'].str.contains('Glioma|Glioblastoma', case=False, na=False)
        exp_val.loc[gbm_mask, 'phospho_evidence'] = 1.0
        
        print(f"  ✓ {phospho_file.name}: {len(phospho)} proteins → Glioblastoma")
        
    except Exception as e:
        print(f"  ⚠️  {phospho_file.name}: {str(e)}")

# ===========================================================================
# IP-MS
# ===========================================================================

print("\n[4/4] Processing IP-MS...")
ipms_dir = STARX_DIR / 'GBM43 IP-MS'
ipms_files = list(ipms_dir.glob('*.csv'))
print(f"  Found {len(ipms_files)} files")

for ipms_file in ipms_files:
    try:
        ipms = pd.read_csv(ipms_file)
        
        # GBM43 = Glioblastoma
        gbm_mask = exp_val['cancer_type'].str.contains('Glioma|Glioblastoma', case=False, na=False)
        exp_val.loc[gbm_mask, 'ipms_evidence'] = 1.0
        
        print(f"  ✓ {ipms_file.name}: {len(ipms)} proteins → Glioblastoma")
        
    except Exception as e:
        print(f"  ⚠️  {ipms_file.name}: {str(e)}")

# ===========================================================================
# CALCULATE COMPREHENSIVE SCORE
# ===========================================================================

print("\n[FINAL] Calculating comprehensive experimental scores...")

# Use existing validation_score_normalized as IC50 evidence base
ic50_evidence = exp_val['validation_score'].fillna(0.0)

# Calculate comprehensive score
exp_val['experimental_validation_score_NEW'] = (
    0.40 * ic50_evidence +
    0.30 * exp_val['deg_evidence'] +
    0.20 * exp_val['phospho_evidence'] +
    0.10 * exp_val['ipms_evidence']
)

# Update validation_score column
exp_val['validation_score'] = exp_val['experimental_validation_score_NEW']

# Count evidence sources
exp_val['n_evidence_sources'] = (
    (exp_val['n_validated_cell_lines'] > 0).astype(int) +
    (exp_val['deg_evidence'] > 0).astype(int) +
    (exp_val['phospho_evidence'] > 0).astype(int) +
    (exp_val['ipms_evidence'] > 0).astype(int)
)

print(f"\n✓ Evidence distribution:")
print(f"  IC50: {(exp_val['n_validated_cell_lines'] > 0).sum()} cancer types")
print(f"  DEG: {(exp_val['deg_evidence'] > 0).sum()} cancer types")
print(f"  Phospho: {(exp_val['phospho_evidence'] > 0).sum()} cancer types")
print(f"  IP-MS: {(exp_val['ipms_evidence'] > 0).sum()} cancer types")
print(f"  Multiple: {(exp_val['n_evidence_sources'] > 1).sum()} cancer types")

# ===========================================================================
# SAVE
# ===========================================================================

print("\n[SAVE] Saving updated experimental_validation.csv...")

exp_val.to_csv(PROCESSED_DIR / 'experimental_validation.csv', index=False)
print(f"✓ Saved: {len(exp_val)} rows")

print("\nTop 10 by comprehensive score:")
top10 = exp_val.nlargest(10, 'validation_score')[['cancer_type', 'validation_score', 'n_evidence_sources']]
print(top10.to_string(index=False))

print("\n" + "="*100)
print("✅ COMPLETE - Now update final rankings")
print("="*100)
