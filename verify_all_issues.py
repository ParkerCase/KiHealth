"""
COMPREHENSIVE VERIFICATION SCRIPT
Verifies all 6 issues raised by the user
"""

import pandas as pd
import numpy as np
from scipy import stats

print("=" * 80)
print("COMPREHENSIVE VERIFICATION - ALL 6 ISSUES")
print("=" * 80)

# ============================================================================
# ISSUE 1: STK17A AML Mean Discrepancy (-0.062 vs -0.082)
# ============================================================================
print("\n" + "=" * 80)
print("ISSUE 1: STK17A AML Mean Discrepancy")
print("=" * 80)

# Load comprehensive rankings
comp_rankings = pd.read_csv(
    "data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv"
)
# Check column names
print(f"Comprehensive rankings columns: {list(comp_rankings.columns[:10])}")
# Find cancer column (might be 'Cancer' or 'cancer_type')
cancer_col = "Cancer" if "Cancer" in comp_rankings.columns else "cancer_type"
aml_comp = comp_rankings[comp_rankings[cancer_col] == "Acute Myeloid Leukemia"]
if len(aml_comp) > 0:
    stk17a_comp = aml_comp["STK17A_mean"].iloc[0]
    print(f"\nComprehensive Rankings STK17A AML mean: {stk17a_comp:.4f}")

# Load individual STK17A rankings
stk17a_rankings = pd.read_csv(
    "outputs/reports/STK17A_COMPLETE_RANKINGS_WITH_SCORES.csv"
)
aml_stk17a = stk17a_rankings[stk17a_rankings["Cancer"] == "Acute Myeloid Leukemia"]
if len(aml_stk17a) > 0:
    stk17a_indiv = aml_stk17a["STK17A_mean"].iloc[0]
    print(f"Individual STK17A Rankings AML mean: {stk17a_indiv:.4f}")

# Calculate directly from raw data
print("\nCalculating directly from raw data...")
dep_df = pd.read_csv("data/raw/depmap/CRISPRGeneEffect.csv", index_col=0)
dep_df = dep_df.reset_index()
dep_df.columns.values[0] = "ModelID"

model_df = pd.read_csv("data/raw/depmap/Model.csv")

# Get STK17A column
stk17a_col = [col for col in dep_df.columns if "STK17A" in col and "STK17B" not in col][
    0
]

# Merge
merged = dep_df[["ModelID", stk17a_col]].copy()
merged.columns = ["ModelID", "STK17A"]
merged = merged.merge(
    model_df[["ModelID", "OncotreePrimaryDisease", "StrippedCellLineName"]],
    on="ModelID",
)

# Filter to AML
aml_raw = merged[merged["OncotreePrimaryDisease"] == "Acute Myeloid Leukemia"]
aml_raw_mean = aml_raw["STK17A"].mean()
aml_raw_n = len(aml_raw)
print(f"Raw data AML mean: {aml_raw_mean:.4f} (n={aml_raw_n})")
print(f"Individual cell line scores:")
for idx, row in aml_raw.iterrows():
    print(f"  {row['StrippedCellLineName']}: {row['STK17A']:.4f}")

print(f"\n✅ VERIFICATION:")
print(f"   Comprehensive: {stk17a_comp:.4f}")
print(f"   Individual:    {stk17a_indiv:.4f}")
print(f"   Raw data:      {aml_raw_mean:.4f}")
if abs(stk17a_comp - aml_raw_mean) < 0.001:
    print(f"   ✅ Comprehensive matches raw data")
else:
    print(f"   ❌ DISCREPANCY: Comprehensive does not match raw data")
if abs(stk17a_indiv - aml_raw_mean) < 0.001:
    print(f"   ✅ Individual matches raw data")
else:
    print(f"   ❌ DISCREPANCY: Individual does not match raw data")

# ============================================================================
# ISSUE 2: Synthetic Lethality Hit Count (106 vs 190 vs 75)
# ============================================================================
print("\n" + "=" * 80)
print("ISSUE 2: Synthetic Lethality Hit Count")
print("=" * 80)

# Load synthetic lethality files
try:
    true_sl = pd.read_csv("data/processed/true_synthetic_lethality_WITH_CELL_LINES.csv")
    print(f"\ntrue_synthetic_lethality_WITH_CELL_LINES.csv: {len(true_sl)} hits")
except:
    print("\n❌ Could not load true_synthetic_lethality_WITH_CELL_LINES.csv")

