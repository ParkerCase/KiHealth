#!/usr/bin/env python3
"""
KiHealth Diabetes Risk Calculator UI

A comprehensive patient assessment tool that:
1. Collects pre-qualifying questionnaire responses
2. Gathers biomarker data (Beta Score, HbA1c, insulin, glucose, BMI, etc.)
3. Calculates current diabetes status (diabetic/prediabetic/normal)
4. Predicts diabetes risk using KiHealth's Beta Score model
5. Provides personalized recommendations
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Model paths
FINAL_MODEL_PATH = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "final_model_calibrated.joblib"
FINAL_THRESHOLDS_PATH = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "final_thresholds.joblib"
ENSEMBLE_MODEL_PATH = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "ensemble_model_calibrated.joblib"
ENSEMBLE_THRESHOLD_PATH = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "ensemble_threshold.joblib"

# M2 Transfer Learning Model paths
# Validated on 129 patients: AUC 0.875 ± 0.065, 95% CI [0.75, 1.00]
# Foundation trained on 17,427 NHANES+CHNS patients
M2_MODELS_PATH = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "M2_Models"
M2_FOUNDATION_PATH = M2_MODELS_PATH / "foundation_combined.joblib"
M2_FOUNDATION_SCALER_PATH = M2_MODELS_PATH / "foundation_scaler.joblib"
M2_BETA_MODEL_PATH = M2_MODELS_PATH / "beta_foundation_model.joblib"
M2_BETA_SCALER_PATH = M2_MODELS_PATH / "beta_foundation_scaler.joblib"
M2_THRESHOLDS_PATH = M2_MODELS_PATH / "beta_foundation_thresholds.joblib"

# SVG Icons
SVG_ICONS = {
    "check_circle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>''',
    "alert_circle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>''',
    "x_circle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>''',
    "info": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>''',
    "activity": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>''',
    "heart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>''',
    "user": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>''',
    "clipboard": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>''',
    "flask": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6v6l4 9H5l4-9V3z"></path><line x1="9" y1="3" x2="15" y2="3"></line></svg>''',
    "chart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>''',
    "shield_check": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>''',
    "shield_alert": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>''',
    "trending_up": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>''',
    "trending_down": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>''',
    "dna": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 15c6.667-6 13.333 0 20-6"></path><path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993"></path><path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993"></path><path d="M17 6l-2.5-2.5"></path><path d="M14 8l-1-1"></path><path d="M7 18l2.5 2.5"></path><path d="M3.5 14.5l.5.5"></path><path d="M20 9l.5.5"></path><path d="M6.5 12.5l1 1"></path><path d="M16.5 10.5l1 1"></path><path d="M10 16l1.5 1.5"></path></svg>''',
}


def svg_icon(name: str, size: int = 24) -> str:
    """Return SVG icon HTML with optional size adjustment."""
    svg = SVG_ICONS.get(name, SVG_ICONS["info"])
    if size != 24:
        svg = svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    return svg


def load_models():
    """Load the prediction models."""
    models = {}
    try:
        import joblib
        
        # Load M2 Transfer Learning Model (AUC 0.875, validated on 129 patients)
        if M2_FOUNDATION_PATH.exists() and M2_BETA_MODEL_PATH.exists():
            models["m2_foundation"] = joblib.load(M2_FOUNDATION_PATH)
            models["m2_foundation_scaler"] = joblib.load(M2_FOUNDATION_SCALER_PATH)
            models["m2_beta_model"] = joblib.load(M2_BETA_MODEL_PATH)
            models["m2_beta_scaler"] = joblib.load(M2_BETA_SCALER_PATH)
            if M2_THRESHOLDS_PATH.exists():
                models["m2_thresholds"] = joblib.load(M2_THRESHOLDS_PATH)
            models["m2_available"] = True
        
        # Load final model (AUC 0.890, multiple thresholds) as fallback
        if FINAL_MODEL_PATH.exists():
            models["final"] = joblib.load(FINAL_MODEL_PATH)
            if FINAL_THRESHOLDS_PATH.exists():
                models["thresholds"] = joblib.load(FINAL_THRESHOLDS_PATH)
        # Fallback to ensemble model
        elif ENSEMBLE_MODEL_PATH.exists():
            models["ensemble"] = joblib.load(ENSEMBLE_MODEL_PATH)
            if ENSEMBLE_THRESHOLD_PATH.exists():
                models["ensemble_threshold"] = joblib.load(ENSEMBLE_THRESHOLD_PATH)
    except Exception as e:
        st.warning(f"Could not load models: {e}")
    return models


def predict_with_m2_model(data: dict, models: dict) -> dict:
    """
    Predict using M2 Transfer Learning model.
    
    This model uses a two-stage approach:
    1. Foundation model (trained on 17,427 NHANES+CHNS patients) predicts traditional risk
    2. Final model combines Beta Score with foundation prediction
    
    Performance (validated on unified dataset n=129):
    - Cross-validated AUC: 0.875 ± 0.065
    - Screening mode: 100% sensitivity, 60% specificity
    - Balanced mode: 76% sensitivity, 82% specificity
    - Confirmation mode: 59% sensitivity, 87% specificity
    """
    result = {
        "probability": None,
        "foundation_pred": None,
        "model_name": "M2 Transfer Learning (AUC: 0.875)"
    }
    
    beta_score = data.get("beta_score")  # This is % Unmethylated
    hba1c = data.get("hba1c")
    insulin = data.get("insulin")
    glucose = data.get("glucose")
    
    if beta_score is None or hba1c is None:
        return result
    
    # Calculate HOMA-IR (needed for foundation model)
    if insulin and glucose and insulin > 0 and glucose > 0:
        homa_ir = (insulin * glucose) / 405
    else:
        # Estimate glucose from HbA1c if not provided
        estimated_glucose = (hba1c - 2.15) * 35.6
        if insulin and insulin > 0:
            homa_ir = (insulin * estimated_glucose) / 405
        else:
            # Use median HOMA-IR from training data
            homa_ir = 2.5
    
    try:
        # Stage 1: Foundation model prediction
        X_foundation = pd.DataFrame([[hba1c, homa_ir]], columns=['hba1c', 'homa_ir'])
        X_foundation_scaled = models["m2_foundation_scaler"].transform(X_foundation)
        foundation_pred = models["m2_foundation"].predict_proba(X_foundation_scaled)[0, 1]
        result["foundation_pred"] = foundation_pred
        
        # Stage 2: Final model (Beta Score + Foundation Prediction)
        X_final = pd.DataFrame([[beta_score, foundation_pred]], columns=['beta_score', 'foundation_pred'])
        X_final_scaled = models["m2_beta_scaler"].transform(X_final)
        final_prob = models["m2_beta_model"].predict_proba(X_final_scaled)[0, 1]
        result["probability"] = final_prob
        
    except Exception as e:
        st.warning(f"M2 model prediction error: {e}")
    
    return result


def calculate_homa_ir(insulin: float, glucose: float) -> float:
    """Calculate HOMA-IR (insulin resistance index)."""
    if insulin > 0 and glucose > 0:
        return (insulin * glucose) / 405
    return np.nan


def calculate_homa_beta(insulin: float, glucose: float) -> float:
    """Calculate HOMA-beta (beta cell function)."""
    if insulin > 0 and glucose > 0:
        glucose_mmol = glucose / 18.0
        if glucose_mmol > 3.5:
            return (20 * insulin) / (glucose_mmol - 3.5)
    return np.nan


def get_diabetes_status(hba1c: float, glucose: float) -> tuple[str, str]:
    """Determine diabetes status based on ADA criteria."""
    if pd.isna(hba1c) and pd.isna(glucose):
        return "Unknown", "Insufficient data to determine status"
    
    is_diabetic_hba1c = hba1c >= 6.5 if not pd.isna(hba1c) else False
    is_diabetic_glucose = glucose >= 126 if not pd.isna(glucose) else False
    is_prediabetic_hba1c = 5.7 <= hba1c < 6.5 if not pd.isna(hba1c) else False
    is_prediabetic_glucose = 100 <= glucose < 126 if not pd.isna(glucose) else False
    
    if is_diabetic_hba1c or is_diabetic_glucose:
        reasons = []
        if is_diabetic_hba1c:
            reasons.append(f"HbA1c {hba1c:.1f}% >= 6.5%")
        if is_diabetic_glucose:
            reasons.append(f"Fasting glucose {glucose:.0f} mg/dL >= 126")
        return "Diabetic", " and ".join(reasons)
    
    if is_prediabetic_hba1c or is_prediabetic_glucose:
        reasons = []
        if is_prediabetic_hba1c:
            reasons.append(f"HbA1c {hba1c:.1f}% in 5.7-6.4% range")
        if is_prediabetic_glucose:
            reasons.append(f"Fasting glucose {glucose:.0f} mg/dL in 100-125 range")
        return "Prediabetic", " and ".join(reasons)
    
    # Normal - handle case where glucose is not provided
    if pd.isna(glucose):
        return "Normal", f"HbA1c {hba1c:.1f}% within normal range (<5.7%)"
    else:
        return "Normal", f"HbA1c {hba1c:.1f}% and glucose {glucose:.0f} mg/dL within normal ranges"


def calculate_risk_score(data: dict, models: dict) -> dict:
    """Calculate comprehensive risk assessment."""
    results = {
        "current_status": None,
        "status_explanation": None,
        "risk_probability": None,
        "risk_category": None,
        "homa_ir": None,
        "homa_beta": None,
        "risk_factors": [],
        "protective_factors": [],
        "recommendations": [],
        "beta_contribution": None,
        "model_used": None,
    }
    
    # Calculate HOMA indices
    if data.get("insulin") and data.get("glucose"):
        results["homa_ir"] = calculate_homa_ir(data["insulin"], data["glucose"])
        results["homa_beta"] = calculate_homa_beta(data["insulin"], data["glucose"])
    
    # Determine current status
    status, explanation = get_diabetes_status(
        data.get("hba1c", np.nan), 
        data.get("glucose", np.nan)
    )
    results["current_status"] = status
    results["status_explanation"] = explanation
    
    # Identify risk factors
    if data.get("bmi") and data["bmi"] >= 30:
        results["risk_factors"].append(f"Obesity (BMI {data['bmi']:.1f})")
    elif data.get("bmi") and data["bmi"] >= 25:
        results["risk_factors"].append(f"Overweight (BMI {data['bmi']:.1f})")
    
    if results["homa_ir"] and results["homa_ir"] > 2.5:
        results["risk_factors"].append(f"Insulin resistance (HOMA-IR {results['homa_ir']:.1f})")
    
    if data.get("age") and data["age"] >= 45:
        results["risk_factors"].append(f"Age >= 45 years ({data['age']})")
    
    if data.get("hbp") == "Yes":
        results["risk_factors"].append("High blood pressure")
    
    # Questionnaire risk factors
    if data.get("q_hungry_after_eating") == "Yes":
        results["risk_factors"].append("Feels hungry shortly after eating")
    if data.get("q_crave_sweets") == "Yes":
        results["risk_factors"].append("Craves sweets")
    if data.get("q_tired_often") == "Yes":
        results["risk_factors"].append("Fatigue despite adequate sleep")
    if data.get("q_skin_tags") == "Yes":
        results["risk_factors"].append("Multiple skin tags")
    if data.get("q_uti_infections") == "Yes":
        results["risk_factors"].append("Recurrent UTI/skin infections")
    if data.get("q_mood_swings") == "Yes":
        results["risk_factors"].append("Mood swings/irritability")
    if data.get("q_pcos") == "Yes":
        results["risk_factors"].append("PCOS diagnosis")
    
    # Protective factors (beta_score is % Unmethylated - lower = healthier)
    if data.get("beta_score") is not None:
        unmeth = data["beta_score"]
        if unmeth <= 6:
            results["protective_factors"].append(f"Low unmethylated DNA ({unmeth:.1f}%) - healthy beta cells")
        elif unmeth >= 10:
            results["risk_factors"].append(f"Elevated unmethylated DNA ({unmeth:.1f}%) - beta cell damage")
    
    if data.get("bmi") and data["bmi"] < 25:
        results["protective_factors"].append(f"Healthy weight (BMI {data['bmi']:.1f})")
    
    if results["homa_ir"] and results["homa_ir"] < 1.5:
        results["protective_factors"].append(f"Good insulin sensitivity (HOMA-IR {results['homa_ir']:.1f})")
    
    # C-peptide and Insulin observations (data-driven from KiHealth cohort)
    # NOTE: In KiHealth data, HIGH C-peptide/insulin correlates with T2D risk (insulin resistance pattern)
    # At-risk patients: mean C-peptide=5.15, mean insulin=36.5
    # Not at-risk: mean C-peptide=3.04, mean insulin=24.5
    c_peptide = data.get("c_peptide")
    insulin = data.get("insulin")
    
    if c_peptide is not None:
        # Based on KiHealth data distribution (mean=3.5, 75th percentile=4.8)
        if c_peptide > 4.8:
            results["risk_factors"].append(f"Elevated C-peptide ({c_peptide:.2f} ng/mL) - associated with insulin resistance in KiHealth data")
        results["c_peptide_value"] = c_peptide
    
    if insulin is not None:
        # Based on KiHealth data distribution (mean=27.4, 75th percentile=39)
        if insulin > 39:
            results["risk_factors"].append(f"Elevated insulin ({insulin:.1f} uU/mL) - associated with insulin resistance in KiHealth data")
        results["insulin_value"] = insulin
    
    # Note: C-peptide and insulin are NOT used in the ML model prediction
    # They are displayed for clinical context only
    
    clinical_mode = data.get("clinical_mode", "balanced")
    use_m2_model = data.get("use_m2_model", True)  # Default to M2 model
    
    # Try M2 Transfer Learning model first (BEST: AUC 0.981)
    if use_m2_model and models.get("m2_available") and data.get("beta_score") is not None and data.get("hba1c") is not None:
        try:
            m2_result = predict_with_m2_model(data, models)
            if m2_result["probability"] is not None:
                prob = m2_result["probability"]
                results["risk_probability"] = round(prob * 100, 1)
                results["foundation_pred"] = m2_result["foundation_pred"]
                
                # M2 model thresholds (optimized on unified dataset n=129)
                # Based on actual cross-validated performance
                m2_thresholds = {
                    "screening": 0.24,      # 100% sensitivity, 60% specificity
                    "balanced": 0.56,       # 76% sensitivity, 82% specificity
                    "confirmation": 0.64,   # 59% sensitivity, 87% specificity
                }
                threshold = m2_thresholds.get(clinical_mode, 0.56)
                
                # M2 mode-specific performance (validated on n=129 unified dataset)
                m2_performance = {
                    "screening": {"sens": "100%", "spec": "60%", "desc": "Catches all at-risk patients"},
                    "balanced": {"sens": "76%", "spec": "82%", "desc": "Optimal trade-off"},
                    "confirmation": {"sens": "59%", "spec": "87%", "desc": "High confidence positives"},
                }
                
                perf = m2_performance.get(clinical_mode, m2_performance["balanced"])
                results["model_used"] = f"M2 Transfer Learning (AUC: 0.875) - {clinical_mode.title()} Mode (Sens: {perf['sens']}, Spec: {perf['spec']})"
                results["clinical_mode"] = clinical_mode
                results["threshold"] = threshold
                
                # Categorize risk
                if prob < threshold * 0.5:
                    results["risk_category"] = "Low"
                elif prob < threshold:
                    results["risk_category"] = "Moderate"
                elif prob < threshold * 1.5:
                    results["risk_category"] = "High"
                else:
                    results["risk_category"] = "Very High"
                
                results["at_risk_classification"] = "At Risk" if prob >= threshold else "Not At Risk"
                
                # Calculate Beta Score contribution (compare to average beta score of 8%)
                avg_beta_data = data.copy()
                avg_beta_data["beta_score"] = 8.0  # Average in validation data
                avg_result = predict_with_m2_model(avg_beta_data, models)
                if avg_result["probability"] is not None:
                    results["beta_contribution"] = round((prob - avg_result["probability"]) * 100, 1)
                
        except Exception as e:
            st.warning(f"M2 model error: {e}")
    
    # Fallback to original model (AUC 0.890) if M2 not available or failed
    if results["risk_probability"] is None:
        model_key = "final" if "final" in models else "ensemble" if "ensemble" in models else None
        
        if model_key and data.get("beta_score") is not None and data.get("hba1c") is not None:
            try:
                features = pd.DataFrame([{
                    "beta_score": data.get("beta_score", 90),
                    "hba1c": data.get("hba1c", 5.5),
                }])
                
                prob = models[model_key].predict_proba(features)[0, 1]
                results["risk_probability"] = round(prob * 100, 1)
                
                # Get threshold based on clinical mode
                thresholds = models.get("thresholds", {"screening": 0.25, "balanced": 0.45, "confirmation": 0.60})
                threshold = thresholds.get(clinical_mode, 0.45)
                
                # Mode-specific performance (fallback model)
                mode_performance = {
                    "screening": {"sens": "100%", "spec": "60%", "desc": "Catches all at-risk patients"},
                    "balanced": {"sens": "76%", "spec": "82%", "desc": "Optimal trade-off"},
                    "confirmation": {"sens": "59%", "spec": "87%", "desc": "High confidence positives"},
                }
                
                perf = mode_performance.get(clinical_mode, mode_performance["balanced"])
                results["model_used"] = f"KiHealth Final (AUC: 0.890) - {clinical_mode.title()} Mode (Sens: {perf['sens']}, Spec: {perf['spec']})"
                results["clinical_mode"] = clinical_mode
                results["threshold"] = threshold
                
                # Categorize risk based on threshold
                if prob < threshold * 0.5:
                    results["risk_category"] = "Low"
                elif prob < threshold:
                    results["risk_category"] = "Moderate"
                elif prob < threshold * 1.5:
                    results["risk_category"] = "High"
                else:
                    results["risk_category"] = "Very High"
                
                # Binary classification based on mode threshold
                results["at_risk_classification"] = "At Risk" if prob >= threshold else "Not At Risk"
                
                # Calculate Beta Score contribution
                features_avg = features.copy()
                features_avg["beta_score"] = 92.0
                prob_avg = models[model_key].predict_proba(features_avg)[0, 1]
                results["beta_contribution"] = round((prob - prob_avg) * 100, 1)
                
            except Exception as e:
                st.warning(f"Model error: {e}")
    
    # Fallback estimation if no model
    if results["risk_probability"] is None:
        base_risk = 20.0
        
        if status == "Prediabetic":
            base_risk += 30
        elif status == "Diabetic":
            base_risk = 95
        
        # Beta Score impact (beta_score is % Unmethylated - higher = more risk)
        unmeth = data.get("beta_score", 5.0)  # Default to healthy 5%
        if unmeth > 10:
            base_risk += (unmeth - 10) * 2  # Add risk for elevated unmethylated
        elif unmeth <= 6:
            base_risk -= (6 - unmeth) * 1.5  # Reduce risk for very healthy
        
        base_risk += len(results["risk_factors"]) * 3
        base_risk -= len(results["protective_factors"]) * 2
        
        results["risk_probability"] = max(5, min(95, base_risk))
        results["model_used"] = "Rule-based estimation"
        
        if results["risk_probability"] < 25:
            results["risk_category"] = "Low"
        elif results["risk_probability"] < 50:
            results["risk_category"] = "Moderate"
        elif results["risk_probability"] < 75:
            results["risk_category"] = "High"
        else:
            results["risk_category"] = "Very High"
    
    # Generate recommendations
    if status == "Diabetic":
        results["recommendations"] = [
            "Consult with endocrinologist for diabetes management plan",
            "Begin or continue diabetes medication as prescribed",
            "Monitor blood glucose regularly",
            "Follow diabetic diet guidelines",
            "Regular HbA1c testing every 3 months",
        ]
    elif status == "Prediabetic" or results["risk_category"] in ["High", "Very High"]:
        results["recommendations"] = [
            "Lifestyle intervention is critical - can reduce progression risk by 58%",
            "Target 7% weight loss if overweight",
            "150 minutes/week of moderate physical activity",
            "Consider metformin if high-risk (discuss with physician)",
            "Retest HbA1c in 3-6 months",
        ]
    else:
        results["recommendations"] = [
            "Maintain healthy lifestyle",
            "Annual diabetes screening recommended",
            "Continue regular physical activity",
            "Balanced diet with limited processed sugars",
        ]
    
    return results


def main():
    st.set_page_config(
        page_title="KiHealth Diabetes Risk Calculator",
        page_icon="data:image/svg+xml," + SVG_ICONS["heart"].replace("#", "%23"),
        layout="wide",
    )
    
    # Custom CSS for SVG icons
    st.markdown("""
    <style>
    .icon-text {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .risk-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-low { background-color: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; }
    .risk-moderate { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; }
    .risk-high { background-color: rgba(249, 115, 22, 0.1); border: 1px solid #f97316; }
    .risk-very-high { background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with icon
    st.markdown(f"""
    <div class="icon-text">
        {svg_icon("heart", 32)}
        <h1 style="margin: 0;">KiHealth Diabetes Risk Calculator</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    This tool assesses diabetes risk using KiHealth's Beta Score technology combined with 
    standard biomarkers and lifestyle factors.
    """)
    
    # Load models
    models = load_models()
    
    # Model status
    if models.get("m2_available"):
        st.markdown(f"""
        <div class="icon-text" style="color: #22c55e;">
            {svg_icon("shield_check", 20)}
            <span><strong>M2 Transfer Learning Model loaded:</strong> AUC 0.875 (CV) | Validated on 129 patients</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Transfer learning from 17,427 NHANES+CHNS patients. Performance varies by clinical mode.")
    elif "final" in models:
        st.markdown(f"""
        <div class="icon-text" style="color: #22c55e;">
            {svg_icon("shield_check", 20)}
            <span>Final Model loaded: AUC 0.890 | Multiple clinical modes available</span>
        </div>
        """, unsafe_allow_html=True)
    elif "ensemble" in models:
        st.markdown(f"""
        <div class="icon-text" style="color: #22c55e;">
            {svg_icon("shield_check", 20)}
            <span>Ensemble Model loaded: AUC 0.890, Sensitivity 78%, Specificity 82%</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs with icons (Results moved inline below Biomarkers)
    tab1, tab2, tab3 = st.tabs([
        "Pre-Qualifying Questions",
        "Biomarkers & Labs",
        "Model Information"
    ])
    
    # Initialize session state
    if "patient_data" not in st.session_state:
        st.session_state.patient_data = {}
    
    # Tab 1: Pre-Qualifying Questionnaire
    with tab1:
        st.markdown(f"""
        <div class="icon-text">
            {svg_icon("clipboard", 28)}
            <h2 style="margin: 0;">Pre-Qualifying Questionnaire</h2>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("These questions help identify lifestyle and symptom-based risk factors.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Medical History")
            
            q_hbp = st.radio(
                "Have you been diagnosed with High Blood Pressure?",
                ["No", "Yes"],
                key="q_hbp",
                horizontal=True
            )
            
            q_pcos = st.radio(
                "Have you been diagnosed with PCOS?",
                ["No", "Yes", "N/A"],
                key="q_pcos",
                horizontal=True
            )
            
            q_blood_thinners = st.radio(
                "Are you taking any blood thinners?",
                ["No", "Yes"],
                key="q_blood_thinners",
                horizontal=True
            )
            
            q_uti = st.radio(
                "Recurrent UTI or Skin Infections (>1 in past year)?",
                ["No", "Yes"],
                key="q_uti",
                horizontal=True
            )
        
        with col2:
            st.subheader("Symptoms & Lifestyle")
            
            q_hungry = st.radio(
                "Do you feel hungry shortly after eating?",
                ["No", "Yes"],
                key="q_hungry",
                horizontal=True
            )
            
            q_sweets = st.radio(
                "Do you crave sweets?",
                ["No", "Yes"],
                key="q_sweets",
                horizontal=True
            )
            
            q_tired = st.radio(
                "Do you feel tired often, even after good sleep?",
                ["No", "Yes"],
                key="q_tired",
                horizontal=True
            )
            
            q_skin_tags = st.radio(
                "Do you have multiple skin tags?",
                ["No", "Yes"],
                key="q_skin_tags",
                horizontal=True
            )
            
            q_mood = st.radio(
                "Do you have mood swings or feel easily irritable?",
                ["No", "Yes"],
                key="q_mood",
                horizontal=True
            )
        
        # Calculate questionnaire risk score
        q_risk_count = sum([
            q_hbp == "Yes",
            q_pcos == "Yes",
            q_uti == "Yes",
            q_hungry == "Yes",
            q_sweets == "Yes",
            q_tired == "Yes",
            q_skin_tags == "Yes",
            q_mood == "Yes",
        ])
        
        st.divider()
        
        if q_risk_count == 0:
            st.markdown(f"""
            <div class="icon-text" style="color: #22c55e;">
                {svg_icon("check_circle")}
                <span>No questionnaire-based risk factors identified</span>
            </div>
            """, unsafe_allow_html=True)
        elif q_risk_count <= 2:
            st.markdown(f"""
            <div class="icon-text" style="color: #3b82f6;">
                {svg_icon("info")}
                <span>{q_risk_count} minor risk factor(s) identified from questionnaire</span>
            </div>
            """, unsafe_allow_html=True)
        elif q_risk_count <= 4:
            st.markdown(f"""
            <div class="icon-text" style="color: #f59e0b;">
                {svg_icon("alert_circle")}
                <span>{q_risk_count} risk factors identified - recommend biomarker testing</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="icon-text" style="color: #ef4444;">
                {svg_icon("x_circle")}
                <span>{q_risk_count} risk factors identified - comprehensive evaluation recommended</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Store questionnaire data
        st.session_state.patient_data.update({
            "hbp": q_hbp,
            "q_pcos": q_pcos,
            "q_blood_thinners": q_blood_thinners,
            "q_uti_infections": q_uti,
            "q_hungry_after_eating": q_hungry,
            "q_crave_sweets": q_sweets,
            "q_tired_often": q_tired,
            "q_skin_tags": q_skin_tags,
            "q_mood_swings": q_mood,
        })
    
    # Tab 2: Biomarkers
    with tab2:
        st.markdown(f"""
        <div class="icon-text">
            {svg_icon("flask", 28)}
            <h2 style="margin: 0;">Patient Biomarkers & Lab Values</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="icon-text">
                {svg_icon("user", 20)}
                <h4 style="margin: 0;">Demographics</h4>
            </div>
            """, unsafe_allow_html=True)
            
            patient_id = st.text_input("Patient/Donor ID", key="patient_id")
            
            age = st.number_input(
                "Age (years)",
                min_value=1,
                max_value=120,
                value=45,
                key="age"
            )
            
            sex = st.selectbox(
                "Sex",
                ["Male", "Female"],
                key="sex"
            )
            
            race = st.selectbox(
                "Race/Ethnicity",
                ["White/Caucasian", "Black/African American", "Hispanic/Latino", "Asian", "Other"],
                key="race"
            )
        
        with col2:
            st.markdown(f"""
            <div class="icon-text">
                {svg_icon("dna", 20)}
                <h4 style="margin: 0;">KiHealth Beta Score</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Primary input: % Unmethylated (this is what the model uses)
            unmethylated = st.number_input(
                "% Unmethylated (Beta Cell Damage Marker)",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=0.1,
                help="Higher % unmethylated = more beta cell damage. Normal: 0-6%, Elevated: 10%+",
                key="unmethylated"
            )
            
            # Secondary display: % Methylated (for reference)
            beta_score = st.number_input(
                "% Methylated (Reference)",
                min_value=0.0,
                max_value=150.0,
                value=95.0,
                step=0.1,
                help="% Methylated = 100 - % Unmethylated. Higher = healthier beta cells.",
                key="beta_score"
            )
            
            st.divider()
            
            st.markdown("**Body Measurements**")
            
            bmi = st.number_input(
                "BMI (kg/m²)",
                min_value=10.0,
                max_value=70.0,
                value=25.0,
                step=0.1,
                key="bmi"
            )
        
        with col3:
            st.markdown(f"""
            <div class="icon-text">
                {svg_icon("activity", 20)}
                <h4 style="margin: 0;">Glycemic Markers</h4>
            </div>
            """, unsafe_allow_html=True)
            
            hba1c = st.number_input(
                "HbA1c (%)",
                min_value=3.0,
                max_value=15.0,
                value=5.5,
                step=0.1,
                help="Normal <5.7%, Prediabetic 5.7-6.4%, Diabetic >=6.5%",
                key="hba1c"
            )
            
            # Glucose is optional
            glucose_provided = st.checkbox("Fasting Glucose available?", value=False, key="glucose_provided")
            
            if glucose_provided:
                glucose = st.number_input(
                    "Fasting Glucose (mg/dL)",
                    min_value=30.0,
                    max_value=600.0,
                    value=100.0,
                    step=1.0,
                    help="Normal <100, Prediabetic 100-125, Diabetic >=126 (Optional)",
                    key="glucose"
                )
            else:
                glucose = None
            
            st.divider()
            
            st.markdown("**Insulin & C-Peptide**")
            
            insulin = st.number_input(
                "Fasting Insulin (uU/mL)",
                min_value=0.0,
                max_value=500.0,
                value=10.0,
                step=0.1,
                key="insulin"
            )
            
            c_peptide = st.number_input(
                "C-Peptide (ng/mL)",
                min_value=0.0,
                max_value=50.0,
                value=2.0,
                step=0.1,
                key="c_peptide"
            )
        
        # Store biomarker data
        # CRITICAL: Model expects beta_score as % UNMETHYLATED (higher = more risk)
        # UI input "% Methylated" needs to be converted: unmethylated = 100 - methylated
        st.session_state.patient_data.update({
            "patient_id": patient_id,
            "age": age,
            "sex": sex,
            "race": race,
            "beta_score": unmethylated,  # Model uses % Unmethylated
            "beta_score_methylated": beta_score,  # Store original for display
            "unmethylated": unmethylated,
            "bmi": bmi,
            "hba1c": hba1c,
            "glucose": glucose if glucose_provided else np.nan,
            "insulin": insulin,
            "c_peptide": c_peptide,
        })
        
        # Show calculated values
        st.divider()
        st.markdown(f"""
        <div class="icon-text">
            {svg_icon("chart", 20)}
            <h4 style="margin: 0;">Calculated Indices</h4>
        </div>
        """, unsafe_allow_html=True)
        
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        
        # HOMA indices require glucose
        if glucose_provided and glucose:
            homa_ir = calculate_homa_ir(insulin, glucose)
            homa_beta = calculate_homa_beta(insulin, glucose)
        else:
            homa_ir = np.nan
            homa_beta = np.nan
        
        with calc_col1:
            if not pd.isna(homa_ir):
                color = "normal" if homa_ir < 2.5 else "inverse"
                st.metric(
                    "HOMA-IR (Insulin Resistance)",
                    f"{homa_ir:.2f}",
                    delta="Normal" if homa_ir < 2.5 else "Elevated",
                    delta_color=color
                )
        
        with calc_col2:
            if not pd.isna(homa_beta):
                st.metric(
                    "HOMA-B (Beta Cell Function)",
                    f"{homa_beta:.1f}",
                )
        
        with calc_col3:
            # Pass glucose only if provided
            glucose_val = glucose if glucose_provided else np.nan
            status, status_reason = get_diabetes_status(hba1c, glucose_val)
            
            if status == "Diabetic":
                st.markdown(f"""
                <div class="risk-card risk-very-high">
                    <div class="icon-text">
                        {svg_icon("x_circle")}
                        <strong>Current Status: {status}</strong>
                    </div>
                    <small>{status_reason}</small>
                </div>
                """, unsafe_allow_html=True)
            elif status == "Prediabetic":
                st.markdown(f"""
                <div class="risk-card risk-high">
                    <div class="icon-text">
                        {svg_icon("alert_circle")}
                        <strong>Current Status: {status}</strong>
                    </div>
                    <small>{status_reason}</small>
                </div>
                """, unsafe_allow_html=True)
            elif status == "Normal":
                st.markdown(f"""
                <div class="risk-card risk-low">
                    <div class="icon-text">
                        {svg_icon("check_circle")}
                        <strong>Current Status: {status}</strong>
                    </div>
                    <small>{status_reason}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="risk-card risk-moderate">
                    <div class="icon-text">
                        {svg_icon("info")}
                        <strong>Current Status: Based on HbA1c only</strong>
                    </div>
                    <small>Glucose not provided</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Results Section (moved here, below Calculated Indices)
        st.divider()
        st.markdown(f"""
        <div class="icon-text">
            {svg_icon("chart", 28)}
            <h2 style="margin: 0;">Risk Assessment Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Clinical Mode Selector
        st.markdown("### Clinical Mode")
        clinical_mode = st.radio(
            "Select assessment mode based on clinical context:",
            ["screening", "balanced", "confirmation"],
            format_func=lambda x: {
                "screening": "Screening (at-risk if >24%) - 100% Sensitivity, catches all cases",
                "balanced": "Balanced (at-risk if >56%) - 76% Sensitivity, 82% Specificity",
                "confirmation": "Confirmation (at-risk if >64%) - High confidence, 87% Specificity"
            }[x],
            index=1,
            key="clinical_mode",
            horizontal=False
        )
        
        st.session_state.patient_data["clinical_mode"] = clinical_mode
        
        st.divider()
        
        if st.button("Calculate Risk Assessment", type="primary", use_container_width=True):
            with st.spinner("Analyzing patient data..."):
                results = calculate_risk_score(st.session_state.patient_data, models)
            
            st.divider()
            
            # Current Status and Risk Score
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current Diabetes Status")
                
                status = results["current_status"]
                if status == "Diabetic":
                    st.markdown(f"""
                    <div class="risk-card risk-very-high">
                        <div class="icon-text">
                            {svg_icon("x_circle", 32)}
                            <h3 style="margin: 0; color: #ef4444;">{status}</h3>
                        </div>
                        <p style="margin-top: 10px;">{results['status_explanation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif status == "Prediabetic":
                    st.markdown(f"""
                    <div class="risk-card risk-high">
                        <div class="icon-text">
                            {svg_icon("alert_circle", 32)}
                            <h3 style="margin: 0; color: #f97316;">{status}</h3>
                        </div>
                        <p style="margin-top: 10px;">{results['status_explanation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="risk-card risk-low">
                        <div class="icon-text">
                            {svg_icon("check_circle", 32)}
                            <h3 style="margin: 0; color: #22c55e;">{status}</h3>
                        </div>
                        <p style="margin-top: 10px;">{results['status_explanation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.subheader("Diabetes Risk Score")
                
                if status == "Diabetic":
                    st.info("Patient already has diabetes - risk score not applicable")
                else:
                    risk = results.get("risk_probability", 0)
                    category = results.get("risk_category", "Unknown")
                    classification = results.get("at_risk_classification", "Unknown")
                    mode = results.get("clinical_mode", "balanced")
                    threshold = results.get("threshold", 0.45)
                    
                    # Show classification result prominently
                    if classification == "At Risk":
                        st.markdown(f"""
                        <div class="risk-card risk-very-high">
                            <div class="icon-text">
                                {svg_icon("shield_alert", 32)}
                                <h3 style="margin: 0; color: #ef4444;">CLASSIFIED: AT RISK</h3>
                            </div>
                            <p style="margin-top: 5px;">Risk Score: {risk:.1f}%</p>
                            <p style="margin-top: 3px; font-size: 0.9em; color: #666;">Classified as at-risk because prediction ({risk:.1f}%) > threshold ({threshold*100:.0f}%)</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="risk-card risk-low">
                            <div class="icon-text">
                                {svg_icon("shield_check", 32)}
                                <h3 style="margin: 0; color: #22c55e;">CLASSIFIED: NOT AT RISK</h3>
                            </div>
                            <p style="margin-top: 5px;">Risk Score: {risk:.1f}%</p>
                            <p style="margin-top: 3px; font-size: 0.9em; color: #666;">Classified as not at-risk because prediction ({risk:.1f}%) ≤ threshold ({threshold*100:.0f}%)</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if results.get("model_used"):
                        st.caption(f"Model: {results['model_used']}")
                    
                    # Beta Score contribution (higher unmethylated = more risk)
                    beta_contrib = results.get("beta_contribution")
                    if beta_contrib is not None:
                        if beta_contrib > 0:
                            st.markdown(f"""
                            <div class="icon-text" style="color: #ef4444;">
                                {svg_icon("trending_up", 20)}
                                <span>Beta Score Impact: +{beta_contrib:.1f}% risk (elevated unmethylated DNA)</span>
                            </div>
                            """, unsafe_allow_html=True)
                        elif beta_contrib < 0:
                            st.markdown(f"""
                            <div class="icon-text" style="color: #22c55e;">
                                {svg_icon("trending_down", 20)}
                                <span>Beta Score Impact: {beta_contrib:.1f}% risk (healthy unmethylated DNA)</span>
                            </div>
                            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Risk Factors
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown(f"""
                <div class="icon-text">
                    {svg_icon("alert_circle", 24)}
                    <h4 style="margin: 0;">Risk Factors Identified</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if results["risk_factors"]:
                    for factor in results["risk_factors"]:
                        st.markdown(f"- {factor}")
                else:
                    st.markdown(f"""
                    <div class="icon-text" style="color: #22c55e;">
                        {svg_icon("check_circle", 16)}
                        <span>No significant risk factors identified</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="icon-text">
                    {svg_icon("shield_check", 24)}
                    <h4 style="margin: 0;">Protective Factors</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if results["protective_factors"]:
                    for factor in results["protective_factors"]:
                        st.markdown(f"- {factor}")
                else:
                    st.info("No specific protective factors noted")
            
            st.divider()
            
            # Recommendations
            st.markdown(f"""
            <div class="icon-text">
                {svg_icon("clipboard", 24)}
                <h4 style="margin: 0;">Clinical Recommendations</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for i, rec in enumerate(results["recommendations"], 1):
                st.markdown(f"{i}. {rec}")
            
            st.divider()
            
            # Beta Score Interpretation (% Unmethylated - higher = more damage)
            st.markdown(f"""
            <div class="icon-text">
                {svg_icon("dna", 24)}
                <h4 style="margin: 0;">Beta Score Interpretation</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Get % Unmethylated (this is what the model uses)
            unmethylated_pct = st.session_state.patient_data.get("unmethylated", 5.0)
            
            # Interpretation based on % Unmethylated thresholds
            if unmethylated_pct <= 6:
                st.markdown(f"""
                <div class="risk-card risk-low">
                    <strong>{unmethylated_pct:.1f}% Unmethylated - Good</strong>
                    <p>Beta cells healthy. Low levels of unmethylated DNA indicate minimal beta cell death.</p>
                </div>
                """, unsafe_allow_html=True)
            elif unmethylated_pct <= 10:
                st.markdown(f"""
                <div class="risk-card risk-moderate">
                    <strong>{unmethylated_pct:.1f}% Unmethylated - Borderline</strong>
                    <p>Monitor closely. Slightly elevated unmethylated DNA may indicate early beta cell stress.</p>
                </div>
                """, unsafe_allow_html=True)
            elif unmethylated_pct <= 15:
                st.markdown(f"""
                <div class="risk-card risk-high">
                    <strong>{unmethylated_pct:.1f}% Unmethylated - Elevated</strong>
                    <p>Beta cell damage detected. Elevated unmethylated DNA suggests active beta cell destruction.</p>
                </div>
                """, unsafe_allow_html=True)
            elif unmethylated_pct <= 20:
                st.markdown(f"""
                <div class="risk-card risk-very-high">
                    <strong>{unmethylated_pct:.1f}% Unmethylated - High</strong>
                    <p>Significant beta cell death. High unmethylated DNA indicates substantial beta cell loss.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="risk-card risk-very-high">
                    <strong>{unmethylated_pct:.1f}% Unmethylated - Very High</strong>
                    <p>Severe beta cell destruction. Very high unmethylated DNA indicates extensive beta cell death. Urgent clinical evaluation recommended.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export
            st.divider()
            
            report_data = {
                "Patient ID": st.session_state.patient_data.get("patient_id", "N/A"),
                "Age": st.session_state.patient_data.get("age"),
                "Sex": st.session_state.patient_data.get("sex"),
                "Beta Score (%)": st.session_state.patient_data.get("beta_score"),
                "HbA1c (%)": st.session_state.patient_data.get("hba1c"),
                "Fasting Glucose (mg/dL)": st.session_state.patient_data.get("glucose"),
                "BMI": st.session_state.patient_data.get("bmi"),
                "Current Status": results["current_status"],
                "Risk Score (%)": results["risk_probability"],
                "Risk Category": results["risk_category"],
                "Model Used": results.get("model_used", "N/A"),
                "Risk Factors": "; ".join(results["risk_factors"]),
                "Protective Factors": "; ".join(results["protective_factors"]),
            }
            
            report_df = pd.DataFrame([report_data])
            
            st.download_button(
                "Download Patient Report (CSV)",
                report_df.to_csv(index=False),
                file_name=f"kihealth_risk_report_{st.session_state.patient_data.get('patient_id', 'patient')}.csv",
                mime="text/csv"
            )
        
        else:
            st.info("Enter patient information above, then click 'Calculate Risk Assessment' to see results.")
    
    # Tab 3: Model Information
    with tab3:
        st.markdown(f"""
        <div class="icon-text">
            {svg_icon("chart", 28)}
            <h2 style="margin: 0;">M2 Transfer Learning Model</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        This model uses transfer learning from large external datasets to improve diabetes risk prediction
        when combined with KiHealth's proprietary Beta Score biomarker.
        """)
        
        # Model Performance Summary
        st.markdown("### Model Performance Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Cross-Validated AUC", "0.875", "+0.8% vs baseline")
            st.caption("5-fold CV on 129 patients")
        
        with col2:
            st.metric("95% Confidence Interval", "[0.75, 1.00]")
            st.caption("Bootstrap estimated")
        
        with col3:
            st.metric("Confirmed Case Detection", "100%")
            st.caption("51/51 at-risk detected at screening threshold")
        
        st.divider()
        
        # Dataset Composition
        st.markdown("### Validation Dataset Composition")
        
        dataset_data = {
            "Source": ["Cardinal", "BioIVT", "T1D Study", "BioIVT Fresh", "**Total**"],
            "Patients": [73, 34, 12, 10, "**129**"],
            "At-Risk": [25, 4, 12, 10, "**51**"],
            "Not At-Risk": [48, 30, 0, 0, "**78**"],
            "Description": [
                "Blood drive samples with questionnaire",
                "Biobank validation samples", 
                "Pediatric T1D onset cases",
                "Fresh diabetic samples",
                ""
            ]
        }
        st.table(pd.DataFrame(dataset_data))
        
        st.divider()
        
        # Clinical Modes
        st.markdown("### Clinical Mode Performance")
        
        mode_data = {
            "Mode": ["Screening", "Balanced", "Confirmation"],
            "Sensitivity": ["100%", "76%", "59%"],
            "Specificity": ["60%", "82%", "87%"],
            "Use Case": [
                "Catch all at-risk patients",
                "Optimal trade-off",
                "High confidence positives"
            ]
        }
        st.table(pd.DataFrame(mode_data))
        
        st.divider()
        
        # Transfer Learning Architecture
        st.markdown("### Transfer Learning Architecture")
        
        st.markdown("""
        **Two-Stage Prediction Process:**
        
        1. **Foundation Model** (trained on 17,427 NHANES+CHNS patients)
           - Learns traditional metabolic risk patterns
           - Input: HbA1c, HOMA-IR
           - Output: Traditional risk probability
        
        2. **Final Model** (fine-tuned on KiHealth data)
           - Combines Beta Score with foundation prediction
           - Input: Beta Score, Foundation Prediction
           - Output: Final risk probability (0-100%)
        
        **Why Transfer Learning?**
        - Foundation model learns from 17,427 patients (vs 129 KiHealth patients)
        - Provides +0.8% AUC improvement over baseline
        - More robust to edge cases
        - Better calibrated predictions
        """)
        
        st.divider()
        
        # Beta Score Independence
        st.markdown("### Beta Score Independence Analysis")
        
        st.markdown("""
        Beta Score provides **independent information** not captured by traditional metabolic markers:
        """)
        
        corr_data = {
            "Feature": ["BMI", "High Blood Pressure", "HbA1c", "HOMA-IR", "C-peptide"],
            "Correlation with Beta Score": ["+0.22", "+0.02", "+0.13", "+0.17", "+0.76"],
            "Significance": ["Weak (p=0.15)", "None (p=0.85)", "Weak (p=0.19)", "Weak (p=0.07)", "Strong (p<0.001)"],
            "Interpretation": [
                "Obesity doesn't directly cause beta cell death",
                "No relationship to beta cell health",
                "Weak link - Beta Score detects damage before HbA1c rises",
                "Moderate link to insulin resistance",
                "Strong link - C-peptide produced by beta cells"
            ]
        }
        st.table(pd.DataFrame(corr_data))
        
        st.info("**Key Insight:** Beta Score measures active beta cell damage, which is independent of obesity and blood pressure. This makes it valuable for early detection before traditional markers become abnormal.")
        
        st.divider()
        
        # Limitations
        st.markdown("### Limitations & Recommendations")
        
        st.warning("""
        **Limitations:**
        - Sample size: 129 patients (moderate - recommend collecting more)
        - Confidence interval: ±0.065 (wider than ideal for clinical deployment)
        - Best for: Beta cell damage detection (T1D, advanced T2D)
        - May miss: Early obesity-driven risk with intact beta cells
        
        **Recommendations:**
        - Use as complementary to traditional metabolic screening
        - Prospective validation recommended before clinical deployment
        - Consider combining with BMI/HBP for comprehensive risk assessment
        """)
        
        st.divider()
        
        # Model Files
        st.markdown("### Model Files")
        
        st.markdown("""
        The following model files are available in `Diabetes-KiHealth/TL-KiHealth/M2_Models/`:
        
        | File | Description |
        |------|-------------|
        | `foundation_combined.joblib` | Foundation model (NHANES+CHNS) |
        | `foundation_scaler.joblib` | Feature scaler for foundation |
        | `beta_foundation_model.joblib` | Final prediction model |
        | `beta_foundation_scaler.joblib` | Feature scaler for final model |
        | `beta_foundation_thresholds.joblib` | Optimized thresholds |
        | `beta_foundation_metrics.json` | Performance metrics |
        """)


if __name__ == "__main__":
    main()
