"""
Investigate OAI dataset for non-surgical treatment response data
Determine if Model 3 (treatment response prediction) is feasible
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

print("=" * 80)
print("INVESTIGATING NON-SURGICAL TREATMENT DATA IN OAI")
print("=" * 80)

base_path = Path(__file__).parent
data_path = base_path / "data" / "raw"

# Determine correct data directory structure
possible_paths = [
    data_path / "General_ASCII",
    Path("data/raw/General_ASCII"),
    Path("."),
]

general_path = None
for path in possible_paths:
    if path.exists() and (path / "Enrollees.txt").exists():
        general_path = path
        break

if general_path is None:
    # Try to find it
    for path in Path(".").rglob("Enrollees.txt"):
        general_path = path.parent
        break

if general_path is None:
    print("⚠️  Could not find data directory. Trying current directory...")
    general_path = Path(".")

print(f"\nUsing data path: {general_path}")

# Find AllClinical files path first (needed for medication check)
clinical_path = None
for path in possible_paths:
    alt_path = (
        path.parent / "AllClinical_ASCII"
        if "General_ASCII" in str(path)
        else path / "AllClinical_ASCII"
    )
    if alt_path.exists():
        clinical_path = alt_path
        break

if clinical_path is None:
    for path in Path(".").rglob("AllClinical00.txt"):
        clinical_path = path.parent
        break

if clinical_path is None:
    clinical_path = general_path

# ============================================================================
# STEP 1: Explore Medication/Treatment Data
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: EXPLORING MEDICATION/TREATMENT DATA")
print("=" * 80)

# Check what medication files exist
# OAI may not have separate medication files - check if embedded in clinical data
med_patterns = ["meds*.txt", "Med*.txt", "MED*.txt", "*medication*.txt", "*Meds*.txt"]
med_files = []
for pattern in med_patterns:
    med_files.extend(list(general_path.glob(pattern)))
    # Also check subdirectories
    for subdir in general_path.iterdir():
        if subdir.is_dir():
            med_files.extend(list(subdir.glob(pattern)))
    # Check parent directories
    if general_path.parent.exists():
        med_files.extend(list(general_path.parent.glob(pattern)))
        for subdir in general_path.parent.iterdir():
            if subdir.is_dir():
                med_files.extend(list(subdir.glob(pattern)))

med_files = sorted(set(med_files))

# Also check if medication data is in AllClinical files
print("\nChecking AllClinical files for medication variables...")
med_cols_in_clinical = []
all_meds_loaded = None
id_col_med = None

try:
    clinical_sample = pd.read_csv(
        clinical_path / "AllClinical00.txt", sep="|", nrows=5, low_memory=False
    )
    med_cols_in_clinical = [
        c
        for c in clinical_sample.columns
        if any(
            word in c.upper()
            for word in [
                "MED",
                "DRUG",
                "RX",
                "TREAT",
                "THERAPY",
                "INJECT",
                "PAIN",
                "ANALGESIC",
                "NSAID",
            ]
        )
    ]
    if med_cols_in_clinical:
        print(
            f"  ✓ Found {len(med_cols_in_clinical)} medication-related columns in AllClinical files:"
        )
        for col in med_cols_in_clinical[:15]:
            print(f"    - {col}")
        # Load full medication data from AllClinical00
        print("\nLoading medication data from AllClinical00.txt...")
        all_meds_loaded = pd.read_csv(
            clinical_path / "AllClinical00.txt", sep="|", low_memory=False
        )
        if "ID" in all_meds_loaded.columns:
            all_meds_loaded["ID"] = all_meds_loaded["ID"].astype(str).str.upper()
            id_col_med = "ID"
            print(
                f"  ✓ Loaded medication data for {all_meds_loaded['ID'].nunique()} patients"
            )
        else:
            id_col_med = None
            print("  ⚠️  No ID column found")
except Exception as e:
    print(f"  ⚠️  Error checking medication columns: {e}")
    med_cols_in_clinical = []
    all_meds_loaded = None
    id_col_med = None

print(f"\nFound {len(med_files)} medication files:")
for f in med_files[:10]:
    print(f"  - {f.name}")
if len(med_files) > 10:
    print(f"  ... and {len(med_files) - 10} more")

# Load first medication file to see structure
if len(med_files) > 0:
    print("\n" + "=" * 80)
    print("MEDICATION FILE STRUCTURE")
    print("=" * 80)

    try:
        # Try different separators
        for sep in ["|", "\t", ","]:
            try:
                meds00 = pd.read_csv(med_files[0], sep=sep, nrows=10, low_memory=False)
                if len(meds00.columns) > 1:
                    print(f"\nFile: {meds00.name}")
                    print(f"Separator: '{sep}'")
                    print(f"Columns: {len(meds00.columns)}")
                    print(f"Shape: {meds00.shape}")
                    print(f"\nFirst 5 columns: {list(meds00.columns[:5])}")
                    break
            except:
                continue

        # Check for ID column
        id_col = None
        for col in ["ID", "id", "V00ID", "P00ID"]:
            if col in meds00.columns:
                id_col = col
                break

        if id_col:
            print(f"\n✓ ID column found: {id_col}")
        else:
            print("\n⚠️  No standard ID column found")

        # Check medication types
        med_cols = [
            c
            for c in meds00.columns
            if any(
                word in c.upper()
                for word in ["MED", "DRUG", "RX", "TREAT", "THERAPY", "INJECT"]
            )
        ]
        print(f"\nMedication-related columns: {len(med_cols)}")
        for col in med_cols[:20]:
            print(f"  - {col}")

        # Load full medication data
        print("\n" + "=" * 80)
        print("LOADING FULL MEDICATION DATA")
        print("=" * 80)

        try:
            all_meds = pd.read_csv(med_files[0], sep=sep, low_memory=False)
            if id_col:
                unique_patients = all_meds[id_col].nunique()
                print(f"Total patients with medication data: {unique_patients}")
                print(f"Total medication records: {len(all_meds)}")
            else:
                print(f"Total records: {len(all_meds)}")
        except Exception as e:
            print(f"⚠️  Error loading full file: {e}")
            all_meds = None

    except Exception as e:
        print(f"⚠️  Error reading medication file: {e}")
        all_meds = None
        meds00 = None
else:
    print("\n⚠️  No medication files found")
    all_meds = None
    meds00 = None

# ============================================================================
# STEP 2: Check for Symptom Trajectories
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: ANALYZING SYMPTOM TRAJECTORIES OVER TIME")
print("=" * 80)

# Clinical path already determined above
print(f"Using clinical path: {clinical_path}")

# Load clinical data from multiple timepoints
timepoints = {
    "00": ("V00", "Baseline"),
    "01": ("V01", "12 months"),
    "02": ("V02", "18 months"),
    "03": ("V03", "24 months"),
    "04": ("V04", "30 months"),
    "05": ("V05", "36 months"),
    "06": ("V06", "48 months"),
}

womac_data = {}
for file_num, (visit, label) in timepoints.items():
    clinical_file = clinical_path / f"AllClinical{file_num}.txt"
    if clinical_file.exists():
        try:
            print(f"\nLoading AllClinical{file_num}.txt ({label})...")
            df = pd.read_csv(clinical_file, sep="|", low_memory=False)

            # Standardize ID
            if "ID" in df.columns:
                df["ID"] = df["ID"].astype(str).str.upper()
            elif "id" in df.columns:
                df["ID"] = df["id"].astype(str).str.upper()

            # Find WOMAC columns - they have visit prefix (V00, V01, etc.)
            womac_cols = [
                c for c in df.columns if "WOM" in c.upper() and "TS" in c.upper()
            ]
            print(f"  WOMAC columns: {len(womac_cols)}")

            if len(womac_cols) >= 2:
                # Find right and left WOMAC total scores
                womac_r_col = None
                womac_l_col = None

                for col in womac_cols:
                    if "TSR" in col.upper() or (
                        "TS" in col.upper()
                        and "R" in col.upper()
                        and "L" not in col.upper()
                    ):
                        womac_r_col = col
                    elif "TSL" in col.upper() or (
                        "TS" in col.upper() and "L" in col.upper()
                    ):
                        womac_l_col = col

                # If not found, try generic pattern
                if womac_r_col is None or womac_l_col is None:
                    # Look for columns with visit prefix
                    visit_prefix = visit
                    possible_r = [
                        c
                        for c in womac_cols
                        if visit_prefix in c and ("R" in c or "RIGHT" in c.upper())
                    ]
                    possible_l = [
                        c
                        for c in womac_cols
                        if visit_prefix in c and ("L" in c or "LEFT" in c.upper())
                    ]

                    if possible_r:
                        womac_r_col = possible_r[0]
                    if possible_l:
                        womac_l_col = possible_l[0]

                if womac_r_col and womac_l_col:
                    womac_df = df[["ID", womac_r_col, womac_l_col]].copy()
                    # Convert to numeric
                    womac_df[womac_r_col] = pd.to_numeric(
                        womac_df[womac_r_col], errors="coerce"
                    )
                    womac_df[womac_l_col] = pd.to_numeric(
                        womac_df[womac_l_col], errors="coerce"
                    )
                    womac_df["worst_womac"] = womac_df[[womac_r_col, womac_l_col]].max(
                        axis=1
                    )
                    womac_data[visit] = womac_df
                    print(f"  Patients: {df['ID'].nunique()}")
                    print(f"  Mean worst WOMAC: {womac_df['worst_womac'].mean():.1f}")
                else:
                    print(
                        f"  ⚠️  Could not find R/L WOMAC columns. Available: {womac_cols[:5]}"
                    )
        except Exception as e:
            print(f"  ⚠️  Error loading {clinical_file}: {e}")

print(f"\n✓ Loaded WOMAC data from {len(womac_data)} timepoints")

# ============================================================================
# STEP 3: Link Treatment to Outcome
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: CAN WE LINK TREATMENT → OUTCOME?")
print("=" * 80)

# Load surgery outcomes to exclude surgical patients
try:
    outcomes_file = general_path / "Outcomes99.txt"
    if outcomes_file.exists():
        outcomes = pd.read_csv(outcomes_file, sep="|", low_memory=False)

        # Standardize ID
        if "id" in outcomes.columns:
            outcomes["ID"] = outcomes["id"].astype(str).str.upper()
        elif "ID" in outcomes.columns:
            outcomes["ID"] = outcomes["ID"].astype(str).str.upper()

        # Identify patients who had TKR
        right_kr = (
            outcomes["V99ERKRPCF"]
            .astype(str)
            .str.contains("3: Replacement adjudicated, confirmed", na=False)
        )
        left_kr = (
            outcomes["V99ELKRPCF"]
            .astype(str)
            .str.contains("3: Replacement adjudicated, confirmed", na=False)
        )
        surgery_patients = set(
            outcomes[(right_kr | left_kr)]["ID"].astype(str).str.upper().unique()
        )

        print(f"Patients with TKR: {len(surgery_patients)}")
    else:
        print("⚠️  Outcomes99.txt not found")
        surgery_patients = set()
except Exception as e:
    print(f"⚠️  Error loading outcomes: {e}")
    surgery_patients = set()

# Filter to non-surgical patients with WOMAC trajectories
if len(womac_data) >= 2 and "V00" in womac_data:
    baseline_ids = set(womac_data["V00"]["ID"].unique())
    non_surgical = baseline_ids - surgery_patients
    print(f"Non-surgical patients with baseline WOMAC: {len(non_surgical)}")

    # Check if we have follow-up WOMAC for non-surgical patients
    if "V03" in womac_data:  # 24 months
        followup_ids = set(womac_data["V03"]["ID"].unique())
        non_surgical_with_followup = non_surgical & followup_ids
        print(
            f"Non-surgical patients with 24-month follow-up: {len(non_surgical_with_followup)}"
        )

        # Calculate symptom change for non-surgical patients
        baseline_womac = womac_data["V00"].set_index("ID")["worst_womac"]
        followup_womac = womac_data["V03"].set_index("ID")["worst_womac"]

        symptom_change = []
        for pid in non_surgical_with_followup:
            pid_str = str(pid).upper()
            if pid_str in baseline_womac.index and pid_str in followup_womac.index:
                baseline_val = baseline_womac[pid_str]
                followup_val = followup_womac[pid_str]
                if pd.notna(baseline_val) and pd.notna(followup_val):
                    change = baseline_val - followup_val  # Positive = improvement
                    symptom_change.append(
                        {
                            "ID": pid_str,
                            "baseline_womac": baseline_val,
                            "followup_womac": followup_val,
                            "womac_change": change,
                            "improved": 1 if change > 0 else 0,
                        }
                    )

        symptom_change_df = pd.DataFrame(symptom_change)
        print(f"\nPatients with calculable symptom change: {len(symptom_change_df)}")
        if len(symptom_change_df) > 0:
            print(
                f"  Mean change: {symptom_change_df['womac_change'].mean():.1f} points"
            )
            print(
                f"  Patients improved: {symptom_change_df['improved'].sum()} ({symptom_change_df['improved'].mean()*100:.1f}%)"
            )

    # Check if we have medication data for these patients
    # Use all_meds_loaded from Step 1 (from AllClinical files)
    if all_meds_loaded is not None and id_col_med:
        meds_ids = set(all_meds_loaded[id_col_med].astype(str).str.upper().unique())
        overlap = non_surgical_with_followup & meds_ids
        print(f"\nNon-surgical patients with medication data: {len(overlap)}")

        # Analyze medication variables
        if len(overlap) > 0 and len(med_cols_in_clinical) > 0:
            print("\nAnalyzing medication variables...")
            available_med_cols = [
                c for c in med_cols_in_clinical if c in all_meds_loaded.columns
            ]
            if available_med_cols:
                med_subset = all_meds_loaded[all_meds_loaded[id_col_med].isin(overlap)][
                    available_med_cols
                ]

                # Count non-missing values
                med_summary = {}
                for col in available_med_cols[:10]:  # Analyze first 10
                    non_missing = med_subset[col].notna().sum()
                    if non_missing > 0:
                        med_summary[col] = non_missing
                        print(
                            f"  {col}: {non_missing} patients ({non_missing/len(overlap)*100:.1f}%)"
                        )

                if len(med_summary) > 0:
                    print(f"\n  ✓ {len(med_summary)} medication variables have data")

        if len(overlap) > 100:
            print("\n✓ SUFFICIENT OVERLAP FOR MODEL 3")
        else:
            print("\n✗ INSUFFICIENT OVERLAP")
    else:
        overlap = set()
        if all_meds_loaded is None:
            print("\n⚠️  Cannot check medication overlap (medication data not loaded)")
        else:
            print("\n⚠️  Cannot check medication overlap (ID column not found)")

else:
    non_surgical = set()
    overlap = set()
    symptom_change_df = pd.DataFrame()
    print("\n⚠️  Insufficient WOMAC trajectory data")

# ============================================================================
# STEP 4: Search for Treatment Intervention Data
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: SEARCHING FOR TREATMENT INTERVENTION DATA")
print("=" * 80)

# Look for treatment-related files
treatment_patterns = [
    "*treatment*.txt",
    "*intervention*.txt",
    "*therapy*.txt",
    "*inject*.txt",
]
treatment_files = []
for pattern in treatment_patterns:
    treatment_files.extend(list(general_path.glob(pattern)))
    for subdir in general_path.iterdir():
        if subdir.is_dir():
            treatment_files.extend(list(subdir.glob(pattern)))

treatment_files = sorted(set(treatment_files))
print(f"\nFound {len(treatment_files)} treatment-related files:")
for f in treatment_files[:10]:
    print(f"  - {f.name}")

# Check enrollment files for treatment variables
enroll_files = sorted(general_path.glob("Enrollees.txt"))
if not enroll_files:
    enroll_files = sorted(general_path.glob("*enroll*.txt"))

for f in enroll_files[:3]:
    try:
        df = pd.read_csv(f, sep="|", nrows=5, low_memory=False)
        treatment_cols = [
            c
            for c in df.columns
            if any(
                word in c.upper()
                for word in [
                    "TREAT",
                    "THERAPY",
                    "INJECT",
                    "EXERCISE",
                    "PHYSICAL",
                    "REHAB",
                ]
            )
        ]
        if treatment_cols:
            print(f"\n{f.name}: {len(treatment_cols)} treatment columns")
            for col in treatment_cols[:10]:
                print(f"  - {col}")
    except:
        pass

# ============================================================================
# STEP 5: Feasibility Assessment
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: MODEL 3 FEASIBILITY ASSESSMENT")
print("=" * 80)

# Determine feasibility criteria
has_treatment_data = (len(med_files) > 0 or len(treatment_files) > 0) or (
    len(med_cols_in_clinical) > 0 and all_meds_loaded is not None
)
has_trajectories = len(womac_data) >= 2
overlap_count = len(overlap) if "overlap" in locals() else 0
can_link = overlap_count > 0
sufficient_size = overlap_count >= 500

feasibility_criteria = {
    "Treatment data available": has_treatment_data,
    "Symptom trajectories available": has_trajectories,
    "Can link treatment → outcome": can_link,
    "Sufficient sample size (>500)": sufficient_size,
    "Multiple treatments to compare": None,  # Requires deeper analysis
}

# Assessment
print("\nCriteria Assessment:")

if feasibility_criteria["Treatment data available"]:
    print("✓ Treatment data: Medication/treatment files available")
else:
    print("✗ Treatment data: Not found")

if feasibility_criteria["Symptom trajectories available"]:
    print(f"✓ Symptom trajectories: WOMAC at {len(womac_data)} timepoints")
else:
    print("✗ Symptom trajectories: Insufficient timepoints")

if feasibility_criteria["Can link treatment → outcome"]:
    print(f"✓ Linkage: {len(overlap)} patients with both treatment + outcome data")
else:
    print("✗ Linkage: Cannot connect treatment to outcomes")

if feasibility_criteria["Sufficient sample size (>500)"]:
    print(f"✓ Sample size: {len(overlap)} patients (adequate)")
elif "overlap" in locals() and len(overlap) > 0:
    print(f"⚠ Sample size: Only {len(overlap)} patients (need 500+)")
else:
    print("✗ Sample size: Unknown or insufficient")

# Multiple treatments - would need detailed medication analysis
print("? Multiple treatments: Requires detailed medication analysis")

# Final verdict
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

met_criteria = sum(1 for v in feasibility_criteria.values() if v == True)
total_criteria = len([v for v in feasibility_criteria.values() if v is not None])

print(f"\nCriteria met: {met_criteria}/{total_criteria}")

if met_criteria >= 4:
    verdict = "✅ MODEL 3 IS FEASIBLE WITH OAI DATA"
    recommendation = "Proceed with treatment response modeling"
elif met_criteria >= 2:
    verdict = "⚠️ MODEL 3 IS PARTIALLY FEASIBLE"
    recommendation = "Consider using Bergman Clinics treatment data instead"
else:
    verdict = "✗ MODEL 3 IS NOT FEASIBLE WITH OAI DATA"
    recommendation = "Requires external treatment registry or Bergman Clinics data"

print(f"\n{verdict}")
print(f"Recommendation: {recommendation}")

# ============================================================================
# STEP 6: Generate Report
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING REPORT")
print("=" * 80)

recommendations = """
## Recommendations for Model 3:

