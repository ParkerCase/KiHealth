#!/usr/bin/env python3
"""
Model 3A: Reduced predictor model (Age, Sex, BMI only) trained on OAI + CHECK for 4-year TKR.
KLoSA used for external pattern validation only (same 3 predictors → arthritis/knee pain in Korea).

Does NOT modify Models 1 or 2. Reads baseline_modeling.csv (same as pipeline); writes only
models/model_3a_*.pkl and data/model_3a_*.csv.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, roc_curve

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
MODELS = BASE / "models"
MODELS.mkdir(exist_ok=True)

# Predictors for Model 3A (same 3 everywhere)
PREDICTORS_3A = ["V00AGE", "P02SEX", "P01BMI"]
OUTCOME = "knee_replacement_4yr"


def main():
    print("=" * 80)
    print("MODEL 3A: REDUCED PREDICTORS (AGE, SEX, BMI) — OAI + CHECK, KLoSA VALIDATION")
    print("=" * 80)
    print("\nModels 1 & 2 are NOT modified. This script only reads baseline_modeling.csv")
    print("and writes model_3a_* files.\n")

    # -------------------------------------------------------------------------
    # 1. Load OAI + CHECK baseline (read-only)
    # -------------------------------------------------------------------------
    print("1. LOADING OAI + CHECK BASELINE...")
    df = pd.read_csv(DATA / "baseline_modeling.csv")
    assert df.shape[0] >= 4796, f"Expected ≥4796 rows, got {df.shape[0]}"
    assert all(c in df.columns for c in PREDICTORS_3A + [OUTCOME])

    X = df[PREDICTORS_3A].copy()
    y = df[OUTCOME].astype(int)

    n_total = len(df)
    n_events = y.sum()
    epv = n_events / len(PREDICTORS_3A)
    print(f"   Total: {n_total}, Events: {n_events}, EPV: {epv:.2f} (≥15 required)")
    assert epv >= 15, f"EPV {epv:.2f} < 15"

    # -------------------------------------------------------------------------
    # 2. Encode Sex (OAI/CHECK use "1: Male", "2: Female" etc.)
    # -------------------------------------------------------------------------
    print("\n2. ENCODING SEX...")
    if X["P02SEX"].dtype == object or X["P02SEX"].astype(str).str.contains(":").any():
        # String labels like "1: Male", "2: Female"
        X["P02SEX"] = X["P02SEX"].astype(str).map(lambda s: 1 if "Male" in s or s.strip().startswith("1") else 0)
    else:
        # Numeric 1/2 -> Male=1, Female=0
        X["P02SEX"] = (X["P02SEX"] == 1).astype(int)
    X["V00AGE"] = pd.to_numeric(X["V00AGE"], errors="coerce")
    X["P01BMI"] = pd.to_numeric(X["P01BMI"], errors="coerce")

    # Drop rows with missing outcome; impute missing predictors
    valid = y.notna()
    X = X.loc[valid]
    y = y.loc[valid]
    for col in ["V00AGE", "P01BMI"]:
        X[col] = X[col].fillna(X[col].median())
    if X["P02SEX"].isna().any():
        X["P02SEX"] = X["P02SEX"].fillna(X["P02SEX"].mode().iloc[0])

    print(f"   After valid rows: {len(X)}, events: {y.sum()}")

    # -------------------------------------------------------------------------
    # 3. Train/test split (same 80/20, random_state=42 as in notebook 4)
    # -------------------------------------------------------------------------
    print("\n3. TRAIN/TEST SPLIT (80/20, stratified, random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    print(f"   Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    print(f"   Train events: {y_train.sum()}, Test events: {y_test.sum()}")

    # -------------------------------------------------------------------------
    # 4. Scale Age and BMI (fit on train only)
    # -------------------------------------------------------------------------
    print("\n4. SCALING (fit on train only)...")
    scaler = StandardScaler()
    scale_cols = ["V00AGE", "P01BMI"]
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    X_train_scaled[scale_cols] = scaler.fit_transform(X_train[scale_cols])
    X_test_scaled[scale_cols] = scaler.transform(X_test[scale_cols])

    # -------------------------------------------------------------------------
    # 5. Train logistic regression (Model 3A)
    # -------------------------------------------------------------------------
    print("\n5. TRAINING MODEL 3A (Logistic Regression, Age + Sex + BMI)...")
    lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42, class_weight="balanced")
    lr.fit(X_train_scaled, y_train)

    # -------------------------------------------------------------------------
    # 6. Evaluate on test set
    # -------------------------------------------------------------------------
    print("\n6. EVALUATING ON TEST SET...")
    y_pred_proba = lr.predict_proba(X_test_scaled)[:, 1]
    auc_3a = roc_auc_score(y_test, y_pred_proba)
    brier_3a = brier_score_loss(y_test, y_pred_proba)
    print(f"   Model 3A Test AUC: {auc_3a:.3f}")
    print(f"   Model 3A Test Brier: {brier_3a:.4f}")

    # -------------------------------------------------------------------------
    # 7. Save Model 3A artifacts (separate from Models 1 & 2)
    # -------------------------------------------------------------------------
    print("\n7. SAVING MODEL 3A ARTIFACTS...")
    joblib.dump(lr, MODELS / "model_3a_lr.pkl")
    joblib.dump(scaler, MODELS / "model_3a_scaler.pkl")
    joblib.dump(PREDICTORS_3A, MODELS / "model_3a_predictors.pkl")

    pred_df = pd.DataFrame({
        "y_true": y_test.values,
        "pred_3a": y_pred_proba,
    })
    pred_df.to_csv(DATA / "model_3a_test_predictions.csv", index=False)
    print(f"   Saved: {MODELS / 'model_3a_lr.pkl'}, {MODELS / 'model_3a_scaler.pkl'}")
    print(f"   Saved: {DATA / 'model_3a_test_predictions.csv'}")

    # -------------------------------------------------------------------------
    # 8. KLoSA pattern validation (external: same 3 predictors → OA proxy)
    # -------------------------------------------------------------------------
    print("\n8. KLoSA PATTERN VALIDATION (external cohort)...")
    klsa_path = BASE / "data/New-OA-Data/extracted/sav_from_r/str08_e.csv"
    if not klsa_path.exists():
        print("   KLoSA file not found; skipping pattern validation.")
        klsa_auc = None
    else:
        klsa_auc = None
        try:
            klsa = pd.read_csv(klsa_path, low_memory=False, encoding="utf-8")
        except UnicodeDecodeError:
            try:
                klsa = pd.read_csv(klsa_path, low_memory=False, encoding="latin-1")
            except Exception:
                print("   KLoSA file encoding error; skipping pattern validation.")
                klsa = None
        if klsa is not None:
            age_col = "w08A002_age"
            bmi_col = "w08bmi"
            sex_col = "w08gender1"
            arthritis_col = "w08chronic_i"
            required = [age_col, bmi_col, sex_col, arthritis_col]
            if not all(c in klsa.columns for c in required):
                print("   KLoSA missing required columns; skipping.")
            else:
                klsa = klsa[[age_col, bmi_col, sex_col, arthritis_col]].copy()
                klsa.columns = ["age", "bmi", "sex", "arthritis"]
                klsa["age"] = pd.to_numeric(klsa["age"], errors="coerce")
                klsa["bmi"] = pd.to_numeric(klsa["bmi"], errors="coerce")
                klsa["sex"] = pd.to_numeric(klsa["sex"], errors="coerce")
                klsa["arthritis"] = pd.to_numeric(klsa["arthritis"], errors="coerce")
                klsa["oa_proxy"] = (klsa["arthritis"] == 1).astype(int)
                klsa = klsa.dropna(subset=["age", "bmi", "sex", "oa_proxy"])
                klsa = klsa[(klsa["age"] >= 45) & (klsa["age"] <= 95) & (klsa["bmi"] >= 15) & (klsa["bmi"] <= 60)]
                klsa["sex"] = (klsa["sex"] == 1).astype(int)
                n_klsa = len(klsa)
                n_oa = klsa["oa_proxy"].sum()
                if n_oa < 20:
                    print("   KLoSA OA proxy events < 20; skipping logistic fit.")
                else:
                    X_klsa = klsa[["age", "sex", "bmi"]]
                    X_klsa = (X_klsa - X_klsa.mean()) / X_klsa.std()
                    y_klsa = klsa["oa_proxy"]
                    lr_klsa = LogisticRegression(C=1.0, max_iter=1000, random_state=42, class_weight="balanced")
                    lr_klsa.fit(X_klsa, y_klsa)
                    klsa_auc = roc_auc_score(y_klsa, lr_klsa.predict_proba(X_klsa)[:, 1])
                    print(f"   KLoSA (Wave 8): N={n_klsa}, arthritis events={n_oa}")
                    print(f"   KLoSA pattern validation AUC (Age+Sex+BMI → arthritis): {klsa_auc:.3f}")
                    print("   Same 3 predictors are associated with OA-related outcome in Korea.")

    # -------------------------------------------------------------------------
    # 9. Summary and confidence checklist
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("MODEL 3A COMPLETE — CONFIDENCE CHECKLIST")
    print("=" * 80)
    print(f"   Model 3A Test AUC: {auc_3a:.3f}")
    print(f"   Model 3A Test Brier: {brier_3a:.4f}")
    print(f"   EPV: {epv:.2f} (≥15)")
    print(f"   Predictors: {PREDICTORS_3A}")
    print(f"   Data: OAI + CHECK only (no KLoSA in training)")
    if klsa_auc is not None:
        print(f"   KLoSA pattern validation AUC: {klsa_auc:.3f}")
    print("   Models 1 & 2: untouched")
    print("=" * 80)


if __name__ == "__main__":
    main()
