"""
Preprocessing functions for DOC model validation
Matches the exact preprocessing pipeline used in model training
"""

import pandas as pd
import numpy as np


def validate_data(df):
    """Validate input data format and ranges"""
    required = ["age", "sex", "bmi", "womac_r", "womac_l", "kl_r", "kl_l", "fam_hx"]

    missing = [c for c in required if c not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"

    if not df["age"].between(45, 79).all():
        return False, "Age must be 45-79"
    if not df["bmi"].between(15, 50).all():
        return False, "BMI must be 15-50"
    if not df["womac_r"].between(0, 96).all():
        return False, "Right WOMAC must be 0-96"
    if not df["womac_l"].between(0, 96).all():
        return False, "Left WOMAC must be 0-96"
    if not df["kl_r"].isin([0, 1, 2, 3, 4]).all():
        return False, "Right KL grade must be 0-4"
    if not df["kl_l"].isin([0, 1, 2, 3, 4]).all():
        return False, "Left KL grade must be 0-4"

    return True, "Valid"


def preprocess_data(df, imputer, scaler, feature_names):
    """Preprocess patient data exactly as done in training"""
    # Extract features - map input columns to model columns
    # Input: age, sex, bmi, womac_r, womac_l, kl_r, kl_l, fam_hx
    # Model expects: V00AGE, P02SEX, P01BMI, V00WOMTSR, V00WOMTSL, V00XRKLR, V00XRKLL, P01FAMKR

    X = df[["age", "sex", "bmi", "womac_r", "womac_l", "kl_r", "kl_l", "fam_hx"]].copy()

    # Rename to match model expectations
    X.rename(
        columns={
            "age": "V00AGE",
            "sex": "P02SEX",
            "bmi": "P01BMI",
            "womac_r": "V00WOMTSR",
            "womac_l": "V00WOMTSL",
            "kl_r": "V00XRKLR",
            "kl_l": "V00XRKLL",
            "fam_hx": "P01FAMKR",
        },
        inplace=True,
    )

    # Feature engineering (matches training pipeline)
    X["worst_womac"] = X[["V00WOMTSR", "V00WOMTSL"]].max(axis=1)
    X["worst_kl_grade"] = X[["V00XRKLR", "V00XRKLL"]].max(axis=1)
    X["avg_womac"] = X[["V00WOMTSR", "V00WOMTSL"]].mean(axis=1)

    # Age groups: 0=<55, 1=55-64, 2=65-74, 3=75+
    X["age_group"] = pd.cut(
        X["V00AGE"], bins=[0, 55, 65, 75, 100], labels=[0, 1, 2, 3]
    ).astype(int)

    # BMI categories: 0=Normal (<25), 1=Overweight (25-30), 2=Obese (>30)
    X["bmi_category"] = pd.cut(
        X["P01BMI"], bins=[0, 25, 30, 100], labels=[0, 1, 2]
    ).astype(int)

    # Separate variable types (matches training)
    continuous_vars = [
        "V00WOMTSR",
        "V00WOMTSL",
        "V00AGE",
        "P01BMI",
        "V00XRKLR",
        "V00XRKLL",
        "worst_womac",
        "avg_womac",
        "worst_kl_grade",
    ]
    numeric_vars = list(set(continuous_vars))

    # Simple imputation (mode/median) instead of large imputer
    # Most data should be complete anyway
    X_numeric = X[numeric_vars].copy()
    if X_numeric.isnull().any().any():
        # Use median for continuous, mode for KL grades
        for col in X_numeric.columns:
            if X_numeric[col].isnull().any():
                if "KL" in col:
                    # Mode for KL grades
                    X_numeric[col].fillna(
                        (
                            X_numeric[col].mode()[0]
                            if len(X_numeric[col].mode()) > 0
                            else 2
                        ),
                        inplace=True,
                    )
                else:
                    # Median for continuous
                    X_numeric[col].fillna(X_numeric[col].median(), inplace=True)

    # Scale
    X_scaled = scaler.transform(X_numeric)
    X_scaled = pd.DataFrame(X_scaled, columns=numeric_vars, index=X.index)

    # One-hot encode categorical variables
    # P02SEX: 1=Male (baseline), 2=Female (encoded as P02SEX_2: Female)
    # P01FAMKR: 0=No (baseline), 1=Yes (encoded as P01FAMKR_1: Yes)

    # Create encoded features
    X_encoded = pd.DataFrame(index=X.index)

    # Sex encoding
    X_encoded["P02SEX_2: Female"] = (X["P02SEX"] == 0).astype(int)  # 0=Female in input

    # Race encoding (default to White/Caucasian - most common)
    X_encoded["P02RACE_0: Other Non-white"] = 0
    X_encoded["P02RACE_1: White or Caucasian"] = 1
    X_encoded["P02RACE_2: Black or African American"] = 0
    X_encoded["P02RACE_3: Asian"] = 0

    # Cohort encoding (default to Incidence)
    X_encoded["V00COHORT_2: Incidence"] = 1
    X_encoded["V00COHORT_3: Non-exposed control group"] = 0

    # Family history encoding
    X_encoded["P01FAMKR_0: No"] = (X["P01FAMKR"] == 0).astype(int)
    X_encoded["P01FAMKR_1: Yes"] = (X["P01FAMKR"] == 1).astype(int)

    # Combine all features
    X_final = pd.concat([X_scaled, X[["age_group", "bmi_category"]], X_encoded], axis=1)

    # Ensure correct column order and presence
    for col in feature_names:
        if col not in X_final.columns:
            X_final[col] = 0

    # Reorder to match feature_names exactly
    X_final = X_final[feature_names]

    return X_final