### Option A: OAI Data (if feasible)
- Extract treatment patterns from medication logs
- Calculate WOMAC improvement over 12-24 months
- Compare responders vs non-responders by treatment type
- Challenge: OAI is observational, not randomized

### Option B: Bergman Clinics Data (recommended)
- Request: Patients who tried conservative treatment first
- Data needed: Treatment type, duration, symptom change
- Outcome: WOMAC improvement after 3-6 months
- Sample size target: 500-1000 patients
- Advantage: Real-world clinical data

### Option C: Literature-Based Model
- Systematic review of treatment RCTs
- Meta-analysis of responder characteristics
- Build decision tree from published data
- Advantage: No new data collection needed
- Disadvantage: Less personalized

### Option D: Hybrid Approach
- Use OAI for baseline risk stratification
- Use literature for treatment effect sizes
- Combine into clinical decision support tool
- Validate with Bergman Clinics prospective data
"""

report_md = f"""# Model 3 Feasibility Report - Treatment Response Prediction

**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}  
**Objective:** Determine if OAI dataset has sufficient data to build Model 3 (predicting which conservative treatment works best for each patient)

---

## Executive Summary

**Verdict:** {verdict}  
**Recommendation:** {recommendation}

**Criteria Met:** {met_criteria}/{total_criteria}

