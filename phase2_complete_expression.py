"""
PHASE 2: Complete Expression Correlation Analysis
Correlate expression with dependency for all 4 targets
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("PHASE 2: COMPLETE EXPRESSION CORRELATION ANALYSIS")
print("="*80)

# Load DepMap dependency data (full)
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

# Load CCLE expression data
print("\nLoading expression data...")
expression = pd.read_csv('data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv')

# Find target gene columns
expr_targets = {
    'STK17A': [col for col in expression.columns if 'STK17A (9263)' in col][0],
    'MYLK4': [col for col in expression.columns if 'MYLK4' in col][0],
    'TBK1': [col for col in expression.columns if 'TBK1 (29110)' in col][0],  # Not TTBK1
    'CLK4': [col for col in expression.columns if 'CLK4' in col][0]
}

expr_clean = expression[['ModelID'] + list(expr_targets.values())].copy()
expr_clean.columns = ['ModelID', 'STK17A_expr', 'MYLK4_expr', 'TBK1_expr', 'CLK4_expr']

print(f"Expression data: {len(expr_clean)} cell lines")

# Merge dependency and expression
print("\nMerging datasets...")
merged = dep_clean.merge(expr_clean, on='ModelID', how='inner')
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
print(f"Cancer types: {merged['OncotreePrimaryDisease'].nunique()}")

# Calculate overall correlations
print("\n" + "="*80)
print("OVERALL EXPRESSION-DEPENDENCY CORRELATIONS")
print("="*80)

overall_corrs = {}
for gene in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
    dep_col = f'{gene}_dep'
    expr_col = f'{gene}_expr'
    
    # Remove NaN
    valid = merged[[dep_col, expr_col]].dropna()
    
    if len(valid) > 0:
        corr, pval = stats.pearsonr(valid[dep_col], valid[expr_col])
        overall_corrs[gene] = {
            'correlation': corr,
            'p_value': pval,
            'n': len(valid)
        }
        
        print(f"\n{gene}:")
        print(f"  Correlation: {corr:.4f}")
        print(f"  P-value: {pval:.4e}")
        print(f"  N: {len(valid)} cell lines")
        
        if pval < 0.05:
            direction = "POSITIVE" if corr > 0 else "NEGATIVE"
            print(f"  ✅ SIGNIFICANT {direction} correlation")
        else:
            print(f"  ⚠️  Not significant")

# Calculate per-cancer-type correlations
print("\n" + "="*80)
print("PER-CANCER-TYPE ANALYSIS")
print("="*80)

cancer_results = []

for cancer in merged['OncotreePrimaryDisease'].dropna().unique():
    cancer_data = merged[merged['OncotreePrimaryDisease'] == cancer]
    
    if len(cancer_data) < 3:
        continue  # Need minimum sample size
    
    cancer_result = {
        'cancer_type': cancer,
        'n_cell_lines': len(cancer_data)
    }
    
    # For each gene
    for gene in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
        dep_col = f'{gene}_dep'
        expr_col = f'{gene}_expr'
        
        valid = cancer_data[[dep_col, expr_col]].dropna()
        
        if len(valid) >= 3:
            # Mean expression
            cancer_result[f'{gene}_expr_mean'] = valid[expr_col].mean()
            cancer_result[f'{gene}_expr_std'] = valid[expr_col].std()
            
            # Mean dependency
            cancer_result[f'{gene}_dep_mean'] = valid[dep_col].mean()
            cancer_result[f'{gene}_dep_std'] = valid[dep_col].std()
            
            # Correlation (if enough data)
            if len(valid) >= 5:
                try:
                    corr, pval = stats.pearsonr(valid[dep_col], valid[expr_col])
                    cancer_result[f'{gene}_corr'] = corr
                    cancer_result[f'{gene}_corr_pval'] = pval
                except:
                    cancer_result[f'{gene}_corr'] = np.nan
                    cancer_result[f'{gene}_corr_pval'] = np.nan
            else:
                cancer_result[f'{gene}_corr'] = np.nan
                cancer_result[f'{gene}_corr_pval'] = np.nan
            
            # High expression + high dependency count
            # High expression = > 75th percentile
            # High dependency = < -0.3
            expr_threshold = merged[expr_col].quantile(0.75)
            high_both = ((valid[expr_col] > expr_threshold) & (valid[dep_col] < -0.3)).sum()
            cancer_result[f'{gene}_high_both'] = high_both
        else:
            # Insufficient data
            for suffix in ['_expr_mean', '_expr_std', '_dep_mean', '_dep_std', 
                          '_corr', '_corr_pval', '_high_both']:
                cancer_result[f'{gene}{suffix}'] = np.nan
    
    cancer_results.append(cancer_result)

# Convert to DataFrame
cancer_df = pd.DataFrame(cancer_results)

# Calculate expression_correlation_score for integration
# This is a normalized score (0-1) representing strength of evidence
def calculate_expr_score(row):
    scores = []
    for gene in ['STK17A', 'MYLK4', 'TBK1', 'CLK4']:
        dep_mean = row[f'{gene}_dep_mean']
        expr_mean = row[f'{gene}_expr_mean']
        high_both = row[f'{gene}_high_both']
        
        # Skip if missing
        if pd.isna(dep_mean) or pd.isna(expr_mean):
            continue
        
        # Score based on:
        # 1. High expression (normalized)
        # 2. High dependency (more negative = better)
        # 3. Cell lines with both
        
        expr_norm = min(1.0, expr_mean / 10.0)  # Normalize expression
        dep_norm = max(0.0, min(1.0, abs(dep_mean) / 0.5))  # Normalize dependency
        both_norm = min(1.0, high_both / 3.0)  # Normalize count
        
        gene_score = (expr_norm + dep_norm + both_norm) / 3.0
        scores.append(gene_score)
    
    return np.mean(scores) if scores else 0.0

cancer_df['expression_correlation_score'] = cancer_df.apply(calculate_expr_score, axis=1)

# Save results
cancer_df.to_csv('data/processed/expression_correlation_COMPLETE.csv', index=False)
print(f"\n✅ Saved: data/processed/expression_correlation_COMPLETE.csv")

# Show top cancer types by expression score
print("\n" + "="*80)
print("TOP 20 CANCER TYPES BY EXPRESSION-DEPENDENCY SCORE")
print("="*80)

top20 = cancer_df.nsmallest(20, 'expression_correlation_score')  # Lowest score = best (most negative dep)

print(f"\n{'Rank':<6}{'Cancer Type':<45}{'N':<6}{'Expr Score':<12}")
print("-" * 75)

for rank, (idx, row) in enumerate(top20.iterrows(), 1):
    cancer = row['cancer_type'][:44]
    n = int(row['n_cell_lines'])
    score = row['expression_correlation_score']
    print(f"{rank:<6}{cancer:<45}{n:<6}{score:.4f}")

print("\n" + "="*80)
print("PHASE 2 COMPLETE")
print("="*80)