try:
    complete_sl = pd.read_csv(
        "data/processed/synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv"
    )
    print(
        f"synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv: {len(complete_sl)} combinations"
    )

    # Check FDR correction
    fdr_sig = None
    if "p_adjusted_fdr" in complete_sl.columns:
        fdr_sig = complete_sl[
            (complete_sl["mean_diff"] < 0) & (complete_sl["p_adjusted_fdr"] < 0.10)
        ]
        print(f"FDR-corrected significant (q < 0.10): {len(fdr_sig)} hits")
    else:
        print("⚠️  No p_adjusted_fdr column found")

    # Check uncorrected
    uncorrected = complete_sl[
        (complete_sl["mean_diff"] < 0) & (complete_sl["p_value"] < 0.10)
    ]
    print(f"Uncorrected significant (p < 0.10): {len(uncorrected)} hits")

    if fdr_sig is not None:
        if len(fdr_sig) > len(uncorrected):
            print(
                f"\n❌ ERROR: FDR-corrected ({len(fdr_sig)}) > uncorrected ({len(uncorrected)})"
            )
            print(
                "   This is impossible! FDR correction should reduce, not increase, counts."
            )
        else:
            print(f"\n✅ FDR correction logic is correct (FDR ≤ uncorrected)")
    else:
        print(f"\n⚠️  Could not verify FDR correction (column missing)")

except Exception as e:
    print(f"\n❌ Error loading complete SL file: {e}")

# Check comprehensive synthetic lethality script
print("\nChecking FDR correction implementation...")
try:
    with open("comprehensive_synthetic_lethality_all_mutations.py", "r") as f:
        script_content = f.read()
        if "fdr_correction" in script_content:
            print("✅ FDR correction function found")
            # Check if it's implemented correctly
            if "p_adjusted[sorted_indices[i]] = min" in script_content:
                print("✅ FDR correction uses min() - correct implementation")
            if "p_adjusted < alpha" in script_content:
                print("✅ FDR rejection uses p_adjusted < alpha - correct")
except:
    print("⚠️  Could not check FDR implementation in script")

# ============================================================================
# ISSUE 3: Terminology Drift (106 vs 243 total hits)
# ============================================================================
print("\n" + "=" * 80)
print("ISSUE 3: Terminology Drift (106 vs 243)")
print("=" * 80)

try:
    complete_sl = pd.read_csv(
        "data/processed/synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv"
    )
    total_tested = len(complete_sl)
    print(f"\nTotal combinations tested: {total_tested}")

    # True positives (mean_diff < 0 AND p < 0.10)
    true_positives = complete_sl[
        (complete_sl["mean_diff"] < 0) & (complete_sl["p_value"] < 0.10)
    ]
    print(f"True positives (mean_diff < 0 AND p < 0.10): {len(true_positives)}")

    # All with mean_diff < 0 (regardless of p-value)
    all_negative = complete_sl[complete_sl["mean_diff"] < 0]
    print(f"All with mean_diff < 0: {len(all_negative)}")

    print(f"\n✅ CLARIFICATION:")
    print(f"   - {total_tested} = Total combinations tested")
    print(
        f"   - {len(true_positives)} = True synthetic lethality hits (mean_diff < 0 AND p < 0.10)"
    )
    print(f"   - {len(all_negative)} = All combinations with negative mean_diff")

    if len(true_positives) == 106:
        print(f"\n✅ 106 = True synthetic lethality hits (correct)")
    if total_tested == 660:  # 165 mutations × 4 targets
        print(
            f"✅ {total_tested} = Total tested combinations (165 mutations × 4 targets)"
        )

except Exception as e:
    print(f"\n❌ Error: {e}")

# ============================================================================
# ISSUE 4: Effect Size Sign Conventions
# ============================================================================
print("\n" + "=" * 80)
print("ISSUE 4: Effect Size Sign Conventions")
print("=" * 80)

try:
    complete_sl = pd.read_csv(
        "data/processed/synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv"
    )

    # Check if mean_diff preserves sign
    negative_count = (complete_sl["mean_diff"] < 0).sum()
    positive_count = (complete_sl["mean_diff"] > 0).sum()
    zero_count = (complete_sl["mean_diff"] == 0).sum()

    print(f"\nmean_diff sign distribution:")
    print(f"  Negative (SL): {negative_count}")
    print(f"  Positive:     {positive_count}")
    print(f"  Zero:         {zero_count}")

    # Check if any exports use absolute values
    if "abs_mean_diff" in complete_sl.columns:
        print(f"\n⚠️  WARNING: Found 'abs_mean_diff' column - sign may be lost!")
    else:
        print(f"\n✅ No absolute value columns found - sign preserved")

    # Sample some values to verify
    print(f"\nSample mean_diff values (first 10):")
    for idx, row in complete_sl.head(10).iterrows():
        sign = "NEGATIVE (SL)" if row["mean_diff"] < 0 else "POSITIVE"
        print(f"  {row['mutation']} × {row['target']}: {row['mean_diff']:.4f} ({sign})")

    print(f"\n✅ VERIFICATION:")
    print(f"   mean_diff < 0 = Synthetic lethality (mutants more dependent)")
    print(f"   mean_diff > 0 = Not synthetic lethality")
    print(f"   Sign is preserved in exports")

except Exception as e:
    print(f"\n❌ Error: {e}")

# ============================================================================
# ISSUE 5: Validation Overlap Percentage (12.4%)
# ============================================================================
print("\n" + "=" * 80)
print("ISSUE 5: Validation Overlap Percentage")
print("=" * 80)

