"""
DOC Risk Calculator - Flask Backend
===================================
Web-based risk calculator for 4-year knee replacement prediction.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import os
import warnings
import sys

# Suppress sklearn version warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent
SCALER_PATH = BASE_DIR / "models" / "scaler.pkl"
FEATURE_NAMES_PATH = BASE_DIR / "models" / "feature_names.pkl"

# Add utils to path for model_loader
sys.path.insert(0, str(BASE_DIR / "utils"))
from model_loader import load_tkr_model, load_preprocessing_objects

# Determine which model to use (from environment variable or default to original)
USE_LITERATURE_CALIBRATION = os.getenv('USE_LITERATURE_CALIBRATION', 'false').lower() == 'true'

# Load model and preprocessing objects
print("Loading model and preprocessing objects...")
print(f"Model type: {'Literature-Calibrated' if USE_LITERATURE_CALIBRATION else 'Pure Data-Driven (Original)'}")
try:
    model = load_tkr_model(use_literature_calibration=USE_LITERATURE_CALIBRATION)
    scaler, imputer, feature_names = load_preprocessing_objects()
    if feature_names is None:
        # Fallback to loading directly if model_loader doesn't provide it
        feature_names = joblib.load(FEATURE_NAMES_PATH)
    print("✓ Model and preprocessing objects loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()
    model = None
    scaler = None
    feature_names = None


def calculate_engineered_features(age, bmi, womac_r, womac_l, kl_r, kl_l):
    """Calculate engineered features."""
    worst_womac = max(womac_r, womac_l)
    worst_kl_grade = max(kl_r, kl_l)
    avg_womac = (womac_r + womac_l) / 2

    # Age groups: 0=<55, 1=55-64, 2=65-74, 3=75+
    if age < 55:
        age_group = 0
    elif age < 65:
        age_group = 1
    elif age < 75:
        age_group = 2
    else:
        age_group = 3

    # BMI categories: 0=Normal (<25), 1=Overweight (25-30), 2=Obese (>30)
    if bmi < 25:
        bmi_category = 0
    elif bmi < 30:
        bmi_category = 1
    else:
        bmi_category = 2

    return {
        "worst_womac": worst_womac,
        "worst_kl_grade": worst_kl_grade,
        "avg_womac": avg_womac,
        "age_group": age_group,
        "bmi_category": bmi_category,
    }


def preprocess_input(data):
    """Preprocess user input to match model format."""
    # Extract inputs
    age = float(data["age"])
    sex = data["sex"]  # "Male" or "Female"
    bmi = float(data["bmi"])
    womac_r = float(data["womac_right"])
    womac_l = float(data["womac_left"])
    kl_r = float(data["kl_right"])
    kl_l = float(data["kl_left"])
    fam_history = data["family_history"]  # "Yes" or "No"

    # Calculate engineered features
    engineered = calculate_engineered_features(age, bmi, womac_r, womac_l, kl_r, kl_l)

    # Create base dataframe with numeric features
    numeric_features = {
        "V00WOMTSR": womac_r,
        "V00WOMTSL": womac_l,
        "V00AGE": age,
        "P01BMI": bmi,
        "V00XRKLR": kl_r,
        "V00XRKLL": kl_l,
        "worst_womac": engineered["worst_womac"],
        "worst_kl_grade": engineered["worst_kl_grade"],
        "avg_womac": engineered["avg_womac"],
        "age_group": engineered["age_group"],
        "bmi_category": engineered["bmi_category"],
    }

    # Create dataframe
    df = pd.DataFrame([numeric_features])

    # Scale numeric features
    scale_vars = [
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
    df[scale_vars] = scaler.transform(df[scale_vars])

    # One-hot encode categorical variables
    # Based on actual preprocessed data format
    # Note: get_dummies with drop_first=True creates 0/1 columns
    # In CSV they appear as True/False but are actually 1/0

    # Initialize all one-hot encoded columns to 0
    encoded_features = {}

    # Sex: Female = 1 if "Female", else 0 (Male is baseline, dropped)
    encoded_features["P02SEX_2: Female"] = 1 if sex == "Female" else 0

    # Race: Default to White or Caucasian (most common in OAI)
    # All race columns exist in preprocessed data
    encoded_features["P02RACE_0: Other Non-white"] = 0
    encoded_features["P02RACE_1: White or Caucasian"] = 1  # Most common
    encoded_features["P02RACE_2: Black or African American"] = 0
    encoded_features["P02RACE_3: Asian"] = 0

    # Cohort: Default to Incidence (for new patients in calculator)
    # Progression is baseline (dropped)
    encoded_features["V00COHORT_2: Incidence"] = 1
    encoded_features["V00COHORT_3: Non-exposed control group"] = 0

    # Family history: Both columns exist (possibly due to 3 categories originally)
    # Set based on user input
    if fam_history == "Yes":
        encoded_features["P01FAMKR_0: No"] = 0
        encoded_features["P01FAMKR_1: Yes"] = 1
    else:  # No
        encoded_features["P01FAMKR_0: No"] = 1
        encoded_features["P01FAMKR_1: Yes"] = 0

    # Add encoded features to dataframe
    for key, value in encoded_features.items():
        df[key] = value

    # Ensure all feature names match (in correct order)
    # Reorder columns to match feature_names
    df = df.reindex(columns=feature_names, fill_value=0)

    return df


def get_risk_category(risk_percent):
    """Categorize risk percentage."""
    if risk_percent < 5:
        return "Low", "#28a745"  # Green
    elif risk_percent < 15:
        return "Moderate", "#ffc107"  # Yellow
    elif risk_percent < 30:
        return "High", "#fd7e14"  # Orange
    else:
        return "Very High", "#dc3545"  # Red


def get_clinical_interpretation(risk_percent, category):
    """Generate clinical interpretation text."""
    if category == "Low":
        return (
            "This patient has a low risk of requiring knee replacement within 4 years. "
            "Continue routine monitoring and standard OA management."
        )
    elif category == "Moderate":
        return (
            "This patient has moderate risk. Consider enhanced surveillance and "
            "discuss preventive interventions such as weight management and physical therapy."
        )
    elif category == "High":
        return (
            "This patient has high risk. Recommend aggressive preventive measures including "
            "weight loss, physical therapy, and consider referral to orthopedic specialist "
            "for advanced management options."
        )
    else:  # Very High
        return (
            "This patient has very high risk. Urgent referral to orthopedic specialist recommended. "
            "Consider early intervention strategies and discuss surgical options with patient."
        )


@app.route("/")
def index():
    """Render main calculator page."""
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    """Calculate risk prediction."""
    try:
        # Get form data
        data = request.json
        
        # Check if user wants to use literature-calibrated model (from request)
        use_calibrated = data.get("use_literature_calibration", False)
        
        # Load the appropriate model if different from current
        current_model = model
        if use_calibrated != USE_LITERATURE_CALIBRATION:
            try:
                current_model = load_tkr_model(use_literature_calibration=use_calibrated)
            except Exception as e:
                # If calibrated model not available, use current model
                print(f"Warning: Could not load {'calibrated' if use_calibrated else 'original'} model: {e}")
                current_model = model

        # Validate inputs
        age = float(data["age"])
        bmi = float(data["bmi"])
        womac_r = float(data["womac_right"])
        womac_l = float(data["womac_left"])
        kl_r = float(data["kl_right"])
        kl_l = float(data["kl_left"])

        # Basic validation
        if not (45 <= age <= 79):
            return jsonify({"error": "Age must be between 45 and 79"}), 400
        if not (15 <= bmi <= 50):
            return jsonify({"error": "BMI must be between 15 and 50"}), 400
        if not (0 <= womac_r <= 96) or not (0 <= womac_l <= 96):
            return jsonify({"error": "WOMAC scores must be between 0 and 96"}), 400
        if not (0 <= kl_r <= 4) or not (0 <= kl_l <= 4):
            return jsonify({"error": "KL grades must be between 0 and 4"}), 400

        # Preprocess input
        X = preprocess_input(data)

        # Make prediction
        risk_probability = current_model.predict_proba(X)[0, 1]
        risk_percent = risk_probability * 100

        # Get risk category
        category, color = get_risk_category(risk_percent)

        # Get interpretation
        interpretation = get_clinical_interpretation(risk_percent, category)
        
        # Add model info to response
        model_type = "Literature-Calibrated" if use_calibrated else "Pure Data-Driven"

        # Return results
        return jsonify(
            {
                "success": True,
                "risk_percent": round(risk_percent, 1),
                "risk_probability": round(risk_probability, 4),
                "category": category,
                "color": color,
                "interpretation": interpretation,
                "model_type": model_type,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/model/info", methods=["GET"])
def model_info():
    """Get information about available models."""
    from model_loader import get_model_info
    
    original_info = get_model_info(use_literature_calibration=False)
    try:
        calibrated_info = get_model_info(use_literature_calibration=True)
    except:
        calibrated_info = {"exists": False}
    
    return jsonify({
        "current_model": "Literature-Calibrated" if USE_LITERATURE_CALIBRATION else "Pure Data-Driven",
        "original_model": original_info,
        "calibrated_model": calibrated_info,
    })


if __name__ == "__main__":
    if model is None:
        print("❌ Cannot start server: Model not loaded")
    else:
        import warnings

        # Suppress sklearn version warnings (model works fine with different versions)
        warnings.filterwarnings("ignore", category=UserWarning)

        print("\n" + "=" * 60)
        print("DOC Risk Calculator - Starting Server")
        print("=" * 60)
        print(f"Model: {'Literature-Calibrated' if USE_LITERATURE_CALIBRATION else 'Pure Data-Driven (Original)'}")
        print("Access the calculator at: http://localhost:3003")
        print("Toggle model via: USE_LITERATURE_CALIBRATION=true python app.py")
        print("Or send use_literature_calibration=true in POST /calculate request")
        print("Press Ctrl+C to stop the server")
        print("=" * 60 + "\n")
        app.run(debug=True, host="0.0.0.0", port=3003)
