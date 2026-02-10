"""
PROMPT 2 VALIDATION SCRIPT
Run this in Cursor AI to validate expression correlation analysis outputs
"""

import pandas as pd
import os
from pathlib import Path

print("=" * 80)
print("PROMPT 2: EXPRESSION CORRELATION ANALYSIS - VALIDATION")
print("=" * 80)

PROJECT_ROOT = Path("/Users/parkercase/starx-therapeutics-analysis")
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

validation_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

# ==============================================================================
# CHECK 1: Required Files Exist
# ==============================================================================

print("\n[CHECK 1] Verifying required files exist...")

required_files = {
    "expression_correlation.csv": DATA_PROCESSED / "expression_correlation.csv",
    "expression_summary.txt": DATA_PROCESSED / "expression_summary.txt",
    "expression_dependency_scatter_4panel.png": FIGURES / "expression_dependency_scatter_4panel.png",
    "cancer_type_expression_heatmap.png": FIGURES / "cancer_type_expression_heatmap.png",
    "high_expression_high_dependency_candidates.png": FIGURES / "high_expression_high_dependency_candidates.png"
}

for name, path in required_files.items():
    if path.exists():
        print(f"  ✓ {name}")
        validation_results["passed"].append(f"File exists: {name}")
    else:
        print(f"  ✗ {name} - MISSING!")
        validation_results["failed"].append(f"File missing: {name}")

# ==============================================================================
# CHECK 2: expression_correlation.csv Structure
# ==============================================================================

print("\n[CHECK 2] Validating expression_correlation.csv structure...")

try:
    expr_df = pd.read_csv(DATA_PROCESSED / "expression_correlation.csv")
    
    # Check required columns
    required_cols = [
        'cancer_type', 'n_cell_lines',
        'STK17A_expression_mean', 'STK17A_expression_std', 'STK17A_corr', 'STK17A_corr_pval',
        'MYLK4_expression_mean', 'MYLK4_expression_std', 'MYLK4_corr', 'MYLK4_corr_pval',
        'TBK1_expression_mean', 'TBK1_expression_std', 'TBK1_corr', 'TBK1_corr_pval',
        'CLK4_expression_mean', 'CLK4_expression_std', 'CLK4_corr', 'CLK4_corr_pval',
        'high_expr_high_dep_count', 'expression_correlation_score'
    ]
    
    missing_cols = [col for col in required_cols if col not in expr_df.columns]
    if missing_cols:
        print(f"  ✗ Missing columns: {missing_cols}")
        validation_results["failed"].append(f"Missing columns in expression_correlation.csv: {missing_cols}")
    else:
        print(f"  ✓ All required columns present")
        validation_results["passed"].append("expression_correlation.csv has all required columns")
    
    # Check row count (should have many cancer types, at least 40+)
    if len(expr_df) >= 40:
        print(f"  ✓ Row count: {len(expr_df)} cancer types")
        validation_results["passed"].append(f"expression_correlation.csv has {len(expr_df)} rows")
    else:
        print(f"  ⚠️  Row count: {len(expr_df)} (expected ≥40)")
        validation_results["warnings"].append(f"expression_correlation.csv has only {len(expr_df)} rows (expected ≥40)")
    
    # Check data types
    if expr_df['n_cell_lines'].dtype in ['int64', 'int32']:
        print(f"  ✓ n_cell_lines is integer")
        validation_results["passed"].append("n_cell_lines is integer type")
    else:
        print(f"  ✗ n_cell_lines is not integer: {expr_df['n_cell_lines'].dtype}")
        validation_results["failed"].append(f"n_cell_lines has wrong type: {expr_df['n_cell_lines'].dtype}")
    
    # Check expression_correlation_score is between 0-1
    if (expr_df['expression_correlation_score'] >= 0).all() and (expr_df['expression_correlation_score'] <= 1).all():
        print(f"  ✓ expression_correlation_score is 0-1")
        validation_results["passed"].append("expression_correlation_score is in [0,1] range")
    else:
        print(f"  ✗ expression_correlation_score outside [0,1]")
        validation_results["failed"].append("expression_correlation_score has values outside [0,1]")
    
    # Check for unexpected NaN values in critical columns
    critical_cols = ['cancer_type', 'n_cell_lines', 'expression_correlation_score']
    nan_cols = [col for col in critical_cols if expr_df[col].isna().any()]
    if nan_cols:
        print(f"  ✗ Unexpected NaN values in: {nan_cols}")
        validation_results["failed"].append(f"Unexpected NaN in critical columns: {nan_cols}")
    else:
        print(f"  ✓ No unexpected NaN values in critical columns")
        validation_results["passed"].append("No NaN in critical columns")
    