---

## Data Assessment

### Treatment Data
- **Medication files found:** {len(med_files)}
- **Treatment files found:** {len(treatment_files)}
- **Status:** {'✓ Available' if feasibility_criteria['Treatment data available'] else '✗ Not found'}

### Symptom Trajectories
- **Timepoints with WOMAC data:** {len(womac_data)}
- **Available visits:** {', '.join(womac_data.keys()) if womac_data else 'None'}
- **Status:** {'✓ Available' if feasibility_criteria['Symptom trajectories available'] else '✗ Insufficient'}

### Treatment-Outcome Linkage
- **Non-surgical patients:** {len(non_surgical) if 'non_surgical' in locals() else 'Unknown'}
- **With treatment data:** {len(overlap) if 'overlap' in locals() else 'Unknown'}
- **With symptom change data:** {len(symptom_change_df) if len(symptom_change_df) > 0 else 'Unknown'}
- **Status:** {'✓ Can link' if feasibility_criteria['Can link treatment → outcome'] else '✗ Cannot link'}

### Sample Size
- **Patients with both treatment + outcome:** {len(overlap) if 'overlap' in locals() else 0}
- **Required:** ≥500 patients
- **Status:** {'✓ Adequate' if feasibility_criteria['Sufficient sample size (>500)'] else '✗ Insufficient' if 'overlap' in locals() and len(overlap) > 0 else '✗ Unknown'}