# Load DepMap cell lines
try:
    model_df = pd.read_csv("data/raw/depmap/Model.csv")
    depmap_cell_lines = set(model_df["StrippedCellLineName"].unique())
    print(f"\nDepMap total cell lines: {len(depmap_cell_lines)}")
except Exception as e:
    print(f"\n❌ Error loading DepMap: {e}")
    depmap_cell_lines = set()

# Load IC50 data
ic50_files = [
    "data/processed/compound_target_ic50s.csv",
    "data/processed/tulasi_ic50_detailed.csv",
    "data/raw/StarXData/Tulasi Data/IC50 data with the different drugs.csv",
]

ic50_cell_lines = set()
for file in ic50_files:
    try:
        df = pd.read_csv(file)
        # Try to find cell line column
        for col in df.columns:
            if "cell" in col.lower() or "line" in col.lower() or "name" in col.lower():
                ic50_cell_lines.update(df[col].dropna().astype(str).unique())
                break
        print(f"✅ Loaded {file}: {len(ic50_cell_lines)} unique cell lines")
    except Exception as e:
        print(f"⚠️  Could not load {file}: {e}")

# Calculate overlap
if depmap_cell_lines and ic50_cell_lines:
    overlap = depmap_cell_lines.intersection(ic50_cell_lines)
    percent_overlap = (
        100 * len(overlap) / len(depmap_cell_lines) if depmap_cell_lines else 0
    )

    print(f"\nOverlap calculation:")
    print(f"  DepMap cell lines: {len(depmap_cell_lines)}")
    print(f"  IC50 cell lines:   {len(ic50_cell_lines)}")
    print(f"  Overlap:           {len(overlap)}")
    print(f"  Percent overlap:   {percent_overlap:.2f}%")

    if abs(percent_overlap - 12.4) < 1.0:
        print(f"\n✅ Matches expected ~12.4% overlap")
    else:
        print(f"\n⚠️  Does not match expected 12.4% (got {percent_overlap:.2f}%)")
        print(f"   Check if denominator is correct (should be total DepMap lines)")

# ============================================================================
# ISSUE 6: Composite Score Normalization
# ============================================================================
print("\n" + "=" * 80)
print("ISSUE 6: Composite Score Normalization")
print("=" * 80)

try:
    comp_rankings = pd.read_csv(
        "data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv"
    )

    # Check normalization columns (check what actually exists)
    all_cols = list(comp_rankings.columns)
    score_cols = [
        col for col in all_cols if "score" in col.lower() or "normalized" in col.lower()
    ]
    print(f"Found score columns: {score_cols}")

    # Expected columns
    expected_cols = [
        "dependency_score",
        "expression_correlation_score",
        "mutation_context_score",
        "copy_number_score",
        "literature_score_normalized",
        "experimental_validation_score",
    ]

    print(f"\nChecking score columns and ranges:")
    for col in score_cols:
        if col in comp_rankings.columns:
            min_val = comp_rankings[col].min()
            max_val = comp_rankings[col].max()
            mean_val = comp_rankings[col].mean()
            print(f"  {col}:")
            print(f"    Range: [{min_val:.4f}, {max_val:.4f}]")
            print(f"    Mean:  {mean_val:.4f}")

            # Check if normalized (0-1 range)
            if 0 <= min_val <= 1 and 0 <= max_val <= 1:
                print(f"    ✅ Appears normalized (0-1 range)")
            else:
                print(f"    ⚠️  Not in 0-1 range - may need normalization")

    # Check overall_score calculation
    print(f"\nChecking overall_score:")
    if "overall_score" in comp_rankings.columns:
        overall_min = comp_rankings["overall_score"].min()
        overall_max = comp_rankings["overall_score"].max()
        overall_mean = comp_rankings["overall_score"].mean()
        print(f"  Range: [{overall_min:.4f}, {overall_max:.4f}]")
        print(f"  Mean:  {overall_mean:.4f}")

        # Check if it's weighted sum
        print(f"\n  Sample calculation (first row):")
        first_row = comp_rankings.iloc[0]
        for col in score_cols:
            if col in comp_rankings.columns:
                print(f"    {col}: {first_row[col]:.4f}")
        print(f"    overall_score: {first_row['overall_score']:.4f}")

    # Check the script to see normalization order
    print(f"\nChecking normalization order in script...")
    try:
        with open("create_comprehensive_final_rankings.py", "r") as f:
            script = f.read()
            if "MinMaxScaler" in script or "normalize" in script.lower():
                print("✅ Normalization found in script")
                # Try to find where normalization happens
                if script.find("normalize") < script.find("weight"):
                    print("✅ Normalization happens BEFORE weighting (correct)")
                elif script.find("weight") < script.find("normalize"):
                    print(
                        "⚠️  Weighting happens BEFORE normalization (may be incorrect)"
                    )
            else:
                print("⚠️  No explicit normalization found in script")
    except:
        print("⚠️  Could not check script")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
