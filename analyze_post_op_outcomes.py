"""
Analyze post-operative outcome data for TKR patients in OAI dataset
Checks if we have follow-up WOMAC scores after surgery
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Base paths
general_path = Path("data/raw/General_ASCII")
clinical_path = Path("data/raw/AllClinical_ASCII")

print("=" * 80)
print("POST-OPERATIVE OUTCOME ANALYSIS")
print("=" * 80)

# Step 1: Load Outcomes99.txt and identify surgery patients
print("\n1. Loading Outcomes99.txt...")
outcomes = pd.read_csv(general_path / "Outcomes99.txt", sep="|", low_memory=False)
print(f"   Total patients in Outcomes99: {len(outcomes)}")

# Standardize ID column
if "id" in outcomes.columns:
    outcomes["ID"] = outcomes["id"].astype(str).str.upper()
elif "ID" in outcomes.columns:
    outcomes["ID"] = outcomes["ID"].astype(str).str.upper()
else:
    raise ValueError("No ID column found in Outcomes99.txt")

# Check actual values in replacement columns
print("\n   Checking replacement status values...")
if "V99ERKRPCF" in outcomes.columns:
    print(f"   Right KR status values: {outcomes['V99ERKRPCF'].value_counts().head()}")
if "V99ELKRPCF" in outcomes.columns:
    print(f"   Left KR status values: {outcomes['V99ELKRPCF'].value_counts().head()}")

# Identify confirmed replacements (exact match for "3: Replacement adjudicated, confirmed")
right_kr_confirmed = (
    outcomes["V99ERKRPCF"].astype(str) == "3: Replacement adjudicated, confirmed"
)
left_kr_confirmed = (
    outcomes["V99ELKRPCF"].astype(str) == "3: Replacement adjudicated, confirmed"
)

print(f"   Right KR confirmed: {right_kr_confirmed.sum()}")
print(f"   Left KR confirmed: {left_kr_confirmed.sum()}")

# Get days to replacement
right_kr_days = pd.to_numeric(outcomes["V99ERKDAYS"], errors="coerce")
left_kr_days = pd.to_numeric(outcomes["V99ELKDAYS"], errors="coerce")

# Create surgery indicator
has_surgery = right_kr_confirmed | left_kr_confirmed

# Get surgery date (earliest if both knees replaced)
surgery_patients = outcomes[has_surgery].copy()

# For each patient, get the earliest surgery date
surgery_days_list = []
for idx, row in surgery_patients.iterrows():
    days_list = []
    if right_kr_confirmed.iloc[idx] and pd.notna(right_kr_days.iloc[idx]):
        days_list.append(right_kr_days.iloc[idx])
    if left_kr_confirmed.iloc[idx] and pd.notna(left_kr_days.iloc[idx]):
        days_list.append(left_kr_days.iloc[idx])

    if days_list:
        surgery_patients.loc[idx, "surgery_days"] = min(days_list)
    else:
        surgery_patients.loc[idx, "surgery_days"] = np.nan

# Filter to patients with valid surgery dates
surgery_patients = surgery_patients[surgery_patients["surgery_days"].notna()].copy()

print(f"   Patients with confirmed TKR: {len(surgery_patients)}")
print(
    f"   Surgery days range: {surgery_patients['surgery_days'].min():.0f} - {surgery_patients['surgery_days'].max():.0f} days"
)

# Step 2: Load baseline WOMAC scores
print("\n2. Loading baseline WOMAC scores (AllClinical00.txt)...")
baseline = pd.read_csv(clinical_path / "AllClinical00.txt", sep="|", low_memory=False)

# Standardize ID
if "ID" in baseline.columns:
    baseline["ID"] = baseline["ID"].astype(str).str.upper()

# Get baseline WOMAC scores (worst knee)
baseline_womac = baseline[["ID", "V00WOMTSR", "V00WOMTSL"]].copy()
# Convert to numeric
baseline_womac["V00WOMTSR"] = pd.to_numeric(
    baseline_womac["V00WOMTSR"], errors="coerce"
)
baseline_womac["V00WOMTSL"] = pd.to_numeric(
    baseline_womac["V00WOMTSL"], errors="coerce"
)
baseline_womac["pre_op_womac"] = baseline_womac[["V00WOMTSR", "V00WOMTSL"]].max(axis=1)

# Merge with surgery patients
surgery_patients = surgery_patients.merge(
    baseline_womac[["ID", "pre_op_womac"]], on="ID", how="left"
)

print(
    f"   Surgery patients with baseline WOMAC: {surgery_patients['pre_op_womac'].notna().sum()}"
)

# Step 3: Load follow-up visits and check post-op data
print("\n3. Loading follow-up visits...")

# Visit files and their approximate months
visit_files = {
    "AllClinical01.txt": 12,  # ~12 months
    "AllClinical02.txt": 18,  # ~18 months
    "AllClinical03.txt": 24,  # ~24 months
    "AllClinical04.txt": 30,  # ~30 months
    "AllClinical05.txt": 36,  # ~36 months
    "AllClinical06.txt": 48,  # ~48 months
    "AllClinical07.txt": 54,  # ~54 months
    "AllClinical08.txt": 60,  # ~60 months
    "AllClinical09.txt": 72,  # ~72 months
    "AllClinical10.txt": 96,  # ~96 months
    "AllClinical11.txt": 108,  # ~108 months
    "AllClinical12.txt": 120,  # ~120 months
    "AllClinical13.txt": 132,  # ~132 months
    "AllClinical14.txt": 144,  # ~144 months
}

post_op_data = []

for filename, visit_months in visit_files.items():
    filepath = clinical_path / filename
    if not filepath.exists():
        print(f"   ⚠️  {filename} not found, skipping...")
        continue

    try:
        visit_df = pd.read_csv(filepath, sep="|", low_memory=False)

        # Standardize ID
        if "ID" in visit_df.columns:
            visit_df["ID"] = visit_df["ID"].astype(str).str.upper()
        else:
            print(f"   ⚠️  No ID column in {filename}, skipping...")
            continue

        # Get WOMAC scores
        womac_cols = [col for col in visit_df.columns if "WOMTS" in col]
        if len(womac_cols) >= 2:
            # Convert to numeric
            for col in womac_cols:
                visit_df[col] = pd.to_numeric(visit_df[col], errors="coerce")
            # Get worst knee WOMAC
            visit_df["womac"] = visit_df[womac_cols].max(axis=1)

            # Merge with surgery patients
            visit_merged = surgery_patients[
                ["ID", "surgery_days", "pre_op_womac"]
            ].merge(
                visit_df[["ID", "womac"]], on="ID", how="inner", suffixes=("", "_visit")
            )

            # Calculate post-op months
            # Approximate: visit_months * 30 days
            visit_days = visit_months * 30
            visit_merged["post_op_months"] = (
                visit_days - visit_merged["surgery_days"]
            ) / 30

            # Keep only visits ≥6 months post-op
            visit_merged = visit_merged[
                (visit_merged["post_op_months"] >= 6) & (visit_merged["womac"].notna())
            ]

            if len(visit_merged) > 0:
                post_op_data.append(visit_merged)
                print(
                    f"   ✅ {filename}: {len(visit_merged)} patients with post-op data (≥6 months)"
                )
    except Exception as e:
        print(f"   ⚠️  Error loading {filename}: {e}")
        continue

# Combine all post-op data
if post_op_data:
    all_post_op = pd.concat(post_op_data, ignore_index=True)

    # For each patient, keep the earliest post-op visit (≥6 months)
    all_post_op = all_post_op.sort_values(["ID", "post_op_months"])
    first_post_op = all_post_op.groupby("ID").first().reset_index()

    print(f"\n   Total unique patients with post-op data: {len(first_post_op)}")

    # Step 4: Calculate improvement
    first_post_op["improvement"] = (
        first_post_op["pre_op_womac"] - first_post_op["womac"]
    )
    first_post_op["favorable_outcome"] = (first_post_op["improvement"] >= 20).astype(
        int
    )

    # Merge back to surgery patients
    surgery_patients = surgery_patients.merge(
        first_post_op[
            ["ID", "womac", "post_op_months", "improvement", "favorable_outcome"]
        ],
        on="ID",
        how="left",
    )
    surgery_patients.rename(columns={"womac": "post_op_womac"}, inplace=True)

    # Step 5: Generate summary
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    n_surgery = len(surgery_patients)
    n_with_post_op = surgery_patients["post_op_womac"].notna().sum()
    n_favorable = surgery_patients["favorable_outcome"].sum()

    print(f"\nN patients with surgery: {n_surgery}")
    print(
        f"N with post-op data (≥6 months): {n_with_post_op} ({n_with_post_op/n_surgery*100:.1f}%)"
    )
    print(
        f"N with favorable outcome (improvement ≥20): {n_favorable} ({n_favorable/n_with_post_op*100:.1f}% of those with data)"
    )

    if n_with_post_op > 0:
        print(f"\nImprovement statistics:")
        print(
            f"  Mean improvement: {surgery_patients['improvement'].mean():.1f} points"
        )
        print(
            f"  Median improvement: {surgery_patients['improvement'].median():.1f} points"
        )
        print(
            f"  Range: {surgery_patients['improvement'].min():.1f} to {surgery_patients['improvement'].max():.1f} points"
        )

    # Feasibility assessment
    print("\n" + "=" * 80)
    print("FEASIBILITY ASSESSMENT")
    print("=" * 80)

    # Criteria
    min_patients = 120
    min_favorable_pct = 50
    min_epv = 15

    # Estimate EPV (assuming ~10 predictors)
    n_predictors = 10
    n_events = n_favorable
    epv_ratio = n_events / n_predictors if n_predictors > 0 else 0

    feasible = (
        n_with_post_op >= min_patients
        and (n_favorable / n_with_post_op * 100) >= min_favorable_pct
        and epv_ratio >= min_epv
    )

    print(f"\nCriteria:")
    print(
        f"  ✅ Patients with post-op data ≥ {min_patients}: {n_with_post_op} {'✅' if n_with_post_op >= min_patients else '❌'}"
    )
    print(
        f"  ✅ Favorable outcome % ≥ {min_favorable_pct}%: {n_favorable/n_with_post_op*100:.1f}% {'✅' if (n_favorable/n_with_post_op*100) >= min_favorable_pct else '❌'}"
    )
    print(
        f"  ✅ EPV ratio ≥ {min_epv}: {epv_ratio:.2f} {'✅' if epv_ratio >= min_epv else '❌'}"
    )

    print(
        f"\n🎯 Feasibility for outcome prediction model: {'✅ YES' if feasible else '❌ NO'}"
    )

    # Save results
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)

    # Save surgery patients with outcomes
    output_cols = [
        "ID",
        "surgery_days",
        "pre_op_womac",
        "post_op_womac",
        "post_op_months",
        "improvement",
        "favorable_outcome",
    ]
    surgery_patients[output_cols].to_csv(
        "surgery_patients_with_outcomes.csv", index=False
    )
    print(
        f"✅ Saved: surgery_patients_with_outcomes.csv ({len(surgery_patients)} rows)"
    )

    # Save summary statistics
    with open("summary_statistics.txt", "w") as f:
        f.write("POST-OPERATIVE OUTCOME ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"N patients with surgery: {n_surgery}\n")
        f.write(
            f"N with post-op data (≥6 months): {n_with_post_op} ({n_with_post_op/n_surgery*100:.1f}%)\n"
        )
        f.write(
            f"N with favorable outcome (improvement ≥20): {n_favorable} ({n_favorable/n_with_post_op*100:.1f}% of those with data)\n\n"
        )

        if n_with_post_op > 0:
            f.write(f"Improvement statistics:\n")
            f.write(f"  Mean: {surgery_patients['improvement'].mean():.1f} points\n")
            f.write(
                f"  Median: {surgery_patients['improvement'].median():.1f} points\n"
            )
            f.write(
                f"  Range: {surgery_patients['improvement'].min():.1f} to {surgery_patients['improvement'].max():.1f} points\n\n"
            )

        f.write("Feasibility Criteria:\n")
        f.write(
            f"  Patients with post-op data ≥ {min_patients}: {n_with_post_op} {'✅' if n_with_post_op >= min_patients else '❌'}\n"
        )
        f.write(
            f"  Favorable outcome % ≥ {min_favorable_pct}%: {n_favorable/n_with_post_op*100:.1f}% {'✅' if (n_favorable/n_with_post_op*100) >= min_favorable_pct else '❌'}\n"
        )
        f.write(
            f"  EPV ratio ≥ {min_epv}: {epv_ratio:.2f} {'✅' if epv_ratio >= min_epv else '❌'}\n\n"
        )
        f.write(
            f"Feasibility for outcome prediction model: {'✅ YES' if feasible else '❌ NO'}\n"
        )

    print(f"✅ Saved: summary_statistics.txt")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

else:
    print("\n❌ No post-operative data found in follow-up visits!")
    print("   This may indicate:")
    print("   - Follow-up visits don't have WOMAC scores")
    print("   - Visit timing doesn't align with surgery dates")
    print("   - Data structure is different than expected")