except Exception as e:
    print(f"  ✗ Error loading/validating expression_correlation.csv: {e}")
    validation_results["failed"].append(f"Error with expression_correlation.csv: {e}")

# ==============================================================================
# CHECK 3: Cross-Reference with cancer_type_rankings.csv
# ==============================================================================

print("\n[CHECK 3] Cross-referencing with cancer_type_rankings.csv...")

try:
    rankings_df = pd.read_csv(DATA_PROCESSED / "cancer_type_rankings.csv")
    
    # Check if cancer types overlap
    rankings_cancers = set(rankings_df['OncotreePrimaryDisease'])
    expr_cancers = set(expr_df['cancer_type'])
    
    overlap = rankings_cancers & expr_cancers
    print(f"  ✓ Cancer types overlap: {len(overlap)}/{len(rankings_cancers)}")
    
    if len(overlap) >= 40:
        validation_results["passed"].append(f"Good overlap between files: {len(overlap)} cancer types")
    else:
        validation_results["warnings"].append(f"Limited overlap: only {len(overlap)} cancer types match")
    
except Exception as e:
    print(f"  ⚠️  Could not cross-reference: {e}")
    validation_results["warnings"].append(f"Cross-reference check failed: {e}")

# ==============================================================================
# CHECK 4: Correlation Values Sanity
# ==============================================================================

print("\n[CHECK 4] Sanity checks on correlation values...")

try:
    # Check correlation coefficients are between -1 and 1
    corr_cols = [col for col in expr_df.columns if col.endswith('_corr')]
    
    for col in corr_cols:
        # Check valid range (allowing for NaN)
        valid_range = expr_df[col].dropna().between(-1, 1).all()
        if valid_range:
            print(f"  ✓ {col} in [-1, 1] range")
            validation_results["passed"].append(f"{col} values are valid")
        else:
            print(f"  ✗ {col} has values outside [-1, 1]")
            validation_results["failed"].append(f"{col} has invalid correlation values")
    
    # Check p-values are between 0 and 1
    pval_cols = [col for col in expr_df.columns if col.endswith('_pval')]
    
    for col in pval_cols:
        valid_range = expr_df[col].dropna().between(0, 1).all()
        if valid_range:
            print(f"  ✓ {col} in [0, 1] range")
            validation_results["passed"].append(f"{col} values are valid")
        else:
            print(f"  ✗ {col} has values outside [0, 1]")
            validation_results["failed"].append(f"{col} has invalid p-values")
    
except Exception as e:
    print(f"  ✗ Error in sanity checks: {e}")
    validation_results["failed"].append(f"Sanity check error: {e}")

# ==============================================================================
# CHECK 5: expression_summary.txt Content
# ==============================================================================

print("\n[CHECK 5] Validating expression_summary.txt content...")

try:
    with open(DATA_PROCESSED / "expression_summary.txt", 'r') as f:
        summary_content = f.read()
    
    # Check for required sections
    required_sections = [
        "GLOBAL CORRELATIONS",
        "TOP 10 CANCER TYPES",
        "KEY FINDINGS",
        "OVERALL ASSESSMENT"
    ]
    
    for section in required_sections:
        if section in summary_content:
            print(f"  ✓ Section present: {section}")
            validation_results["passed"].append(f"summary.txt has {section} section")
        else:
            print(f"  ✗ Section missing: {section}")
            validation_results["failed"].append(f"summary.txt missing {section} section")
    
    # Check file is not empty
    if len(summary_content) > 100:
        print(f"  ✓ File has substantial content ({len(summary_content)} chars)")
        validation_results["passed"].append("summary.txt has good content")
    else:
        print(f"  ✗ File is too short ({len(summary_content)} chars)")
        validation_results["failed"].append("summary.txt is too short")
    
