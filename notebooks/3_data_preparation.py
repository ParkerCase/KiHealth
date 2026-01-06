#!/usr/bin/env python3
"""
Complete Data Preparation for OAI Modeling
100% Verification and Validation at Each Step
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

print("=" * 80)
print("OAI DATA PREPARATION - 100% VERIFICATION")
print("=" * 80)

# ============================================================================
# STEP 1: Load All Source Files
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: Loading Source Files")
print("=" * 80)

# Define base path
base_path = Path(__file__).parent.parent

# Load Enrollees
enrollees = pd.read_csv(
    base_path / "data/raw/General_ASCII/Enrollees.txt", sep="|", low_memory=False
)
print(f"✅ Enrollees: {enrollees.shape}")

# Load AllClinical00
allclinical00 = pd.read_csv(
    base_path / "data/raw/AllClinical_ASCII/AllClinical00.txt",
    sep="|",
    low_memory=False,
)
print(f"✅ AllClinical00: {allclinical00.shape}")

# Load Outcomes99
outcomes = pd.read_csv(
    base_path / "data/raw/General_ASCII/Outcomes99.txt", sep="|", low_memory=False
)
print(f"✅ Outcomes99: {outcomes.shape}")

# Load KL grades from MeasInventory (easier format - one row per patient)
meas_inv = pd.read_csv(
    base_path / "data/raw/General_ASCII/MeasInventory.csv", low_memory=False
)
print(f"✅ MeasInventory: {meas_inv.shape}")

# Load SubjectChar00
subjectchar = pd.read_csv(
    base_path / "data/raw/General_ASCII/SubjectChar00.txt", sep="|", low_memory=False
)
print(f"✅ SubjectChar00: {subjectchar.shape}")

# Verification: Check all have ID columns
print("\n📋 ID Column Verification:")
print(f"  Enrollees: {'ID' in enrollees.columns}")
print(f"  AllClinical00: {'ID' in allclinical00.columns}")
print(f"  Outcomes99: {'id' in outcomes.columns} (lowercase)")
print(f"  MeasInventory: {'id' in meas_inv.columns} (lowercase)")
print(f"  SubjectChar00: {'ID' in subjectchar.columns}")

# ============================================================================
# STEP 2: Standardize ID Columns
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: Standardizing ID Columns")
print("=" * 80)

# Standardize to uppercase 'ID'
if "id" in outcomes.columns:
    outcomes = outcomes.rename(columns={"id": "ID"})
if "id" in meas_inv.columns:
    meas_inv = meas_inv.rename(columns={"id": "ID"})

print("✅ All ID columns standardized to 'ID'")

# Verify unique IDs
print("\n📋 Unique ID Counts:")
print(f"  Enrollees: {enrollees['ID'].nunique()} unique IDs")
print(f"  AllClinical00: {allclinical00['ID'].nunique()} unique IDs")
print(f"  Outcomes99: {outcomes['ID'].nunique()} unique IDs")
print(f"  MeasInventory: {meas_inv['ID'].nunique()} unique IDs")
print(f"  SubjectChar00: {subjectchar['ID'].nunique()} unique IDs")

# ============================================================================
# STEP 3: Define Outcome Variables
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: Defining Outcome Variables")
print("=" * 80)

# Check available knee replacement variables
print("\n📋 Available Knee Replacement Variables:")
kr_vars = [col for col in outcomes.columns if "KRPCF" in col or "KDAYS" in col]
for var in kr_vars:
    print(f"  - {var}")

# Key variables:
# V99ERKRPCF: Right knee replacement confirmed
# V99ELKRPCF: Left knee replacement confirmed
# V99ERKDAYS: Days from baseline to right knee replacement
# V99ELKDAYS: Days from left knee replacement

# Create outcome dataset
outcomes_clean = outcomes[["ID"]].copy()

# Check replacement confirmation status
# Value "3: Replacement adjudicated, confirmed" means replacement occurred
outcomes_clean["right_kr_confirmed"] = (
    outcomes["V99ERKRPCF"].astype(str).str.contains("3: Replacement", na=False)
).astype(int)
outcomes_clean["left_kr_confirmed"] = (
    outcomes["V99ELKRPCF"].astype(str).str.contains("3: Replacement", na=False)
).astype(int)

# Get days to replacement (convert to numeric, handling missing)
outcomes_clean["right_kr_days"] = pd.to_numeric(outcomes["V99ERKDAYS"], errors="coerce")
outcomes_clean["left_kr_days"] = pd.to_numeric(outcomes["V99ELKDAYS"], errors="coerce")

# Create binary outcomes: replacement within 2 years (730 days) or 4 years (1460 days)
outcomes_clean["knee_replacement_2yr"] = (
    (outcomes_clean["right_kr_days"] <= 730) | (outcomes_clean["left_kr_days"] <= 730)
).astype(int)

outcomes_clean["knee_replacement_4yr"] = (
    (outcomes_clean["right_kr_days"] <= 1460) | (outcomes_clean["left_kr_days"] <= 1460)
).astype(int)

# Report event rates
events_2yr = outcomes_clean["knee_replacement_2yr"].sum()
events_4yr = outcomes_clean["knee_replacement_4yr"].sum()
total_patients = len(outcomes_clean)

print(f"\n Outcome Event Rates:")
print(
    f"  Knee replacement within 2 years: {events_2yr} ({events_2yr/total_patients*100:.2f}%)"
)
print(
    f"  Knee replacement within 4 years: {events_4yr} ({events_4yr/total_patients*100:.2f}%)"
)
print(f"  Total patients: {total_patients}")

# ============================================================================
# STEP 4: Select Baseline Predictor Variables
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: Selecting Baseline Predictor Variables")
print("=" * 80)

# From Enrollees - need to check if V00AGE exists or get from SubjectChar
enrollees_vars = ["ID", "P02SEX", "P02RACE", "V00COHORT"]
enrollees_selected = enrollees[enrollees_vars].copy()

# Check if variables exist
print("\n📋 Enrollees Variables:")
for var in enrollees_vars:
    exists = var in enrollees.columns
    print(f"  {'✅' if exists else '❌'} {var}")

# From AllClinical00 - Select MOST IMPORTANT variables only to keep EPV high
# Strategy: Use composite scores and key variables only
womac_vars = [
    "ID",
    "V00WOMTSR",  # WOMAC Total Right (composite - reduces predictors)
    "V00WOMTSL",  # WOMAC Total Left (composite - reduces predictors)
    "V00400MTIM",  # 400m walk time (walking distance measure) - NEW
    # Skip individual pain/stiffness/function to reduce predictor count
]

# Check which exist
allclinical_vars = womac_vars
allclinical_selected = allclinical00[
    [col for col in allclinical_vars if col in allclinical00.columns]
].copy()

print("\n📋 AllClinical00 Variables:")
for var in allclinical_vars:
    exists = var in allclinical00.columns
    print(f"  {'✅' if exists else '❌'} {var}")

# From MeasInventory - KL grades
kl_vars = ["ID", "V00XRKLR", "V00XRKLL"]  # KL grade right, left
kl_selected = meas_inv[[col for col in kl_vars if col in meas_inv.columns]].copy()

# Convert KL grades from string format "2: 2" to numeric
for var in ["V00XRKLR", "V00XRKLL"]:
    if var in kl_selected.columns:
        # Extract numeric part (before the colon)
        kl_selected[var] = kl_selected[var].astype(str).str.split(":").str[0]
        kl_selected[var] = pd.to_numeric(kl_selected[var], errors="coerce")

print("\n📋 KL Grade Variables:")
for var in kl_vars:
    exists = var in meas_inv.columns
    print(f"  {'✅' if exists else '❌'} {var}")

# From SubjectChar00 - select ONLY MOST CRITICAL risk factors to keep EPV high
# Strategy: Use only top 3-4 most important variables
subjectchar_candidates = [
    "ID",
    "P01FAMKR",  # Family history knee OA (key risk factor)
    # Skip others to reduce predictor count for EPV
]

# Get age and BMI from AllClinical00 if available
if "V00AGE" in allclinical00.columns:
    age_var = "V00AGE"
    age_source = allclinical00[["ID", "V00AGE"]]
else:
    age_var = None
    age_source = None

# Get BMI from AllClinical00
if "P01BMI" in allclinical00.columns:
    bmi_source = allclinical00[["ID", "P01BMI"]]
else:
    bmi_source = None

subjectchar_selected = subjectchar[
    [col for col in subjectchar_candidates if col in subjectchar.columns]
].copy()

print("\n📋 SubjectChar00 Variables:")
for var in subjectchar_candidates:
    exists = var in subjectchar.columns
    print(f"  {'✅' if exists else '❌'} {var}")

# ============================================================================
# STEP 5: Merge All Datasets
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: Merging Datasets")
print("=" * 80)

# Start with Enrollees as base
baseline_data = enrollees_selected.copy()
print(f"  Starting with Enrollees: {baseline_data.shape}")

# Merge AllClinical00
baseline_data = baseline_data.merge(
    allclinical_selected, on="ID", how="left", suffixes=("", "_clinical")
)
print(f"  After AllClinical00 merge: {baseline_data.shape}")

# Add age if available from AllClinical00
if age_source is not None:
    baseline_data = baseline_data.merge(
        age_source, on="ID", how="left", suffixes=("", "_age")
    )
    print(f"  After adding age: {baseline_data.shape}")

# Add BMI if available from AllClinical00
if bmi_source is not None:
    baseline_data = baseline_data.merge(
        bmi_source, on="ID", how="left", suffixes=("", "_bmi")
    )
    print(f"  After adding BMI: {baseline_data.shape}")

# Merge KL grades
baseline_data = baseline_data.merge(
    kl_selected, on="ID", how="left", suffixes=("", "_kl")
)
print(f"  After KL grades merge: {baseline_data.shape}")

# Merge SubjectChar00
baseline_data = baseline_data.merge(
    subjectchar_selected, on="ID", how="left", suffixes=("", "_char")
)
print(f"  After SubjectChar00 merge: {baseline_data.shape}")

# Merge outcomes
baseline_data = baseline_data.merge(
    outcomes_clean[["ID", "knee_replacement_2yr", "knee_replacement_4yr"]],
    on="ID",
    how="left",
)
print(f"  After Outcomes merge: {baseline_data.shape}")

# Verification checks
print("\n📋 Merge Verification:")
print(f"  Final dataset rows: {len(baseline_data)}")
print(f"  Expected rows: 4796")
print(f"  ✅ Match: {len(baseline_data) == 4796}")
print(f"  Duplicate IDs: {baseline_data['ID'].duplicated().sum()}")
print(f"  ✅ No duplicates: {baseline_data['ID'].duplicated().sum() == 0}")

# ============================================================================
# STEP 6: Calculate EPV Ratio
# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: Calculating EPV Ratio")
print("=" * 80)

# Count events (using 2-year outcome)
events_2yr = baseline_data["knee_replacement_2yr"].sum()

# Count predictor variables (exclude ID and outcome variables)
predictor_cols = [
    col
    for col in baseline_data.columns
    if col not in ["ID", "knee_replacement_2yr", "knee_replacement_4yr"]
]
n_predictors = len(predictor_cols)

# Calculate EPV
EPV_2yr = events_2yr / n_predictors if n_predictors > 0 else 0

# Also calculate for 4-year outcome
events_4yr = baseline_data["knee_replacement_4yr"].sum()
EPV_4yr = events_4yr / n_predictors if n_predictors > 0 else 0

print(f"\n EPV Calculation (2-year outcome):")
print(f"  Events: {events_2yr}")
print(f"  Predictors: {n_predictors}")
print(f"  EPV Ratio: {EPV_2yr:.2f}")
print(f"  Status: {'✅ PASS' if EPV_2yr >= 15 else '❌ FAIL'} (need ≥15)")

print(f"\n EPV Calculation (4-year outcome):")
print(f"  Events: {events_4yr}")
print(f"  Predictors: {n_predictors}")
print(f"  EPV Ratio: {EPV_4yr:.2f}")
print(f"  Status: {'✅ PASS' if EPV_4yr >= 15 else '❌ FAIL'} (need ≥15)")

# Save EPV report
with open(base_path / "EPV_calculation.txt", "w") as f:
    f.write("EPV RATIO CALCULATION REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"2-Year Outcome:\n")
    f.write(f"  Events: {events_2yr}\n")
    f.write(f"  Predictors: {n_predictors}\n")
    f.write(f"  EPV Ratio: {EPV_2yr:.2f}\n")
    f.write(f"  Status: {'PASS' if EPV_2yr >= 15 else 'FAIL'} (need ≥15)\n\n")
    f.write(f"4-Year Outcome:\n")
    f.write(f"  Events: {events_4yr}\n")
    f.write(f"  Predictors: {n_predictors}\n")
    f.write(f"  EPV Ratio: {EPV_4yr:.2f}\n")
    f.write(f"  Status: {'PASS' if EPV_4yr >= 15 else 'FAIL'} (need ≥15)\n\n")
    f.write(f"\nPredictor Variables ({n_predictors}):\n")
    for i, col in enumerate(predictor_cols, 1):
        f.write(f"  {i}. {col}\n")

print("\n✅ Saved EPV_calculation.txt")

# ============================================================================
# STEP 7: Missing Data Analysis
# ============================================================================
print("\n" + "=" * 80)
print("STEP 7: Missing Data Analysis")
print("=" * 80)

# Calculate missing percentages
missing_data = []
for col in predictor_cols:
    missing_count = baseline_data[col].isna().sum()
    missing_pct = missing_count / len(baseline_data) * 100
    missing_data.append(
        {
            "variable": col,
            "missing_count": missing_count,
            "missing_pct": missing_pct,
        }
    )

missing_df = pd.DataFrame(missing_data).sort_values("missing_pct", ascending=False)

print("\n Missing Data Summary:")
print(f"  Variables with >20% missing: {(missing_df['missing_pct'] > 20).sum()}")
print(f"  Variables with >10% missing: {(missing_df['missing_pct'] > 10).sum()}")
print(f"  Variables with >5% missing: {(missing_df['missing_pct'] > 5).sum()}")

print("\n Top 10 Variables by Missing Data:")
print(missing_df.head(10).to_string(index=False))

# Create missingness heatmap
if len(predictor_cols) > 0:
    # Select top 20 variables by missingness for visualization
    top_missing = missing_df.head(20)["variable"].tolist()
    if len(top_missing) > 0:
        missing_matrix = baseline_data[top_missing].isnull()

        plt.figure(figsize=(12, 8))
        sns.heatmap(
            missing_matrix.T,
            cbar=True,
            yticklabels=True,
            xticklabels=False,
            cmap="viridis_r",
        )
        plt.title("Missing Data Heatmap (Top 20 Variables)", fontsize=14)
        plt.ylabel("Variables", fontsize=12)
        plt.xlabel("Patients", fontsize=12)
        plt.tight_layout()
        plt.savefig(base_path / "missing_data_report.png", dpi=150, bbox_inches="tight")
        print("\n✅ Saved missing_data_report.png")

# ============================================================================
# STEP 8: Data Quality Checks
# ============================================================================
print("\n" + "=" * 80)
print("STEP 8: Data Quality Checks")
print("=" * 80)

quality_issues = []

# Check age range (check both V00AGE and any age column)
age_col = None
for col in ["V00AGE", "age"]:
    if col in baseline_data.columns:
        age_col = col
        break

if age_col:
    age_min = baseline_data[age_col].min()
    age_max = baseline_data[age_col].max()
    age_issues = (baseline_data[age_col] < 45) | (baseline_data[age_col] > 85)
    n_age_issues = age_issues.sum()
    print(f"\n Age Check:")
    print(f"  Range: {age_min:.0f} - {age_max:.0f}")
    print(f"  Values outside 45-85: {n_age_issues}")
    if n_age_issues > 0:
        quality_issues.append(f"Age: {n_age_issues} values outside 45-85 range")

# Check BMI range (check both P01BMI and any BMI column)
bmi_col = None
for col in ["P01BMI", "BMI", "bmi"]:
    if col in baseline_data.columns:
        bmi_col = col
        break

if bmi_col:
    bmi_min = baseline_data[bmi_col].min()
    bmi_max = baseline_data[bmi_col].max()
    bmi_issues = (baseline_data[bmi_col] < 15) | (baseline_data[bmi_col] > 60)
    n_bmi_issues = bmi_issues.sum()
    print(f"\n BMI Check:")
    print(f"  Range: {bmi_min:.1f} - {bmi_max:.1f}")
    print(f"  Values outside 15-60: {n_bmi_issues}")
    if n_bmi_issues > 0:
        quality_issues.append(f"BMI: {n_bmi_issues} values outside 15-60 range")

# Check WOMAC scores (Total scores typically 0-96, but can vary)
womac_checks = {
    "V00WOMTSR": (0, 100, "WOMAC Total Right"),
    "V00WOMTSL": (0, 100, "WOMAC Total Left"),
}

print(f"\n WOMAC Score Checks:")
for var, (min_val, max_val, name) in womac_checks.items():
    if var in baseline_data.columns:
        actual_min = baseline_data[var].min()
        actual_max = baseline_data[var].max()
        issues = (baseline_data[var] < min_val) | (baseline_data[var] > max_val)
        n_issues = issues.sum()
        print(
            f"  {name} ({var}): Range {actual_min:.0f}-{actual_max:.0f} (expected {min_val}-{max_val}), Issues: {n_issues}"
        )
        if n_issues > 0:
            quality_issues.append(
                f"{name}: {n_issues} values outside {min_val}-{max_val} range"
            )

# Check KL grades (should be 0-4) - convert to numeric first
kl_checks = {"V00XRKLR": "KL Grade Right", "V00XRKLL": "KL Grade Left"}
print(f"\n KL Grade Checks:")
for var, name in kl_checks.items():
    if var in baseline_data.columns:
        # Convert to numeric, handling any string values
        kl_numeric = pd.to_numeric(baseline_data[var], errors="coerce")
        actual_min = kl_numeric.min()
        actual_max = kl_numeric.max()
        issues = (kl_numeric < 0) | (kl_numeric > 4)
        n_issues = issues.sum()
        print(
            f"  {name} ({var}): Range {actual_min:.0f}-{actual_max:.0f} (expected 0-4), Issues: {n_issues}"
        )
        if n_issues > 0:
            quality_issues.append(f"{name}: {n_issues} values outside 0-4 range")
        # Update the column to numeric
        baseline_data[var] = kl_numeric

# Summary
print(f"\n Quality Issues Summary:")
if len(quality_issues) == 0:
    print("  ✅ No quality issues detected")
else:
    print(f"  ⚠️ {len(quality_issues)} quality issues found:")
    for issue in quality_issues:
        print(f"    - {issue}")

# ============================================================================
# STEP 9: Create Data Dictionary
# ============================================================================
print("\n" + "=" * 80)
print("STEP 9: Creating Data Dictionary")
print("=" * 80)

# Create comprehensive data dictionary
data_dict = []

# Add all variables
all_vars = ["ID"] + predictor_cols + ["knee_replacement_2yr", "knee_replacement_4yr"]

for var in all_vars:
    if var in baseline_data.columns:
        # Determine source file
        if var in enrollees_selected.columns:
            source = "Enrollees.txt"
        elif var in allclinical_selected.columns:
            source = "AllClinical00.txt"
        elif var in kl_selected.columns:
            source = "MeasInventory.csv"
        elif var in subjectchar_selected.columns:
            source = "SubjectChar00.txt"
        elif var in outcomes_clean.columns:
            source = "Outcomes99.txt"
        else:
            source = "Unknown"

        # Get data type
        dtype = str(baseline_data[var].dtype)

        # Get range
        if baseline_data[var].dtype in [np.int64, np.float64]:
            min_val = baseline_data[var].min()
            max_val = baseline_data[var].max()
            range_str = f"{min_val:.2f} - {max_val:.2f}"
        else:
            unique_vals = baseline_data[var].nunique()
            range_str = f"{unique_vals} unique values"

        # Get missing percentage
        missing_pct = baseline_data[var].isna().sum() / len(baseline_data) * 100

        # Description (simplified - would need full OAI documentation)
        descriptions = {
            "ID": "Patient identifier",
            "V00AGE": "Age at baseline",
            "P02SEX": "Sex",
            "P02RACE": "Race",
            "V00COHORT": "Cohort (Progression vs Incidence)",
            "V00WOMTSR": "WOMAC Total score (Right knee)",
            "V00WOMTSL": "WOMAC Total score (Left knee)",
            "V00XRKLR": "Kellgren-Lawrence grade (Right knee)",
            "V00XRKLL": "Kellgren-Lawrence grade (Left knee)",
            "P01BMI": "Body Mass Index",
            "P01FAMKR": "Family history of knee OA",
            "knee_replacement_2yr": "Knee replacement within 2 years (binary)",
            "knee_replacement_4yr": "Knee replacement within 4 years (binary)",
        }

        description = descriptions.get(var, "See OAI documentation")

        data_dict.append(
            {
                "Variable_Name": var,
                "Source_File": source,
                "Description": description,
                "Data_Type": dtype,
                "Range": range_str,
                "Missing_Pct": f"{missing_pct:.2f}%",
            }
        )

data_dict_df = pd.DataFrame(data_dict)
data_dict_df.to_csv(base_path / "data_dictionary.csv", index=False)
print(f"\n✅ Created data_dictionary.csv with {len(data_dict)} variables")

# ============================================================================
# STEP 10: Save Final Datasets
# ============================================================================
print("\n" + "=" * 80)
print("STEP 10: Saving Final Datasets")
print("=" * 80)

# Save baseline merged (without outcomes)
baseline_merged = baseline_data.drop(
    columns=["knee_replacement_2yr", "knee_replacement_4yr"], errors="ignore"
)
baseline_merged.to_csv(base_path / "data/baseline_merged.csv", index=False)
print(f"✅ Saved data/baseline_merged.csv: {baseline_merged.shape}")

# Save baseline modeling (with outcomes)
baseline_data.to_csv(base_path / "data/baseline_modeling.csv", index=False)
print(f"✅ Saved data/baseline_modeling.csv: {baseline_data.shape}")

# ============================================================================
# FINAL VALIDATION
# ============================================================================
print("\n" + "=" * 80)
print("FINAL VALIDATION CHECKLIST")
print("=" * 80)

validation_results = []

# Check 1: 4,796 rows
check1 = len(baseline_data) == 4796
validation_results.append(("4,796 rows", check1))
print(
    f"  {'✅' if check1 else '❌'} Merged dataset has 4,796 rows: {len(baseline_data)}"
)

# Check 2: No duplicate patients
check2 = baseline_data["ID"].duplicated().sum() == 0
validation_results.append(("No duplicate patients", check2))
print(
    f"  {'✅' if check2 else '❌'} No duplicate patients: {baseline_data['ID'].duplicated().sum()} duplicates"
)

# Check 3: EPV ratio ≥ 15
check3_2yr = EPV_2yr >= 15
check3_4yr = EPV_4yr >= 15
validation_results.append(("EPV ratio ≥ 15 (2yr)", check3_2yr))
validation_results.append(("EPV ratio ≥ 15 (4yr)", check3_4yr))
print(f"  {'✅' if check3_2yr else '❌'} EPV ratio ≥ 15 (2yr): {EPV_2yr:.2f}")
print(f"  {'✅' if check3_4yr else '❌'} EPV ratio ≥ 15 (4yr): {EPV_4yr:.2f}")

# Check 4: <20% missing in critical variables
critical_vars = ["V00WOMTSR", "V00WOMTSL", "V00XRKLR", "V00XRKLL"]
if age_col:
    critical_vars.append(age_col)
if bmi_col:
    critical_vars.append(bmi_col)
critical_missing = []
for var in critical_vars:
    if var in baseline_data.columns:
        missing_pct = baseline_data[var].isna().sum() / len(baseline_data) * 100
        critical_missing.append(missing_pct < 20)
        print(
            f"  {'✅' if missing_pct < 20 else '❌'} {var}: {missing_pct:.1f}% missing"
        )
check4 = all(critical_missing) if critical_missing else False
validation_results.append(("<20% missing in critical variables", check4))

# Check 5: All values within plausible ranges
check5 = len(quality_issues) == 0
validation_results.append(("All values within plausible ranges", check5))
print(
    f"  {'✅' if check5 else '❌'} All values within plausible ranges: {len(quality_issues)} issues"
)

# Check 6: Only baseline (V00) variables
non_baseline = [
    col
    for col in predictor_cols
    if not col.startswith("V00")
    and not col.startswith("P01")
    and not col.startswith("P02")
]
check6 = len(non_baseline) == 0
validation_results.append(("Only baseline variables", check6))
print(
    f"  {'✅' if check6 else '❌'} Only baseline variables: {len(non_baseline)} non-baseline variables found"
)
if non_baseline:
    print(f"    Non-baseline: {non_baseline}")

# Summary
all_passed = all([result[1] for result in validation_results])
print(f"\n{'='*80}")
print(
    f"VALIDATION SUMMARY: {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}"
)
print(f"{'='*80}")

for check_name, passed in validation_results:
    print(f"  {'✅' if passed else '❌'} {check_name}")

print("\n" + "=" * 80)
print("✅ DATA PREPARATION COMPLETE")
print("=" * 80)