---

## Detailed Findings

### Medication Data Structure
"""

if meds00 is not None:
    report_md += f"""
- **File format:** {meds00.shape[1]} columns
- **Sample columns:** {', '.join(list(meds00.columns[:5]))}
- **Medication columns found:** {len(med_cols) if 'med_cols' in locals() else 0}
"""
else:
    report_md += "\n- **Status:** Medication files not accessible or not found\n"

report_md += f"""
### Symptom Trajectory Analysis
"""

if len(symptom_change_df) > 0:
    report_md += f"""
- **Patients with baseline + follow-up:** {len(symptom_change_df)}
- **Mean WOMAC change:** {symptom_change_df['womac_change'].mean():.1f} points
- **Patients improved:** {symptom_change_df['improved'].sum()} ({symptom_change_df['improved'].mean()*100:.1f}%)
- **Patients worsened:** {(~symptom_change_df['improved'].astype(bool)).sum()} ({(1-symptom_change_df['improved'].mean())*100:.1f}%)
"""
else:
    report_md += "\n- **Status:** Insufficient trajectory data for analysis\n"

report_md += f"""

---

## Feasibility Criteria

| Criterion | Status | Details |
|-----------|--------|---------|
| Treatment data available | {'✓' if feasibility_criteria['Treatment data available'] else '✗'} | {len(med_files)} medication files found |
| Symptom trajectories available | {'✓' if feasibility_criteria['Symptom trajectories available'] else '✗'} | {len(womac_data)} timepoints with WOMAC data |
| Can link treatment → outcome | {'✓' if feasibility_criteria['Can link treatment → outcome'] else '✗'} | {len(overlap) if 'overlap' in locals() else 0} patients with both |
| Sufficient sample size (>500) | {'✓' if feasibility_criteria['Sufficient sample size (>500)'] else '✗'} | {len(overlap) if 'overlap' in locals() else 0} patients |
| Multiple treatments to compare | ? | Requires detailed medication analysis |

