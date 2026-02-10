"""
Merge CHNS 2009 biomarker, demographics, and anthropometry data.

Reads from data/raw/chns/ if present, else Diabetes-KiHealth/TL-KiHealth/CHNS/.
Output: data/raw/chns/chns_2009_merged.csv
Ready for load_chns() in ETL pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Resolve paths: prefer data/raw/chns, fallback to Diabetes-KiHealth/TL-KiHealth/CHNS
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_CHNS = PROJECT_ROOT / "data" / "raw" / "chns"
FALLBACK_CHNS = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "CHNS"
INPUT_DIR = RAW_CHNS if (RAW_CHNS / "biomarker_09.sas7bdat").exists() else FALLBACK_CHNS
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "chns"
OUTPUT_PATH = OUTPUT_DIR / "chns_2009_merged.csv"

print("=" * 70)
print("CHNS 2009 DATA MERGE")
print("=" * 70)
print(f"Input directory: {INPUT_DIR}")
print(f"Output path: {OUTPUT_PATH}")

# ============================================================================
# STEP 1: Load biomarker file (base)
# ============================================================================
print("\n1. Loading biomarker_09.sas7bdat...")
bio = pd.read_sas(INPUT_DIR / "biomarker_09.sas7bdat")
print(f"   Rows: {len(bio)}")
print(f"   Key variables:")
print(f"     - IDind: {bio['IDind'].notna().sum()} non-null")
print(f"     - INS (insulin): {bio['INS'].notna().sum()} non-null, mean={bio['INS'].mean():.2f}")
print(f"     - GLUCOSE_MG: {bio['GLUCOSE_MG'].notna().sum()} non-null, mean={bio['GLUCOSE_MG'].mean():.2f}")
print(f"     - HbA1c: {bio['HbA1c'].notna().sum()} non-null, mean={bio['HbA1c'].mean():.2f}")

# ============================================================================
# STEP 2: Load mast_pub_12 (demographics - age, sex)
# ============================================================================
print("\n2. Loading mast_pub_12.sas7bdat (demographics)...")
mast = pd.read_sas(INPUT_DIR / "mast_pub_12.sas7bdat")
print(f"   Rows: {len(mast)}")
if "Idind" in mast.columns:
    mast = mast.rename(columns={"Idind": "IDind"})
    print("   ✅ Renamed Idind → IDind for merge")
print(f"   Key variables:")
print(f"     - IDind: {mast['IDind'].notna().sum()} non-null")
print(f"     - GENDER: {mast['GENDER'].notna().sum()} non-null")
print(f"     - WEST_DOB_Y: {mast['WEST_DOB_Y'].notna().sum()} non-null")

mast_subset = mast[["IDind", "GENDER", "WEST_DOB_Y"]].copy()

# ============================================================================
# STEP 3: Merge biomarker + mast (age, sex)
# ============================================================================
print("\n3. Merging biomarker + demographics...")
merged = bio.merge(mast_subset, on="IDind", how="left", indicator="_merge_mast")
print(f"   Both matched: {(merged._merge_mast == 'both').sum()}")
print(f"   Left only (no demo): {(merged._merge_mast == 'left_only').sum()}")

# ============================================================================
# STEP 4: Load pexam_00 (anthropometry - height, weight for BMI)
# ============================================================================
print("\n4. Loading pexam_00.sas7bdat (anthropometry)...")
pexam = pd.read_sas(INPUT_DIR / "pexam_00.sas7bdat")
pexam_2009 = pexam[pexam["WAVE"] == 2009].copy()
print(f"   Rows with WAVE=2009: {len(pexam_2009)}")
print(f"   HEIGHT: {pexam_2009['HEIGHT'].notna().sum()} non-null, mean={pexam_2009['HEIGHT'].mean():.2f} cm")
print(f"   WEIGHT: {pexam_2009['WEIGHT'].notna().sum()} non-null, mean={pexam_2009['WEIGHT'].mean():.2f} kg")

# pexam has SYSTOL1, DIASTOL1 (not SYSTOL/DIASTOL)
pexam_cols = ["IDind", "HEIGHT", "WEIGHT"]
if "SYSTOL1" in pexam_2009.columns:
    pexam_cols.append("SYSTOL1")
if "DIASTOL1" in pexam_2009.columns:
    pexam_cols.append("DIASTOL1")
pexam_subset = pexam_2009[[c for c in pexam_cols if c in pexam_2009.columns]].copy()

# ============================================================================
# STEP 5: Merge with anthropometry
# ============================================================================
print("\n5. Merging with anthropometry (height, weight)...")
merged = merged.merge(pexam_subset, on="IDind", how="left", indicator="_merge_pexam")
print(f"   Both matched: {(merged._merge_pexam == 'both').sum()}")
print(f"   Left only (no anthro): {(merged._merge_pexam == 'left_only').sum()}")

# ============================================================================
# STEP 6: Calculate derived variables
# ============================================================================
print("\n6. Calculating derived variables...")
merged["age_years"] = 2009 - merged["WEST_DOB_Y"]
merged["sex"] = merged["GENDER"].map({1: 1, 2: 0})
merged["bmi_kg_m2"] = merged["WEIGHT"] / ((merged["HEIGHT"] / 100) ** 2)
print(f"   Age: mean={merged['age_years'].mean():.1f}, range={merged['age_years'].min():.0f}-{merged['age_years'].max():.0f}")
print(f"   Sex: Male={(merged['sex'] == 1).sum()}, Female={(merged['sex'] == 0).sum()}, Missing={merged['sex'].isna().sum()}")
print(f"   BMI: mean={merged['bmi_kg_m2'].mean():.2f}, missing={merged['bmi_kg_m2'].isna().sum()}")

# Blood pressure: use SYSTOL1, DIASTOL1 if present
merged["bp_systolic_mmHg"] = merged["SYSTOL1"] if "SYSTOL1" in merged.columns else np.nan
merged["bp_diastolic_mmHg"] = merged["DIASTOL1"] if "DIASTOL1" in merged.columns else np.nan

# ============================================================================
# STEP 7: Create unified schema columns
# ============================================================================
print("\n7. Creating unified schema...")
chns_unified = pd.DataFrame({
    "patient_id": "chns_2009_" + merged["IDind"].astype(str),
    "dataset_source": "chns_2009",
    "survey_year": 2009,
    "age_years": merged["age_years"],
    "sex": merged["sex"],
    "bmi_kg_m2": merged["bmi_kg_m2"],
    "glucose_mg_dl": merged["GLUCOSE_MG"],
    "insulin_uU_ml": merged["INS"],
    "hba1c_percent": merged["HbA1c"],
    "bp_systolic_mmHg": merged["bp_systolic_mmHg"],
    "bp_diastolic_mmHg": merged["bp_diastolic_mmHg"],
    "race_ethnicity": "Chinese",
    "education_level": np.nan,
    "pir": np.nan,
    "pregnancies_count": np.nan,
    "diabetes_pedigree_function": np.nan,
    "survey_weight": np.nan,
})
print(f"   Created unified dataframe: {len(chns_unified)} rows, {len(chns_unified.columns)} columns")

# ============================================================================
# STEP 8: Save merged file
# ============================================================================
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
chns_unified.to_csv(OUTPUT_PATH, index=False)
print(f"\n✅ Saved: {OUTPUT_PATH}")
print(f"   Rows: {len(chns_unified)}")

# ============================================================================
# STEP 9: Data quality summary
# ============================================================================
print("\n" + "=" * 70)
print("DATA QUALITY SUMMARY")
print("=" * 70)
for col in ["age_years", "sex", "bmi_kg_m2", "glucose_mg_dl", "insulin_uU_ml", "hba1c_percent"]:
    missing_pct = 100 * chns_unified[col].isna().sum() / len(chns_unified)
    print(f"  {col:25s} {missing_pct:5.1f}% missing")
valid_homa = (
    (chns_unified["glucose_mg_dl"] > 0)
    & chns_unified["glucose_mg_dl"].notna()
    & (chns_unified["insulin_uU_ml"] > 0)
    & chns_unified["insulin_uU_ml"].notna()
)
print(f"\nValid HOMA (glucose>0 AND insulin>0): {valid_homa.sum()} / {len(chns_unified)} ({100 * valid_homa.sum() / len(chns_unified):.1f}%)")
print("\n" + "=" * 70)
print("MERGE COMPLETE ✅")
print("=" * 70)
print("\nNext step: Run build_unified_kihealth() to include CHNS in unified dataset.")
