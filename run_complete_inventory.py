#!/usr/bin/env python3
"""
Run the complete data inventory notebook as a script
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

# Set display options
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 20)
pd.set_option("display.width", 150)

print("=" * 80)
print("COMPLETE OAI DATA INVENTORY")
print("=" * 80)

# ============================================================================
# 1. AllClinical Dataset Exploration
# ============================================================================
print("\n" + "=" * 80)
print("1. AllClinical Dataset Exploration")
print("=" * 80)

allclinical_files = sorted(glob.glob("data/raw/AllClinical_ASCII/AllClinical*.txt"))
print(f"\nFound {len(allclinical_files)} AllClinical files:")
for f in allclinical_files[:5]:
    print(f"  - {Path(f).name}")
if len(allclinical_files) > 5:
    print(f"  ... and {len(allclinical_files) - 5} more")

# Load baseline
allclinical00 = pd.read_csv(
    "data/raw/AllClinical_ASCII/AllClinical00.txt", sep="|", low_memory=False
)
print(f"\n✅ AllClinical00 loaded: {allclinical00.shape}")

# Find WOMAC variables
womac_vars = [col for col in allclinical00.columns if "WOM" in col.upper()]
print(f"\nWOMAC variables found ({len(womac_vars)}):")
for var in sorted(womac_vars):
    print(f"  - {var}")

# Key WOMAC variables
key_womac = {
    "Pain (Right)": "V00WOMKPR",
    "Pain (Left)": "V00WOMKPL",
    "Stiffness (Right)": "V00WOMSTFR",
    "Stiffness (Left)": "V00WOMSTFL",
    "Function (Right)": "V00WOMADLR",
    "Function (Left)": "V00WOMADLL",
    "Total Score (Right)": "V00WOMTSR",
    "Total Score (Left)": "V00WOMTSL",
}

print("\n📊 Key WOMAC Variables:")
for name, var in key_womac.items():
    if var in allclinical00.columns:
        n_valid = allclinical00[var].notna().sum()
        pct = n_valid / len(allclinical00) * 100
        print(f"  ✅ {name} ({var}): {n_valid} patients ({pct:.1f}%)")
    else:
        print(f"  ❌ {name} ({var}): NOT FOUND")

# Check WOMAC availability
womac_cols = [
    "V00WOMKPR",
    "V00WOMKPL",
    "V00WOMSTFR",
    "V00WOMSTFL",
    "V00WOMADLR",
    "V00WOMADLL",
]
womac_cols = [col for col in womac_cols if col in allclinical00.columns]
if womac_cols:
    has_womac = allclinical00[womac_cols].notna().any(axis=1).sum()
    print(f"\n📊 Baseline WOMAC Data Availability:")
    print(
        f"  - Patients with at least one WOMAC score: {has_womac} ({has_womac/len(allclinical00)*100:.1f}%)"
    )

# Temporal structure
allclinical_data = {}
visit_codes = []
for file_path in allclinical_files:
    filename = Path(file_path).name
    visit_num = (
        filename.replace("AllClinical", "")
        .replace("ALLCLINICAL", "")
        .replace(".txt", "")
    )
    try:
        full_df = pd.read_csv(file_path, sep="|", low_memory=False)
        allclinical_data[visit_num] = {"rows": len(full_df)}
        visit_codes.append(visit_num)
    except Exception as e:
        print(f"Error loading {filename}: {e}")

print(f"\n📅 AllClinical Temporal Structure: {len(allclinical_data)} visits")

# ============================================================================
# 2. Biomarkers Dataset Exploration
# ============================================================================
print("\n" + "=" * 80)
print("2. Biomarkers Dataset Exploration")
print("=" * 80)

biomarker_files = sorted(glob.glob("data/raw/Biomarkers_ASCII/Biomarkers*.txt"))
print(f"\nFound {len(biomarker_files)} Biomarkers files")
biomarkers00 = pd.read_csv(
    "data/raw/Biomarkers_ASCII/Biomarkers00.txt", sep="|", low_memory=False
)
print(f"✅ Biomarkers00 loaded: {biomarkers00.shape}")

if "ID" in biomarkers00.columns:
    biomarker_ids = set(biomarkers00["ID"].dropna())
    print(f"\n📊 Biomarkers Data Availability:")
    print(f"  - Unique patients: {len(biomarker_ids)}")
    print(f"  - % of 4,796 total cohort: {len(biomarker_ids)/4796*100:.1f}%")

# ============================================================================
# 3. X-Ray KL Grade Exploration
# ============================================================================
print("\n" + "=" * 80)
print("3. X-Ray KL Grade Exploration")
print("=" * 80)

xray_sq00 = pd.read_csv(
    "data/raw/X-Ray Image Assessments_ASCII/Semi-Quant Scoring_ASCII/kxr_sq_bu00.txt",
    sep="|",
    low_memory=False,
)
print(f"✅ X-ray Semi-Quant Scoring (baseline) loaded: {xray_sq00.shape}")

if "V00XRKL" in xray_sq00.columns:
    xray_patients = set(xray_sq00["ID"].dropna())
    print(f"\n📊 X-ray KL Grade Data Availability:")
    print(f"  - Unique patients: {len(xray_patients)}")
    print(f"  - % of 4,796 total cohort: {len(xray_patients)/4796*100:.1f}%")
    missing_kl = xray_sq00["V00XRKL"].isna().sum()
    print(f"  - Missing KL grades: {missing_kl} ({missing_kl/len(xray_sq00)*100:.1f}%)")

# ============================================================================
# 4. MeasInventory Exploration
# ============================================================================
print("\n" + "=" * 80)
print("4. MeasInventory Exploration")
print("=" * 80)

meas_inv = pd.read_csv("data/raw/General_ASCII/MeasInventory.csv", low_memory=False)
print(f"✅ MeasInventory loaded: {meas_inv.shape}")

if "id" in meas_inv.columns:
    meas_ids = set(meas_inv["id"].dropna())
    print(f"\n  - Unique patients: {len(meas_ids)}")
    print(f"  - % of 4,796 total cohort: {len(meas_ids)/4796*100:.1f}%")
    if "V00XRKLR" in meas_inv.columns and "V00XRKLL" in meas_inv.columns:
        has_kl_r = meas_inv["V00XRKLR"].notna().sum()
        has_kl_l = meas_inv["V00XRKLL"].notna().sum()
        print(
            f"  - Patients with right knee KL grade: {has_kl_r} ({has_kl_r/len(meas_inv)*100:.1f}%)"
        )
        print(
            f"  - Patients with left knee KL grade: {has_kl_l} ({has_kl_l/len(meas_inv)*100:.1f}%)"
        )

# ============================================================================
# 5. Create Summary Table
# ============================================================================
print("\n" + "=" * 80)
print("5. Creating Summary Table")
print("=" * 80)

summary_data = []

# Enrollees
enrollees = pd.read_csv(
    "data/raw/General_ASCII/Enrollees.txt", sep="|", low_memory=False
)
summary_data.append(
    {
        "Dataset": "Demographics",
        "File": "Enrollees.txt",
        "N_Patients": len(enrollees),
        "Pct_Cohort": 100.0,
        "Key_Variables": "Age, Sex, Race, Cohort",
    }
)

# SubjectChar00
subjectchar = pd.read_csv(
    "data/raw/General_ASCII/SubjectChar00.txt", sep="|", low_memory=False
)
summary_data.append(
    {
        "Dataset": "Baseline Characteristics",
        "File": "SubjectChar00.txt",
        "N_Patients": len(subjectchar),
        "Pct_Cohort": 100.0,
        "Key_Variables": "Risk factors, Activity, Work status",
    }
)

# AllClinical00 - WOMAC
has_womac_count = (
    allclinical00[womac_cols].notna().any(axis=1).sum() if womac_cols else 0
)
summary_data.append(
    {
        "Dataset": "Clinical Scores",
        "File": "AllClinical00.txt",
        "N_Patients": has_womac_count,
        "Pct_Cohort": has_womac_count / 4796 * 100,
        "Key_Variables": "WOMAC, Pain VAS, Physical function",
    }
)

# Outcomes99
outcomes = pd.read_csv(
    "data/raw/General_ASCII/Outcomes99.txt", sep="|", low_memory=False
)
summary_data.append(
    {
        "Dataset": "Outcomes",
        "File": "Outcomes99.txt",
        "N_Patients": len(outcomes),
        "Pct_Cohort": 100.0,
        "Key_Variables": "Knee replacement, Death",
    }
)

# X-ray KL grade
if "V00XRKL" in xray_sq00.columns:
    xray_kl_patients = len(set(xray_sq00["ID"].dropna()))
    summary_data.append(
        {
            "Dataset": "X-ray (KL grade)",
            "File": "kxr_sq_bu00.txt",
            "N_Patients": xray_kl_patients,
            "Pct_Cohort": xray_kl_patients / 4796 * 100,
            "Key_Variables": "Kellgren-Lawrence grade",
        }
    )

# X-ray Alignment
xray_align = pd.read_csv(
    "data/raw/X-Ray Image Assessments_ASCII/Alignment_ASCII/flxr_kneealign_cooke01.txt",
    sep="|",
    low_memory=False,
)
xray_align_patients = len(set(xray_align["ID"].dropna()))
summary_data.append(
    {
        "Dataset": "X-ray (Alignment)",
        "File": "flxr_kneealign_cooke01.txt",
        "N_Patients": xray_align_patients,
        "Pct_Cohort": xray_align_patients / 4796 * 100,
        "Key_Variables": "Knee alignment angles",
    }
)

# Biomarkers
if "ID" in biomarkers00.columns:
    biomarker_patients = len(set(biomarkers00["ID"].dropna()))
    summary_data.append(
        {
            "Dataset": "Biomarkers",
            "File": "Biomarkers00.txt",
            "N_Patients": biomarker_patients,
            "Pct_Cohort": biomarker_patients / 4796 * 100,
            "Key_Variables": "Serum biomarkers",
        }
    )

# Create DataFrame
summary_df = pd.DataFrame(summary_data)
print("\n📊 Data Availability Summary:")
print(summary_df.to_string(index=False))

# Save to CSV
summary_df.to_csv("data_availability_summary.csv", index=False)
print("\n✅ Saved to data_availability_summary.csv")

# ============================================================================
# 6. Create Critical Variables Document
# ============================================================================
print("\n" + "=" * 80)
print("6. Creating Critical Variables Document")
print("=" * 80)

critical_vars_md = """# Critical Variables for OAI Model