---

## Challenges Identified

1. **Observational Data:** OAI is not a randomized trial, so treatment assignment is not random
2. **Treatment Heterogeneity:** Medication logs may not capture all treatments (injections, PT, etc.)
3. **Confounding:** Patients self-select treatments based on severity, which confounds analysis
4. **Sample Size:** May be insufficient for robust treatment response modeling
5. **Outcome Definition:** Need clear definition of "treatment response" (e.g., ≥20 point WOMAC improvement)

---

{recommendations}

---

## Next Steps

### If OAI Data is Feasible:
1. Extract detailed medication data from all timepoints
2. Classify treatments into categories (NSAIDs, injections, supplements, etc.)
3. Calculate treatment exposure duration
4. Link to symptom trajectories
5. Build treatment response model (responder vs non-responder by treatment type)

### If OAI Data is Not Feasible:
1. **Request Bergman Clinics Data:**
   - Patients who tried conservative treatment first
   - Treatment type, start date, duration
   - WOMAC scores before and after treatment
   - Target: 500-1000 patients

2. **Literature-Based Approach:**
   - Systematic review of treatment RCTs
   - Extract responder characteristics
   - Build decision support tool

3. **Hybrid Approach:**
   - Use OAI for baseline risk prediction
   - Use literature for treatment effect estimates
   - Combine into personalized treatment recommendation

---

**Report Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

with open(base_path / "MODEL3_FEASIBILITY_REPORT.md", "w") as f:
    f.write(report_md)

print("✓ Report saved: MODEL3_FEASIBILITY_REPORT.md")

# Save symptom change data if available
if len(symptom_change_df) > 0:
    symptom_change_df.to_csv(base_path / "symptom_trajectory_analysis.csv", index=False)
    print("✓ Symptom trajectory data saved: symptom_trajectory_analysis.csv")

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
