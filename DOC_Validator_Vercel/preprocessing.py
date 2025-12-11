"""
Preprocessing functions for DOC model validation
Matches the exact preprocessing pipeline used in model training
"""

import pandas as pd
import numpy as np


def vas_to_womac(vas_score, scale="0-10"):
    """
    Convert VAS pain score to approximate WOMAC total score
    Based on literature (Tubach 2005, Salaffi 2003)

    Args:
        vas_score: VAS pain rating
        scale: '0-10' or '0-100'

    Returns:
        Estimated WOMAC total score (0-96)
    """
    if scale == "0-100":
        vas_score = vas_score / 10

    # Linear approximation: WOMAC ≈ 8×VAS + 15
    womac_approx = (vas_score * 8) + 15

    # Clip to valid range
    womac_approx = np.clip(womac_approx, 0, 96)

    return womac_approx


def validate_data(df):
    """Validate input data format and ranges"""
    # Check if we have WOMAC or VAS (all optional now)
    has_womac_r = "womac_r" in df.columns
    has_womac_l = "womac_l" in df.columns
    has_vas_r = "vas_r" in df.columns
    has_vas_l = "vas_l" in df.columns

    # Cannot have both WOMAC and VAS for same knee
    if has_womac_r and has_vas_r:
        return False, "Cannot provide both 'womac_r' and 'vas_r' - use one or the other"
    if has_womac_l and has_vas_l:
        return False, "Cannot provide both 'womac_l' and 'vas_l' - use one or the other"

    required = ["age", "sex", "bmi", "kl_r", "kl_l"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"

    # Family history is optional - will default to 0 (No) if missing

    # Age range expanded to 30-85
    if not df["age"].between(30, 85).all():
        return False, "Age must be 30-85"
    if not df["bmi"].between(15, 50).all():
        return False, "BMI must be 15-50"

    # Validate KL grades - allow NaN/null for "Not available"
    # Convert "na" string to NaN if present
    if "kl_r" in df.columns:
        # Replace "na" string with NaN
        df["kl_r"] = df["kl_r"].replace(["na", "NA", ""], np.nan)
        # Validate non-null values are 0-4
        kl_r_valid = df["kl_r"].isna() | df["kl_r"].isin([0, 1, 2, 3, 4])
        if not kl_r_valid.all():
            return False, "Right KL grade must be 0-4 or 'Not available'"

    if "kl_l" in df.columns:
        # Replace "na" string with NaN
        df["kl_l"] = df["kl_l"].replace(["na", "NA", ""], np.nan)
        # Validate non-null values are 0-4
        kl_l_valid = df["kl_l"].isna() | df["kl_l"].isin([0, 1, 2, 3, 4])
        if not kl_l_valid.all():
            return False, "Left KL grade must be 0-4 or 'Not available'"

    # Check that at least one knee has imaging data (not both NaN)
    if ((df["kl_r"].isna()) & (df["kl_l"].isna())).any():
        return (
            False,
            "At least one knee must have imaging data. Both knees cannot be 'Not available'.",
        )

    # Check that at least one knee has KL ≥ 1 for patients where both KL grades are available
    both_available = (~df["kl_r"].isna()) & (~df["kl_l"].isna())
    if both_available.any():
        if (
            (df.loc[both_available, "kl_r"] == 0)
            & (df.loc[both_available, "kl_l"] == 0)
        ).any():
            return (
                False,
                "At least one knee must have OA findings (KL grade ≥ 1). Both knees cannot be KL grade 0.",
            )

    # Validate WOMAC if provided (now optional)
    if has_womac_r:
        # Only validate non-null values
        womac_r_valid = df["womac_r"].isna() | df["womac_r"].between(0, 96)
        if not womac_r_valid.all():
            return False, "Right WOMAC must be 0-96 (or empty)"
    if has_womac_l:
        womac_l_valid = df["womac_l"].isna() | df["womac_l"].between(0, 96)
        if not womac_l_valid.all():
            return False, "Left WOMAC must be 0-96 (or empty)"

    # Validate VAS if provided (now optional)
    if has_vas_r:
        vas_r_valid = df["vas_r"].isna() | df["vas_r"].between(0, 10)
        if not vas_r_valid.all():
            return False, "Right VAS must be 0-10 (or empty)"
    if has_vas_l:
        vas_l_valid = df["vas_l"].isna() | df["vas_l"].between(0, 10)
        if not vas_l_valid.all():
            return False, "Left VAS must be 0-10 (or empty)"

    return True, "Valid"


def preprocess_data(df, imputer, scaler, feature_names):
    """Preprocess patient data exactly as done in training"""
    # Extract features - map input columns to model columns
    # Input: age, sex, bmi, womac_r, womac_l (or vas_r, vas_l), kl_r, kl_l, fam_hx
    # Model expects: V00AGE, P02SEX, P01BMI, V00WOMTSR, V00WOMTSL, V00XRKLR, V00XRKLL, P01FAMKR

    # Create a copy for processing
    # Family history is optional - default to 0 (No) if missing
    X = df[["age", "sex", "bmi"]].copy()

    # Handle KL grades - convert "na" to NaN if not already
    if "kl_r" in df.columns:
        X["kl_r"] = df["kl_r"].replace(["na", "NA", ""], np.nan)
    else:
        X["kl_r"] = np.nan

    if "kl_l" in df.columns:
        X["kl_l"] = df["kl_l"].replace(["na", "NA", ""], np.nan)
    else:
        X["kl_l"] = np.nan

    if "fam_hx" in df.columns:
        X["fam_hx"] = df["fam_hx"].fillna(0).astype(int)
    else:
        X["fam_hx"] = 0  # Default to No if not provided

    # Handle WOMAC/VAS conversion
    # Convert VAS to WOMAC if VAS is provided, otherwise use WOMAC (can be missing)
    if "vas_r" in df.columns:
        # Convert VAS to WOMAC, handling NaN values
        X["womac_r"] = df["vas_r"].apply(
            lambda x: vas_to_womac(x, scale="0-10") if pd.notna(x) else np.nan
        )
    elif "womac_r" in df.columns:
        X["womac_r"] = df["womac_r"]
    else:
        # No WOMAC or VAS provided - will be imputed later
        X["womac_r"] = np.nan

    if "vas_l" in df.columns:
        # Convert VAS to WOMAC, handling NaN values
        X["womac_l"] = df["vas_l"].apply(
            lambda x: vas_to_womac(x, scale="0-10") if pd.notna(x) else np.nan
        )
    elif "womac_l" in df.columns:
        X["womac_l"] = df["womac_l"]
    else:
        # No WOMAC or VAS provided - will be imputed later
        X["womac_l"] = np.nan

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
    # Handle missing WOMAC values in feature engineering
    X["worst_womac"] = X[["V00WOMTSR", "V00WOMTSL"]].max(axis=1, skipna=True)
    # Handle missing KL grades in feature engineering
    X["worst_kl_grade"] = X[["V00XRKLR", "V00XRKLL"]].max(axis=1, skipna=True)
    X["avg_womac"] = X[["V00WOMTSR", "V00WOMTSL"]].mean(axis=1, skipna=True)

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

    # Scale - ensure columns are in the same order as scaler was trained
    # Get the feature names that the scaler expects (from training)
    scaler_feature_names = (
        scaler.feature_names_in_
        if hasattr(scaler, "feature_names_in_")
        else numeric_vars
    )

    # Reorder X_numeric to match scaler's expected order
    X_numeric_ordered = X_numeric[
        [col for col in scaler_feature_names if col in X_numeric.columns]
    ]

    # Add any missing columns (shouldn't happen, but just in case)
    for col in scaler_feature_names:
        if col not in X_numeric_ordered.columns:
            X_numeric_ordered[col] = 0

    # Ensure exact order
    X_numeric_ordered = X_numeric_ordered[scaler_feature_names]

    # Scale
    X_scaled = scaler.transform(X_numeric_ordered)
    X_scaled = pd.DataFrame(X_scaled, columns=scaler_feature_names, index=X.index)

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

    # Ensure all feature_names are present (add missing ones as 0)
    missing_features = [col for col in feature_names if col not in X_final.columns]
    if missing_features:
        for col in missing_features:
            X_final[col] = 0

    # Reorder to match feature_names exactly (critical for model)
    try:
        X_final = X_final[feature_names]
    except KeyError as e:
        # Debug: show what's missing
        missing = [col for col in feature_names if col not in X_final.columns]
        raise Exception(
            f"Feature mismatch. Missing features: {missing}. "
            f"Expected {len(feature_names)} features, got {len(X_final.columns)}. "
            f"Expected features: {feature_names[:10]}... (showing first 10)"
        )

    return X_final