This document lists all variables needed for building the predictive model.

## 1. Demographics (Enrollees.txt)
- **ID**: Patient identifier
- **V00AGE**: Age at baseline
- **P02SEX**: Sex
- **P02RACE**: Race
- **V00COHORT**: Cohort (Progression vs Incidence)

## 2. Baseline Characteristics (SubjectChar00.txt)
- **ID**: Patient identifier
- **P01BMI**: BMI
- **P01FAMKR**: Family history of knee OA
- **V00PASE**: Physical activity scale
- **V00WORK7**: Work status

## 3. Clinical Scores (AllClinical00.txt)

### WOMAC Scores
- **V00WOMKPR**: WOMAC Pain (Right knee)
- **V00WOMKPL**: WOMAC Pain (Left knee)
- **V00WOMSTFR**: WOMAC Stiffness (Right knee)
- **V00WOMSTFL**: WOMAC Stiffness (Left knee)
- **V00WOMADLR**: WOMAC Function/ADL (Right knee)
- **V00WOMADLL**: WOMAC Function/ADL (Left knee)
- **V00WOMTSR**: WOMAC Total Score (Right knee)
- **V00WOMTSL**: WOMAC Total Score (Left knee)

### Pain VAS
- **V00KPPNRT**: Pain VAS Right knee (if exists)
- **V00KPPNLT**: Pain VAS Left knee (if exists)

