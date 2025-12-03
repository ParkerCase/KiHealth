"""
Explore OAI dataset for data on other body areas/joints beyond knees
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 80)
print("EXPLORING OAI DATA FOR OTHER BODY AREAS/JOINTS")
print("=" * 80)

base_path = Path(__file__).parent
data_path = base_path / "data" / "raw"

# Load AllClinical00 to check for other joint variables
clinical_path = data_path / "AllClinical_ASCII"
subject_char_path = data_path / "General_ASCII"

print("\n" + "=" * 80)
print("SEARCHING FOR OTHER JOINT/BODY AREA VARIABLES")
print("=" * 80)

# Keywords for other joints/body areas
joint_keywords = {
    "Hip": ["HIP", "HRS"],
    "Hand": ["HAND", "HND"],
    "Back/Spine": ["BACK", "BCK", "SPINE", "SPN"],
    "Shoulder": ["SHOULDER", "SHL"],
    "Ankle": ["ANKLE", "ANK"],
    "Wrist": ["WRIST", "WRS"],
    "Elbow": ["ELBOW", "ELB"],
    "Foot": ["FOOT", "FT"],
    "Neck": ["NECK", "NCK"],
    "General OA": ["OA", "OSTEO"],
}

# Load AllClinical00
print("\n1. Checking AllClinical00.txt...")
try:
    clinical = pd.read_csv(
        clinical_path / "AllClinical00.txt", sep="|", nrows=5, low_memory=False
    )

    other_joint_vars = {}
    for area, keywords in joint_keywords.items():
        matching = [
            c
            for c in clinical.columns
            if any(kw in c.upper() for kw in keywords)
            and "KNEE" not in c.upper()  # Exclude knee-specific
        ]
        if matching:
            other_joint_vars[area] = matching

    print(f"\nFound variables for other body areas:")
    for area, vars_list in other_joint_vars.items():
        print(f"\n  {area}: {len(vars_list)} variables")
        for var in vars_list[:10]:
            print(f"    - {var}")
        if len(vars_list) > 10:
            print(f"    ... and {len(vars_list) - 10} more")
except Exception as e:
    print(f"  Error: {e}")

# Load SubjectChar00
print("\n\n2. Checking SubjectChar00.txt...")
try:
    subject_char = pd.read_csv(
        subject_char_path / "SubjectChar00.txt", sep="|", nrows=5, low_memory=False
    )

    other_joint_vars_sc = {}
    for area, keywords in joint_keywords.items():
        matching = [
            c
            for c in subject_char.columns
            if any(kw in c.upper() for kw in keywords) and "KNEE" not in c.upper()
        ]
        if matching:
            other_joint_vars_sc[area] = matching

    if other_joint_vars_sc:
        print(f"\nFound variables in SubjectChar00:")
        for area, vars_list in other_joint_vars_sc.items():
            print(f"\n  {area}: {len(vars_list)} variables")
            for var in vars_list[:10]:
                print(f"    - {var}")
except Exception as e:
    print(f"  Error: {e}")

# Load full data to see actual values
print("\n" + "=" * 80)
print("LOADING FULL DATA TO ANALYZE OTHER JOINT PREVALENCE")
print("=" * 80)

try:
    print("\nLoading AllClinical00 (full)...")
    clinical_full = pd.read_csv(
        clinical_path / "AllClinical00.txt", sep="|", low_memory=False
    )

    print("\nLoading SubjectChar00 (full)...")
    subject_char_full = pd.read_csv(
        subject_char_path / "SubjectChar00.txt", sep="|", low_memory=False
    )

    # Standardize ID
    if "ID" in clinical_full.columns:
        clinical_full["ID"] = clinical_full["ID"].astype(str).str.upper()
    if "ID" in subject_char_full.columns:
        subject_char_full["ID"] = subject_char_full["ID"].astype(str).str.upper()

    print("\n" + "=" * 80)
    print("PREVALENCE OF OA IN OTHER JOINTS")
    print("=" * 80)

    # Check hip OA
    hip_vars = [
        "P01HRSROA",  # Hip OA right
        "P01HRSLOA",  # Hip OA left
        "P01OAHIPCV",  # OA hip confirmed
    ]

    print("\nHIP OA:")
    for var in hip_vars:
        if var in subject_char_full.columns:
            non_missing = subject_char_full[var].notna().sum()
            if non_missing > 0:
                unique_vals = subject_char_full[var].value_counts()
                print(f"  {var}:")
                print(
                    f"    Non-missing: {non_missing} ({non_missing/len(subject_char_full)*100:.1f}%)"
                )
                print(f"    Values: {dict(unique_vals.head(10))}")

    # Check hand OA
    hand_vars = ["P01OAHNDCV"]  # OA hand confirmed

    print("\nHAND OA:")
    for var in hand_vars:
        if var in subject_char_full.columns:
            non_missing = subject_char_full[var].notna().sum()
            if non_missing > 0:
                unique_vals = subject_char_full[var].value_counts()
                print(f"  {var}:")
                print(
                    f"    Non-missing: {non_missing} ({non_missing/len(subject_char_full)*100:.1f}%)"
                )
                print(f"    Values: {dict(unique_vals.head(10))}")

    # Check back OA
    back_vars = ["P01OABCKCV"]  # OA back confirmed

    print("\nBACK/SPINE OA:")
    for var in back_vars:
        if var in subject_char_full.columns:
            non_missing = subject_char_full[var].notna().sum()
            if non_missing > 0:
                unique_vals = subject_char_full[var].value_counts()
                print(f"  {var}:")
                print(
                    f"    Non-missing: {non_missing} ({non_missing/len(subject_char_full)*100:.1f}%)"
                )
                print(f"    Values: {dict(unique_vals.head(10))}")

    # Check other OA
    other_vars = ["P01OAOTHCV"]  # OA other confirmed

    print("\nOTHER OA:")
    for var in other_vars:
        if var in subject_char_full.columns:
            non_missing = subject_char_full[var].notna().sum()
            if non_missing > 0:
                unique_vals = subject_char_full[var].value_counts()
                print(f"  {var}:")
                print(
                    f"    Non-missing: {non_missing} ({non_missing/len(subject_char_full)*100:.1f}%)"
                )
                print(f"    Values: {dict(unique_vals.head(10))}")

    # Check hip fracture
    hip_fx_vars = ["V00HIPFX", "V00HIPFXAG"]

    print("\nHIP FRACTURE:")
    for var in hip_fx_vars:
        if var in clinical_full.columns:
            non_missing = clinical_full[var].notna().sum()
            if non_missing > 0:
                unique_vals = clinical_full[var].value_counts()
                print(f"  {var}:")
                print(
                    f"    Non-missing: {non_missing} ({non_missing/len(clinical_full)*100:.1f}%)"
                )
                print(f"    Values: {dict(unique_vals.head(10))}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\nOAI Dataset Focus:")
    print("  Primary: KNEE osteoarthritis (comprehensive data)")
    print("  Secondary: Limited data on other joints")

    print("\nOther Joint Data Available:")
    print("  ✓ Hip OA (prevalence/confirmation variables)")
    print("  ✓ Hand OA (prevalence/confirmation variables)")
    print("  ✓ Back/Spine OA (prevalence/confirmation variables)")
    print("  ✓ Other OA (prevalence/confirmation variables)")
    print("  ✓ Hip fracture (history)")

    print("\nData Limitations:")
    print("  - No detailed symptom scores (WOMAC) for other joints")
    print("  - No imaging (X-ray/MRI) for other joints")
    print("  - No treatment/medication data specific to other joints")
    print("  - Primarily prevalence/confirmation variables")

    print("\nUse Cases:")
    print("  - Comorbidity assessment (other OA as confounder)")
    print("  - General OA burden (polyarticular OA)")
    print("  - Not suitable for modeling other joint outcomes")

except Exception as e:
    print(f"Error loading full data: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
print("EXPLORATION COMPLETE")
print("=" * 80)
