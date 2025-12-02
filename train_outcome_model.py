"""
Train outcome prediction model (Random Forest Regressor)
Predicts expected WOMAC improvement for surgical candidates
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import sys

warnings.filterwarnings("ignore")

print("=" * 80)
print("OUTCOME MODEL TRAINING")
print("=" * 80)

# Paths
base_path = Path(__file__).parent
models_path = base_path / "models"
data_path = base_path / "data"

# Load surgery patients with outcomes
print("\n1. Loading surgery patients with outcomes...")
outcomes_df = pd.read_csv("surgery_patients_with_outcomes.csv")
print(f"   Total surgery patients: {len(outcomes_df)}")

# Filter to patients with post-op data
outcomes_df = outcomes_df[outcomes_df["improvement"].notna()].copy()
print(f"   Patients with post-op data: {len(outcomes_df)}")

# Load baseline data to get all features
print("\n2. Loading baseline data...")
try:
    # Try to load preprocessed baseline data
    baseline_path = data_path / "baseline_modeling.csv"
    if baseline_path.exists():
        baseline_df = pd.read_csv(baseline_path)
        print(f"   Baseline data loaded: {baseline_df.shape}")
    else:
        # Load from raw data
        from pathlib import Path

        general_path = Path("data/raw/General_ASCII")
        clinical_path = Path("data/raw/AllClinical_ASCII")

        # Load baseline clinical data
        baseline_clinical = pd.read_csv(
            clinical_path / "AllClinical00.txt", sep="|", low_memory=False
        )

        # Load subject characteristics
        subject_char = pd.read_csv(
            general_path / "SubjectChar00.txt", sep="|", low_memory=False
        )

        # Load enrollees for demographics
        enrollees = pd.read_csv(
            general_path / "Enrollees.txt", sep="|", low_memory=False
        )

        # Standardize IDs
        baseline_clinical["ID"] = baseline_clinical["ID"].astype(str).str.upper()
        subject_char["ID"] = subject_char["ID"].astype(str).str.upper()
        enrollees["ID"] = enrollees["ID"].astype(str).str.upper()
        outcomes_df["ID"] = outcomes_df["ID"].astype(str).str.upper()

        # Merge
        baseline_df = baseline_clinical.merge(
            subject_char[["ID", "P01BMI", "P01FAMKR"]], on="ID", how="left"
        ).merge(
            enrollees[["ID", "V00AGE", "P02SEX", "P02RACE", "V00COHORT"]],
            on="ID",
            how="left",
        )

        print(f"   Baseline data merged: {baseline_df.shape}")

except Exception as e:
    print(f"   Error loading baseline data: {e}")
    print("   Will use minimal feature set from outcomes data")
    baseline_df = None

# Merge outcomes with baseline features
print("\n3. Merging outcomes with baseline features...")
if baseline_df is not None:
    # Standardize ID (ensure both are strings)
    baseline_df["ID"] = baseline_df["ID"].astype(str).str.upper().str.strip()
    outcomes_df["ID"] = outcomes_df["ID"].astype(str).str.upper().str.strip()

    # Merge
    training_df = outcomes_df.merge(baseline_df, on="ID", how="inner")
    print(f"   Merged dataset: {training_df.shape}")
    print(f"   Matched {len(training_df)} out of {len(outcomes_df)} surgery patients")
else:
    # Use outcomes data only (minimal features)
    training_df = outcomes_df.copy()
    print(f"   Using outcomes data only: {training_df.shape}")

# Check if we have enough data
if len(training_df) < 50:
    print(f"\n❌ ERROR: Insufficient data for training ({len(training_df)} patients)")
    print("   Need at least 50 patients with post-op outcomes")
    sys.exit(1)

# Load surgery model preprocessing components
print("\n4. Loading surgery model preprocessing components...")
try:
    scaler = joblib.load(models_path / "scaler.pkl")
    feature_names = joblib.load(models_path / "feature_names.pkl")
    print(f"   ✓ Scaler loaded")
    print(f"   ✓ Feature names loaded ({len(feature_names)} features)")
except Exception as e:
    print(f"   ❌ Error loading preprocessing components: {e}")
    sys.exit(1)

# Prepare features using same preprocessing as surgery model
print("\n5. Preprocessing features...")
try:
    from DOC_Validator_Vercel.preprocessing import preprocess_data

    # Create input dataframe in the format expected by preprocess_data
    # Map baseline columns to input format
    input_df = pd.DataFrame()

    # Age
    if "V00AGE" in training_df.columns:
        input_df["age"] = training_df["V00AGE"]
    else:
        print("   ⚠️  Age not found, using surgery_days as proxy")
        input_df["age"] = 65  # Default age

    # Sex (1=Male, 0=Female in input format)
    if "P02SEX" in training_df.columns:
        # OAI: 1=Male, 2=Female -> Input: 1=Male, 0=Female
        input_df["sex"] = (training_df["P02SEX"] == 1).astype(int)
    else:
        input_df["sex"] = 1  # Default to Male

    # BMI
    if "P01BMI" in training_df.columns:
        input_df["bmi"] = training_df["P01BMI"]
    else:
        input_df["bmi"] = 28  # Default BMI

    # WOMAC scores (use pre-op)
    if "pre_op_womac" in training_df.columns:
        # Split into left/right (use same value for both if only one available)
        if "V00WOMTSR" in training_df.columns:
            input_df["womac_r"] = training_df["V00WOMTSR"]
        else:
            input_df["womac_r"] = training_df["pre_op_womac"]

        if "V00WOMTSL" in training_df.columns:
            input_df["womac_l"] = training_df["V00WOMTSL"]
        else:
            input_df["womac_l"] = training_df["pre_op_womac"]
    elif "V00WOMTSR" in training_df.columns and "V00WOMTSL" in training_df.columns:
        input_df["womac_r"] = training_df["V00WOMTSR"]
        input_df["womac_l"] = training_df["V00WOMTSL"]
    else:
        print("   ❌ WOMAC scores not found")
        sys.exit(1)

    # KL grades
    if "V00XRKLR" in training_df.columns and "V00XRKLL" in training_df.columns:
        input_df["kl_r"] = training_df["V00XRKLR"]
        input_df["kl_l"] = training_df["V00XRKLL"]
    else:
        # Try to get from other sources or use defaults
        print("   ⚠️  KL grades not found, using defaults")
        input_df["kl_r"] = 2
        input_df["kl_l"] = 2

    # Family history
    if "P01FAMKR" in training_df.columns:
        input_df["fam_hx"] = training_df["P01FAMKR"]
    else:
        input_df["fam_hx"] = 0  # Default to No

    # Preprocess
    X_preprocessed = preprocess_data(input_df, None, scaler, feature_names)
    print(f"   ✓ Features preprocessed: {X_preprocessed.shape}")

except Exception as e:
    print(f"   ❌ Error preprocessing: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Prepare outcome (improvement)
y = training_df["improvement"].values
print(f"\n6. Outcome statistics:")
print(f"   Mean improvement: {y.mean():.1f} points")
print(f"   Median improvement: {np.median(y):.1f} points")
print(f"   Std deviation: {y.std():.1f} points")
print(f"   Range: {y.min():.1f} to {y.max():.1f} points")

# Train/test split
print("\n7. Train/test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X_preprocessed, y, test_size=0.2, random_state=42
)
print(f"   Train: {len(X_train)} patients")
print(f"   Test: {len(X_test)} patients")

# Train Random Forest Regressor
print("\n8. Training Random Forest Regressor...")
rf_regressor = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=20,
    min_samples_leaf=10,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1,
)

rf_regressor.fit(X_train, y_train)
print("   ✓ Model trained")

# Evaluate
print("\n9. Evaluating model...")
y_train_pred = rf_regressor.predict(X_train)
y_test_pred = rf_regressor.predict(X_test)

train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print(f"   Train RMSE: {train_rmse:.2f} points")
print(f"   Test RMSE: {test_rmse:.2f} points")
print(f"   Train MAE: {train_mae:.2f} points")
print(f"   Test MAE: {test_mae:.2f} points")
print(f"   Train R²: {train_r2:.3f}")
print(f"   Test R²: {test_r2:.3f}")

# Save model
print("\n10. Saving model...")
model_path = models_path / "outcome_rf_regressor.pkl"
joblib.dump(rf_regressor, model_path)
print(f"   ✓ Model saved: {model_path}")

# Also save to Vercel models directory
vercel_models_path = base_path / "DOC_Validator_Vercel" / "api" / "models"
if vercel_models_path.exists():
    vercel_model_path = vercel_models_path / "outcome_rf_regressor.pkl"
    joblib.dump(rf_regressor, vercel_model_path)
    print(f"   ✓ Model saved to Vercel directory: {vercel_model_path}")

print("\n" + "=" * 80)
print("OUTCOME MODEL TRAINING COMPLETE")
print("=" * 80)
print(f"\nModel performance:")
print(f"  Test RMSE: {test_rmse:.2f} points")
print(f"  Test MAE: {test_mae:.2f} points")
print(f"  Test R²: {test_r2:.3f}")
print(f"\nModel saved to: {model_path}")