### Physical Function
- **V00WTMWK**: 20m walk time
- **V00CSTIME**: Chair stand time

## 4. X-Ray Assessments

### KL Grades (kxr_sq_bu00.txt)
- **V00XRKL**: Kellgren-Lawrence grade (per knee, per side)
- **ID**: Patient identifier
- **SIDE**: 1=Right, 2=Left

### Alignment (flxr_kneealign_cooke01.txt)
- **V01HKANGLE**: Hip-knee-ankle angle

## 5. Outcomes (Outcomes99.txt)
- **id**: Patient identifier (lowercase)
- **V99ERKBLRP**: Right knee replacement at baseline
- **V99ELKBLRP**: Left knee replacement at baseline
- **V99ERKRPCF**: Right knee replacement confirmed
- **V99ELKRPCF**: Left knee replacement confirmed

## 6. Biomarkers (Biomarkers00.txt)
- **ID**: Patient identifier
- [Biomarker value columns to be determined]

## Data Linkage Notes
- Most datasets use **ID** (uppercase) as patient identifier
- Outcomes99 uses **id** (lowercase) - needs standardization
- X-ray files have **SIDE** column (1=Right, 2=Left)
- Visit codes: V00=baseline, V01=12mo, V02=24mo, etc.
"""

with open("critical_variables.md", "w") as f:
    f.write(critical_vars_md)

print("✅ Created critical_variables.md")

print("\n" + "=" * 80)
print("✅ COMPLETE DATA INVENTORY FINISHED")
print("=" * 80)