except Exception as e:
    print(f"  ✗ Error reading summary.txt: {e}")
    validation_results["failed"].append(f"Error with summary.txt: {e}")

# ==============================================================================
# CHECK 6: Figure Files
# ==============================================================================

print("\n[CHECK 6] Validating figure files...")

figure_files = [
    "expression_dependency_scatter_4panel.png",
    "cancer_type_expression_heatmap.png",
    "high_expression_high_dependency_candidates.png"
]

for fig in figure_files:
    fig_path = FIGURES / fig
    if fig_path.exists():
        size = fig_path.stat().st_size
        if size > 10000:  # At least 10KB
            print(f"  ✓ {fig} ({size:,} bytes)")
            validation_results["passed"].append(f"{fig} exists and has good size")
        else:
            print(f"  ⚠️  {fig} exists but is very small ({size} bytes)")
            validation_results["warnings"].append(f"{fig} is suspiciously small")
    else:
        print(f"  ✗ {fig} - MISSING!")
        validation_results["failed"].append(f"Figure missing: {fig}")

# ==============================================================================
# FINAL VALIDATION REPORT
# ==============================================================================

print("\n" + "=" * 80)
print("VALIDATION SUMMARY")
print("=" * 80)

print(f"\n✅ PASSED: {len(validation_results['passed'])}")
for item in validation_results['passed'][:5]:  # Show first 5
    print(f"  • {item}")
if len(validation_results['passed']) > 5:
    print(f"  ... and {len(validation_results['passed']) - 5} more")

if validation_results['warnings']:
    print(f"\n⚠️  WARNINGS: {len(validation_results['warnings'])}")
    for item in validation_results['warnings']:
        print(f"  • {item}")

if validation_results['failed']:
    print(f"\n❌ FAILED: {len(validation_results['failed'])}")
    for item in validation_results['failed']:
        print(f"  • {item}")
    print("\n🚨 VALIDATION FAILED - FIX ISSUES BEFORE PROCEEDING")
else:
    print("\n🎉 ALL VALIDATIONS PASSED!")
    print("\n✅ READY TO PROCEED TO PROMPT 2.5 (Copy Number Analysis)")

print("=" * 80)

# Save validation report
validation_report_path = PROJECT_ROOT / "outputs" / "reports" / "validation_prompt_2.txt"
validation_report_path.parent.mkdir(parents=True, exist_ok=True)

with open(validation_report_path, 'w') as f:
    f.write("PROMPT 2 VALIDATION REPORT\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Passed: {len(validation_results['passed'])}\n")
    f.write(f"Warnings: {len(validation_results['warnings'])}\n")
    f.write(f"Failed: {len(validation_results['failed'])}\n\n")
    
    if validation_results['passed']:
        f.write("PASSED CHECKS:\n")
        for item in validation_results['passed']:
            f.write(f"  ✓ {item}\n")
        f.write("\n")
    
    if validation_results['warnings']:
        f.write("WARNINGS:\n")
        for item in validation_results['warnings']:
            f.write(f"  ⚠️  {item}\n")
        f.write("\n")
    
    if validation_results['failed']:
        f.write("FAILED CHECKS:\n")
        for item in validation_results['failed']:
            f.write(f"  ✗ {item}\n")
        f.write("\n")
    
    if not validation_results['failed']:
        f.write("STATUS: VALIDATION PASSED ✅\n")
        f.write("Ready to proceed to PROMPT 2.5\n")
    else:
        f.write("STATUS: VALIDATION FAILED ❌\n")
        f.write("Fix issues before proceeding\n")

print(f"\nValidation report saved to: {validation_report_path}")
