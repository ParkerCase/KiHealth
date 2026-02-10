#!/usr/bin/env python3
"""
Transfer-learning diabetes prediction for KiHealth patients.

1. Load unified_kihealth.csv (25k+ transfer learning samples)
2. Train a model on diabetes_status (glucose>=126 OR HbA1c>=6.5)
3. Map KiHealth patient CSV to model features
4. Predict diabetes probability for each KiHealth patient

Features:
- Prediabetic tier: A1c 5.7-6.4 → always "Prediabetic" (ADA criteria)
- Glucose imputation: For A1c 5.7-6.4, use median (not ADAG) to avoid over-calling diabetic
- KiHealth-style flags: BMI>=30, HBP, Ins/Cpep ratio, % methylated (see INSULIN_CPEP_RATIO_*)
- Configurable: INSULIN_CPEP_RATIO_MIN/MAX for out-of-range flag (update when C-peptide range known)

Usage:
  python scripts/kihealth_diabetes_prediction.py

Inputs:
  - data/processed/unified_kihealth.csv (transfer learning data)
  - Diabetes-KiHealth/TL-KiHealth/kihealth_patients.csv (KiHealth patients)

Outputs:
  - Diabetes-KiHealth/TL-KiHealth/kihealth_predictions.csv
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.features.homa_calculations import homa_ir, homa_beta

# Paths
UNIFIED_CSV = PROJECT_ROOT / "data" / "processed" / "unified_kihealth.csv"
KIHEALTH_CSV = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "kihealth_patients.csv"
OUTPUT_CSV = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "kihealth_predictions.csv"

# Model features (must match KiHealth mapping)
# c_peptide_ng_ml, ins_cpep_ratio: from C-Pep NHANES (1999-2004) and KiHealth
FEATURE_COLS = [
    "age_years",
    "sex",
    "bmi_kg_m2",
    "glucose_mg_dl",
    "insulin_uU_ml",
    "homa_ir",
    "homa_beta",
    "hba1c_percent",
    "hbp",
    "c_peptide_ng_ml",   # from C-Pep NHANES & KiHealth
    "ins_cpep_ratio",    # Insulin/C-peptide
]

# A1c thresholds (ADA): prediabetes 5.7–6.4, diabetes >= 6.5
A1C_PREDIABETIC_LO = 5.7
A1C_PREDIABETIC_HI = 6.5  # exclusive upper bound: prediab = 5.7 <= a1c < 6.5
A1C_DIABETES = 6.5
GLUCOSE_DIABETES = 126

# Ins/C-peptide ratio: placeholder range (user to provide). Out-of-range = possible insulin resistance.
# Typical fasting: insulin 2-25 μU/mL, c-peptide 0.5-2.0 ng/mL. Ratio ~1-10.
INSULIN_CPEP_RATIO_MIN = 0.5
INSULIN_CPEP_RATIO_MAX = 15.0

# KiHealth column mapping
COL_MAP = {
    "age_years": "Age (as of Aug 2025)",
    "sex": "Gender",
    "bmi_kg_m2": "BMI",
    "glucose_mg_dl": "Glucose (mg/dL)",
    "insulin_uU_ml": "Insulin",
    "hba1c_percent": "A1c",
}


def _parse_pct(s: str) -> float | None:
    """Parse % methylated / % Unmethylated to float."""
    if pd.isna(s) or s == "" or str(s).strip() == "":
        return None
    s = str(s).strip().replace("%", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_num(s: str) -> float | None:
    """Parse numeric string, handle n/a, N/A, etc."""
    if pd.isna(s) or s == "" or str(s).strip() in ("", "n/a", "N/A", "N/A ", "NA"):
        return None
    s = str(s).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _gender_to_sex(g: str) -> float:
    """Map Gender to sex: 0=Female, 1=Male."""
    if pd.isna(g) or str(g).strip() == "":
        return np.nan
    g = str(g).strip().upper()
    if g in ("F", "FEMALE"):
        return 0.0
    if g in ("M", "MALE"):
        return 1.0
    return np.nan


def map_kihealth_to_features(df: pd.DataFrame, glu_median: float = 100.0) -> pd.DataFrame:
    """
    Map KiHealth columns to unified schema features.

    Glucose imputation:
    - If glucose present: use directly.
    - If missing and A1c in prediabetic range (5.7-6.4): use training median (NOT ADAG).
      Rationale: ADAG would give ~128 mg/dL for A1c 6.1, falsely crossing 126 and over-calling diabetic.
    - If missing and A1c < 5.7 or >= 6.5: use ADAG (28.7 * A1c - 46.7).
    """
    # Handle column name variations
    age_col = next((c for c in df.columns if "Age" in c and "Aug" in c), None) or "Age (as of Aug 2025)"
    glu_col = next((c for c in df.columns if "Glucose" in c and "mg" in c), None) or "Glucose (mg/dL)"
    ins_col = next((c for c in df.columns if c == "Insulin"), None) or "Insulin"
    a1c_col = next((c for c in df.columns if c == "A1c"), None) or "A1c"
    bmi_col = next((c for c in df.columns if c == "BMI"), None) or "BMI"
    sex_col = next((c for c in df.columns if c == "Gender"), None) or "Gender"
    hbp_col = next((c for c in df.columns if c == "HBP"), None) or "HBP"
    cpep_col = next((c for c in df.columns if "C-peptide" in c and "Ratio" not in c), None) or "C-peptide"
    ratio_col = next((c for c in df.columns if "Ins/C-peptide" in c and "Ratio" in c), None) or next((c for c in df.columns if c == "Ins/C-peptide Ratio"), None)
    meth_col = next((c for c in df.columns if "methylated" in c.lower() and "%" in c), None)

    out = pd.DataFrame(index=df.index)
    out["age_years"] = df[age_col].apply(_parse_num) if age_col in df.columns else np.nan
    out["sex"] = df[sex_col].apply(_gender_to_sex) if sex_col in df.columns else np.nan
    out["bmi_kg_m2"] = df[bmi_col].apply(_parse_num) if bmi_col in df.columns else np.nan
    out["insulin_uU_ml"] = df[ins_col].apply(_parse_num) if ins_col in df.columns else np.nan
    out["hba1c_percent"] = df[a1c_col].apply(_parse_num) if a1c_col in df.columns else np.nan

    # HBP: 1=YES, 0=NO
    def _hbp(v):
        if pd.isna(v) or str(v).strip() == "":
            return 0.0
        return 1.0 if str(v).strip().upper() in ("YES", "Y", "1") else 0.0

    out["hbp"] = df[hbp_col].apply(_hbp) if hbp_col in df.columns else 0.0

    # KiHealth: C-peptide (ng/mL), Ins/C-peptide ratio
    out["c_peptide_ng_ml"] = np.nan
    out["ins_cpep_ratio"] = np.nan
    if cpep_col and cpep_col in df.columns:
        out["c_peptide_ng_ml"] = df[cpep_col].apply(_parse_num)
    if ratio_col and ratio_col in df.columns:
        out["ins_cpep_ratio"] = df[ratio_col].apply(_parse_num)
    elif ins_col in df.columns and cpep_col in df.columns:
        ins = df[ins_col].apply(_parse_num)
        cpep = df[cpep_col].apply(_parse_num)
        out["ins_cpep_ratio"] = ins / cpep.replace(0, np.nan)

    out["pct_methylated"] = np.nan
    if meth_col and meth_col in df.columns:
        out["pct_methylated"] = df[meth_col].apply(_parse_pct)

    # Glucose: use direct if available
    glucose_raw = df[glu_col].apply(_parse_num) if glu_col in df.columns else pd.Series([np.nan] * len(df), index=df.index)
    out["glucose_mg_dl"] = glucose_raw
    missing_glu = out["glucose_mg_dl"].isna()
    a1c = out["hba1c_percent"]

    # ADAG for non-prediabetic A1c only
    prediab_range = (a1c >= A1C_PREDIABETIC_LO) & (a1c < A1C_PREDIABETIC_HI)
    adag_ok = missing_glu & a1c.notna() & ~prediab_range
    imputed = 28.7 * a1c - 46.7
    out.loc[adag_ok, "glucose_mg_dl"] = imputed[adag_ok]

    # Prediabetic A1c + missing glucose: use median (avoids over-calling diabetic)
    out.loc[missing_glu & prediab_range, "glucose_mg_dl"] = glu_median

    # HOMA-IR, HOMA-beta
    out["homa_ir"] = np.nan
    out["homa_beta"] = np.nan
    valid = (out["glucose_mg_dl"].notna()) & (out["glucose_mg_dl"] > 0) & (out["insulin_uU_ml"].notna()) & (out["insulin_uU_ml"] > 0)
    out.loc[valid, "homa_ir"] = homa_ir(out.loc[valid, "glucose_mg_dl"], out.loc[valid, "insulin_uU_ml"])
    out.loc[valid & (out["glucose_mg_dl"] > 63), "homa_beta"] = homa_beta(
        out.loc[valid & (out["glucose_mg_dl"] > 63), "glucose_mg_dl"],
        out.loc[valid & (out["glucose_mg_dl"] > 63), "insulin_uU_ml"],
    )

    return out


def main() -> None:
    # 1. Load transfer learning data
    if not UNIFIED_CSV.exists():
        print(f"ERROR: {UNIFIED_CSV} not found. Extract from M1 package or run build_unified_kihealth().")
        sys.exit(1)

    unified = pd.read_csv(UNIFIED_CSV, low_memory=False)
    # Use HOMA-eligible rows for training (NHANES + CHNS with valid fasting glucose/insulin)
    train_mask = (
        unified["homa_analysis_eligible"].fillna(False)
        & ~unified["invalid_homa_flag"].fillna(True)
        & unified["glucose_mg_dl"].notna()
        & (unified["glucose_mg_dl"] > 0)
        & unified["insulin_uU_ml"].notna()
        & (unified["insulin_uU_ml"] > 0)
    )
    train_df = unified[train_mask].copy()
    print(f"Transfer learning training samples: {len(train_df):,} (HOMA-eligible)")

    # 2. Prepare features for training (add hbp: derive from BP when available, else 0)
    hbp_train = (
        ((train_df["bp_systolic_mmHg"] >= 130) | (train_df["bp_diastolic_mmHg"] >= 80))
        .fillna(False).astype(float)
    )
    train_df = train_df.copy()
    train_df["hbp"] = hbp_train

    X_train = train_df[[c for c in FEATURE_COLS if c in train_df.columns]].copy()
    if "hbp" not in X_train.columns:
        X_train["hbp"] = 0.0
    for c in FEATURE_COLS:
        if c not in X_train.columns:
            X_train[c] = 0.0
    X_train = X_train[FEATURE_COLS]
    y_train = train_df["diabetes_status"]

    # Impute missing values for training
    for c in X_train.columns:
        if X_train[c].isna().any():
            X_train[c] = X_train[c].fillna(X_train[c].median())

    glu_median = float(X_train["glucose_mg_dl"].median())

    # 3. Train model
    try:
        import xgboost as xgb
        model = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42, use_label_encoder=False, eval_metric="logloss")
    except ImportError:
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)

    model.fit(X_train, y_train)

    # 4. Load KiHealth patients
    if not KIHEALTH_CSV.exists():
        print(f"ERROR: {KIHEALTH_CSV} not found. Run tsv_to_csv first.")
        sys.exit(1)

    kihealth = pd.read_csv(KIHEALTH_CSV)
    print(f"KiHealth patients (total): {len(kihealth)}")

    # Filter: include only patients with at least A1c OR insulin (exclude those with neither)
    a1c_col = next((c for c in kihealth.columns if c == "A1c"), None)
    ins_col = next((c for c in kihealth.columns if c == "Insulin"), None) or "Insulin"
    glu_col = next((c for c in kihealth.columns if "Glucose" in c and "mg" in c), None) or "Glucose (mg/dL)"

    def _has_val(s):
        if pd.isna(s) or s == "" or str(s).strip() in ("", "n/a", "N/A", "NA"):
            return False
        try:
            float(str(s).replace("%", "").replace(",", ""))
            return True
        except ValueError:
            return False

    has_a1c = kihealth[a1c_col].apply(_has_val) if a1c_col else pd.Series(False, index=kihealth.index)
    has_insulin = kihealth[ins_col].apply(_has_val) if ins_col in kihealth.columns else pd.Series(False, index=kihealth.index)
    has_glucose = kihealth[glu_col].apply(_has_val) if glu_col in kihealth.columns else pd.Series(False, index=kihealth.index)
    eligible = has_a1c | has_insulin | has_glucose  # at least one biomarker

    n_excluded = (~eligible).sum()
    kihealth = kihealth[eligible].reset_index(drop=True)
    print(f"Eligible (has A1c, Insulin, or Glucose): {len(kihealth)}")
    print(f"  - With A1c: {has_a1c[eligible].sum()}")
    print(f"  - With Insulin: {has_insulin[eligible].sum()}")
    print(f"  - Excluded (no A1c/Insulin/Glucose): {n_excluded}")

    if len(kihealth) == 0:
        print("ERROR: No patients with A1c, Insulin, or Glucose. Nothing to predict.")
        sys.exit(1)

    # 5. Map KiHealth to features (pass glu_median for prediabetic A1c imputation)
    X_kihealth = map_kihealth_to_features(kihealth, glu_median=glu_median)

    # Impute missing with training medians
    medians = X_train.median()
    for c in FEATURE_COLS:
        if c in X_kihealth.columns:
            X_kihealth[c] = pd.to_numeric(X_kihealth[c], errors="coerce").fillna(medians.get(c, np.nan))

    # Ensure all feature cols exist
    for c in FEATURE_COLS:
        if c not in X_kihealth.columns:
            X_kihealth[c] = medians.get(c, 0)

    X_pred = X_kihealth[FEATURE_COLS]

    # 6. Predict
    proba = model.predict_proba(X_pred)[:, 1]
    pred_class = (proba >= 0.5).astype(int)

    # 7. Build output with prediabetic tier and KiHealth-style flags
    out = kihealth.copy()
    out["predicted_diabetes_status"] = pred_class

    a1c = X_kihealth["hba1c_percent"]
    bmi = X_kihealth["bmi_kg_m2"]
    hbp = X_kihealth["hbp"]
    ins_cpep = X_kihealth.get("ins_cpep_ratio", pd.Series([np.nan] * len(out), index=out.index))
    pct_meth = X_kihealth.get("pct_methylated", pd.Series([np.nan] * len(out), index=out.index))

    # Prediabetic tier: ADA criteria take precedence over model.
    # Diabetic: A1c >= 6.5 OR fasting glucose >= 126 (never Prediabetic)
    # Prediabetic: A1c 5.7-6.4 (do NOT use model to override; model can over-call in this range)
    # Non-diabetic: A1c < 5.7, use model for borderline cases
    glu_col = next((c for c in kihealth.columns if "Glucose" in c and "mg" in c), None)
    actual_glu = kihealth[glu_col].apply(_parse_num) if glu_col else pd.Series([np.nan] * len(kihealth))
    diabetic_by_criteria = (a1c >= A1C_DIABETES) | ((actual_glu >= GLUCOSE_DIABETES) & actual_glu.notna())
    prediab_range = (a1c >= A1C_PREDIABETIC_LO) & (a1c < A1C_PREDIABETIC_HI)

    def _label(i: int) -> str:
        if diabetic_by_criteria.iloc[i]:
            return "Diabetic"
        if prediab_range.iloc[i]:
            return "Prediabetic"  # A1c 5.7-6.4: always Prediabetic, never let model override
        return "Diabetic" if pred_class[i] == 1 else "Non-diabetic"

    out["predicted_diabetes_label"] = [_label(i) for i in range(len(out))]

    # predicted_diabetes_risk_pct: 0-100 scale. Only meaningful for Non-diabetic (model output).
    # For Diabetic: 99.9 (lab-confirmed). For Prediabetic: — (label from ADA, model P(diabetes) is low)
    risk_pct = np.round(proba * 100, 4)
    labels = out["predicted_diabetes_label"]
    risk_pct = np.where(labels == "Diabetic", 99.9, risk_pct)
    risk_pct = np.where(labels == "Prediabetic", np.nan, risk_pct)
    out["predicted_diabetes_risk_pct"] = risk_pct

    # KiHealth at-risk flags (BMI>=30, HBP, Ins/Cpep out of range, % methylated placeholder)
    def _kihealth_flags(i: int) -> str:
        flags = []
        if bmi.iloc[i] >= 30 and pd.notna(bmi.iloc[i]):
            flags.append("BMI>=30")
        if hbp.iloc[i] == 1:
            flags.append("HBP")
        if A1C_PREDIABETIC_LO <= a1c.iloc[i] < A1C_PREDIABETIC_HI:
            flags.append("A1c_5.7-6.4")
        r = ins_cpep.iloc[i]
        if pd.notna(r) and (r < INSULIN_CPEP_RATIO_MIN or r > INSULIN_CPEP_RATIO_MAX):
            flags.append("Ins/Cpep_OOR")
        # % methylated: add when user provides range
        if pd.notna(pct_meth.iloc[i]):
            flags.append(f"pct_methylated={pct_meth.iloc[i]:.1f}")
        return "; ".join(flags) if flags else ""

    out["kihealth_at_risk_flags"] = [_kihealth_flags(i) for i in range(len(out))]

    # Risk tier: from PIPELINE MODEL only (not KiHealth flags). Direct mapping of pipeline result.
    def risk_tier(i: int) -> str:
        label = out["predicted_diabetes_label"].iloc[i]
        p = proba[i]
        if label == "Diabetic":
            return "High risk"
        if label == "Prediabetic":
            return "Moderate risk"
        # Non-diabetic: use model probability for tier
        if p >= 0.25:
            return "Elevated (model)"
        return "Low risk"

    out["risk_tier"] = [risk_tier(i) for i in range(len(out))]

    # Save
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)
    print(f"Predictions saved to {OUTPUT_CSV}")

    # Summary
    print("\nPrediction summary:")
    print(out["predicted_diabetes_label"].value_counts().to_string())
    print("\nRisk tier distribution:")
    print(out["risk_tier"].value_counts().to_string())


if __name__ == "__main__":
    main()
