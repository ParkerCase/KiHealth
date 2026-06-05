#!/usr/bin/env python3
# Deployed via Streamlit Community Cloud
# Auto-deploys on push to main branch of connected GitHub repo
# Model files are committed to repo (total ~7MB, acceptable for Streamlit Cloud)
"""
KiHealth Diabetes Risk Calculator UI

A comprehensive patient assessment tool that:
1. Collects pre-qualifying questionnaire responses
2. Gathers biomarker data (Beta Score, HbA1c, insulin, glucose, BMI, etc.)
3. Calculates current diabetes status (diabetic/prediabetic/normal)
4. Predicts diabetes risk using KiHealth's Beta Score model
5. Provides personalized recommendations
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

TL_KIHEALTH_DIR = os.path.join(BASE_DIR, "Diabetes-KiHealth", "TL-KiHealth")
BUNDLED_MODEL_DIR = os.path.join(APP_DIR, "models", "m2")
REPO_MODEL_DIR = os.path.join(TL_KIHEALTH_DIR, "M2_Models")


def _resolve_model_dir() -> str | None:
    """Prefer bundled models next to the app (Streamlit Cloud); fall back to repo path."""
    bundled_core = [
        "foundation_combined.joblib",
        "foundation_scaler.joblib",
        "m2b_final_clean_model_calibrated.joblib",
        "m2b_final_clean_scaler.joblib",
    ]
    for candidate in (BUNDLED_MODEL_DIR, REPO_MODEL_DIR):
        if all(os.path.isfile(os.path.join(candidate, name)) for name in bundled_core):
            return candidate
    return None


MODEL_DIR = _resolve_model_dir() or REPO_MODEL_DIR

# Legacy fallback model paths
FINAL_MODEL_PATH = os.path.join(TL_KIHEALTH_DIR, "final_model_calibrated.joblib")
FINAL_THRESHOLDS_PATH = os.path.join(TL_KIHEALTH_DIR, "final_thresholds.joblib")
ENSEMBLE_MODEL_PATH = os.path.join(TL_KIHEALTH_DIR, "ensemble_model_calibrated.joblib")
ENSEMBLE_THRESHOLD_PATH = os.path.join(TL_KIHEALTH_DIR, "ensemble_threshold.joblib")

# M2-B enhanced transfer learning model paths (production)
# Validated on 129 patients; AUC ~0.896, 95% CI [0.85, 0.95]; 5 features incl. direct HbA1c
# Foundation trained on 23,716 NHANES+CHNS patients using HbA1c + Age + BMI
M2_FOUNDATION_PATH = os.path.join(MODEL_DIR, "foundation_combined.joblib")
M2_FOUNDATION_SCALER_PATH = os.path.join(MODEL_DIR, "foundation_scaler.joblib")
M2_BETA_MODEL_PATH = os.path.join(MODEL_DIR, "m2b_final_clean_model_calibrated.joblib")
M2_BETA_SCALER_PATH = os.path.join(MODEL_DIR, "m2b_final_clean_scaler.joblib")
M2_THRESHOLDS_PATH = os.path.join(MODEL_DIR, "m2b_final_clean_thresholds.joblib")
M2_METRICS_PATH = os.path.join(MODEL_DIR, "m2b_final_clean_metrics.json")

# Deploy marker — visible in app footer; bump when forcing Streamlit Cloud redeploy
DEPLOY_VERSION = "2026-06-05-m2b-metrics-thresholds"
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


def _pct_metric(x, default=0.0):
    """Format a 0-1 metric as integer percent string."""
    if isinstance(x, (int, float)):
        return f"{int(round(x * 100))}%"
    return str(x)


def _get_m2_threshold_info(models: dict) -> dict:
    """Clinical mode thresholds and performance from m2b_final_clean_metrics.json."""
    th = (models.get("m2_metrics") or {}).get("thresholds", {})
    defaults = {
        "screening": {"threshold": 0.09, "sensitivity": 0.98, "specificity": 0.49},
        "balanced": {"threshold": 0.35, "sensitivity": 0.76, "specificity": 0.81},
        "confirmation": {"threshold": 0.47, "sensitivity": 0.71, "specificity": 0.87},
    }
    info = {}
    for mode, default in defaults.items():
        entry = th.get(mode, {})
        if not isinstance(entry, dict):
            entry = {}
        threshold = entry.get("threshold", default["threshold"])
        sensitivity = entry.get("sensitivity", default["sensitivity"])
        specificity = entry.get("specificity", default["specificity"])
        info[mode] = {
            "threshold": threshold,
            "threshold_pct": int(round(threshold * 100)),
            "sensitivity": sensitivity,
            "specificity": specificity,
            "sensitivity_pct": int(round(sensitivity * 100)),
            "specificity_pct": int(round(specificity * 100)),
        }
    return info


def _clinical_mode_label(mode: str, mode_info: dict) -> str:
    """Radio label for a clinical mode using metrics-driven cutoffs."""
    m = mode_info[mode]
    if mode == "screening":
        return (
            f"Screening (at-risk if >{m['threshold_pct']}%) - "
            f"{m['sensitivity_pct']}% Sensitivity, {m['specificity_pct']}% Specificity, "
            "catches nearly all cases"
        )
    if mode == "balanced":
        return (
            f"Balanced (at-risk if >{m['threshold_pct']}%) - "
            f"{m['sensitivity_pct']}% Sensitivity, {m['specificity_pct']}% Specificity"
        )
    return (
        f"Confirmation (at-risk if >{m['threshold_pct']}%) - "
        f"{m['sensitivity_pct']}% Sensitivity, {m['specificity_pct']}% Specificity, "
        "high confidence"
    )


def svg_icon(name: str, size: int = 24) -> str:
    """Return SVG icon HTML with optional size adjustment."""
    svg = SVG_ICONS.get(name, SVG_ICONS["info"])
    if size != 24:
        svg = svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    return svg


def _load_joblib(model_path: str, required: bool = True):
    """Load a joblib artifact; return (obj, error_message)."""
    import joblib

    if not os.path.isfile(model_path):
        msg = (
            f"Model file not found: `{model_path}`. "
            "Ensure `kihealth_ui/models/m2/*.joblib` is committed on GitHub."
        )
        return (None, msg) if required else (None, None)
    try:
        return joblib.load(model_path), None
    except Exception as exc:
        import sklearn

        msg = (
            f"Failed to load `{model_path}`: {exc}. "
            f"Runtime scikit-learn={sklearn.__version__}. "
            "Pinned requirements: scikit-learn==1.5.2 (see root requirements.txt)."
        )
        return (None, msg) if required else (None, None)


@st.cache_resource(show_spinner="Loading M2-B models…")
def load_models():
    """Load the prediction models."""
    models = {"m2_available": False, "load_errors": [], "loaded_paths": {}}
    model_dir = _resolve_model_dir()

    if model_dir is None:
        models["load_errors"].append(
            "M2-B model files not found. Expected bundled path "
            f"`kihealth_ui/models/m2/` or repo path `{REPO_MODEL_DIR}`. "
            f"App directory: `{APP_DIR}`. Repository root: `{BASE_DIR}`."
        )
        return models

    m2_core = {
        "m2_foundation": "foundation_combined.joblib",
        "m2_foundation_scaler": "foundation_scaler.joblib",
        "m2_beta_model": "m2b_final_clean_model_calibrated.joblib",
        "m2_beta_scaler": "m2b_final_clean_scaler.joblib",
    }
    for key, filename in m2_core.items():
        path = os.path.join(model_dir, filename)
        obj, err = _load_joblib(path)
        if err:
            models["load_errors"].append(err)
            return models
        models[key] = obj
        models["loaded_paths"][filename] = path

    thresholds_path = os.path.join(model_dir, "m2b_final_clean_thresholds.joblib")
    metrics_path = os.path.join(model_dir, "m2b_final_clean_metrics.json")
    models["loaded_paths"]["m2b_final_clean_thresholds.joblib"] = thresholds_path
    models["loaded_paths"]["m2b_final_clean_metrics.json"] = metrics_path
    if os.path.isfile(thresholds_path):
        thresholds, _ = _load_joblib(thresholds_path, required=False)
        if thresholds is not None:
            models["m2_thresholds"] = thresholds
    if os.path.isfile(metrics_path):
        with open(metrics_path) as f:
            models["m2_metrics"] = json.load(f)

    models["m2_available"] = True
    models["m2_model_dir"] = model_dir

    if not models.get("m2_available"):
        if os.path.isfile(FINAL_MODEL_PATH):
            final_model, _ = _load_joblib(FINAL_MODEL_PATH, required=False)
            if final_model is not None:
                models["final"] = final_model
            if os.path.isfile(FINAL_THRESHOLDS_PATH):
                thresholds, _ = _load_joblib(FINAL_THRESHOLDS_PATH, required=False)
                if thresholds is not None:
                    models["thresholds"] = thresholds
        elif os.path.isfile(ENSEMBLE_MODEL_PATH):
            ensemble, _ = _load_joblib(ENSEMBLE_MODEL_PATH, required=False)
            if ensemble is not None:
                models["ensemble"] = ensemble
            if os.path.isfile(ENSEMBLE_THRESHOLD_PATH):
                threshold, _ = _load_joblib(ENSEMBLE_THRESHOLD_PATH, required=False)
                if threshold is not None:
                    models["ensemble_threshold"] = threshold

    return models


def _render_model_load_failure(models: dict) -> None:
    """Show a clear error instead of a Streamlit StopException traceback."""
    st.error("Could not load the M2-B prediction models.")
    for msg in models.get("load_errors", []):
        st.markdown(msg)

    bundled = BUNDLED_MODEL_DIR
    repo = REPO_MODEL_DIR
    st.markdown("**Deploy diagnostics**")
    st.code(
        "\n".join(
            [
                f"DEPLOY_VERSION={DEPLOY_VERSION}",
                f"APP_DIR={APP_DIR}",
                f"BASE_DIR={BASE_DIR}",
                f"BUNDLED_MODEL_DIR={bundled} exists={os.path.isdir(bundled)}",
                f"REPO_MODEL_DIR={repo} exists={os.path.isdir(repo)}",
                "Bundled files:",
                *[
                    f"  {name}: {os.path.isfile(os.path.join(bundled, name))}"
                    for name in (
                        "foundation_combined.joblib",
                        "foundation_scaler.joblib",
                        "m2b_final_clean_model_calibrated.joblib",
                        "m2b_final_clean_scaler.joblib",
                    )
                ],
            ]
        )
    )
    try:
        import sklearn

        st.caption(f"Runtime: Python {sys.version.split()[0]}, scikit-learn {sklearn.__version__}")
    except Exception:
        pass
    st.info(
        "On share.streamlit.io: open **Manage app → Reboot app**, confirm main file is "
        "`kihealth_ui/risk_calculator.py`, branch `main`, and requirements `requirements.txt`."
    )


def predict_with_m2_model(data: dict, models: dict) -> dict:
    """
    Predict using M2-B enhanced transfer learning model.
    Two-stage: Foundation (HbA1c, Age, BMI) then Final
    (Beta Score + foundation pred + insulin + C-peptide + HbA1c direct).
    Missing insulin/C-peptide/HbA1c fall back to training medians from metrics.
    """
    metrics = models.get("m2_metrics", {})
    auc_label = f"{metrics.get('cv_auc_mean', 0.896):.2f}" if metrics else "0.90"
    result = {
        "probability": None,
        "foundation_pred": None,
        "model_name": f"M2-B Enhanced Transfer Learning (AUC: {auc_label})"
    }
    
    beta_score = data.get("beta_score")  # % Unmethylated
    hba1c = data.get("hba1c")
    age = data.get("age")
    bmi = data.get("bmi")
    
    if beta_score is None or hba1c is None:
        return result
    
    if age is None:
        age = metrics.get("median_age", 50)
    if bmi is None:
        bmi = metrics.get("median_bmi", 27.5)
    
    try:
        # Stage 1: Foundation (HbA1c + Age + BMI)
        X_foundation = pd.DataFrame([[hba1c, age, bmi]], columns=['hba1c_percent', 'age_years', 'bmi_kg_m2'])
        X_foundation_scaled = models["m2_foundation_scaler"].transform(X_foundation)
        foundation_pred = models["m2_foundation"].predict_proba(X_foundation_scaled)[0, 1]
        result["foundation_pred"] = foundation_pred
        
        # Stage 2: Final model (4 or 5 features)
        scaler = models["m2_beta_scaler"]
        n_features = getattr(scaler, "n_features_in_", 2)
        insulin = data.get("insulin")
        cpeptide = data.get("c_peptide")
        if insulin is None or (isinstance(insulin, float) and np.isnan(insulin)):
            insulin = metrics.get("median_insulin", 21.0)
        if cpeptide is None or (isinstance(cpeptide, float) and np.isnan(cpeptide)):
            cpeptide = metrics.get("median_cpeptide", 2.9)
        if n_features >= 5:
            hba1c_val = hba1c if hba1c is not None else metrics.get("median_hba1c", 5.7)
            X_final = pd.DataFrame(
                [[beta_score, foundation_pred, float(insulin), float(cpeptide), float(hba1c_val)]],
                columns=['beta_score', 'foundation_pred', 'insulin', 'cpeptide', 'hba1c'],
            )
        elif n_features == 4:
            X_final = pd.DataFrame(
                [[beta_score, foundation_pred, float(insulin), float(cpeptide)]],
                columns=['beta_score', 'foundation_pred', 'insulin', 'cpeptide'],
            )
        else:
            X_final = pd.DataFrame([[beta_score, foundation_pred]], columns=['beta_score', 'foundation_pred'])
        X_final_scaled = scaler.transform(X_final)
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
                
                # M2 thresholds and performance (from loaded file or fallback for n=129 model)
                m2_metrics = models.get("m2_metrics", {})
                mode_info = _get_m2_threshold_info(models)
                m2_thresholds = {mode: mode_info[mode]["threshold"] for mode in mode_info}
                threshold = m2_thresholds.get(clinical_mode, 0.35)

                m2_performance = {
                    mode: {
                        "sens": _pct_metric(mode_info[mode]["sensitivity"]),
                        "spec": _pct_metric(mode_info[mode]["specificity"]),
                        "desc": {
                            "screening": "Catches nearly all at-risk patients",
                            "balanced": "Optimal trade-off",
                            "confirmation": "High confidence positives",
                        }[mode],
                    }
                    for mode in mode_info
                }
                perf = m2_performance.get(clinical_mode, m2_performance["balanced"])
                results["model_used"] = f"{m2_result['model_name']} - {clinical_mode.title()} Mode (Sens: {perf['sens']}, Spec: {perf['spec']})"
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
        # Split so clinicians can use the right set: T2D/metabolic vs T1D/autoimmune
        results["recommendations_t2"] = [
            "Lifestyle intervention is critical - can reduce progression risk by 58% (DPP evidence)",
            "Target 7% weight loss if overweight",
            "150 minutes/week of moderate physical activity",
            "Consider metformin if high-risk (discuss with physician)",
            "Retest HbA1c in 3-6 months",
        ]
        results["recommendations_t1"] = [
            "Consider diabetes autoantibody testing (GAD-65, IA-2, ZnT8) if clinical concern for T1D",
            "Retest HbA1c and/or C-peptide in 3-6 months as indicated",
        ]
        results["recommendations"] = results["recommendations_t2"]  # default display; UI shows both blocks
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
        page_title="KiHealth Diabetes Risk Calculator (M2-B)",
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
    if not models.get("m2_available"):
        _render_model_load_failure(models)
        st.caption(f"Deploy version: {DEPLOY_VERSION}")
        return
    if models.get("m2_available"):
        m2_metrics = models.get("m2_metrics", {})
        auc_str = f"{m2_metrics.get('cv_auc_mean', 0.896):.2f}" if m2_metrics else "0.90"
        ci = m2_metrics.get("ci_lower"), m2_metrics.get("ci_upper")
        ci_str = f"[{ci[0]:.2f}, {ci[1]:.2f}]" if (ci[0] is not None and ci[1] is not None) else "[0.85, 0.95]"
        st.markdown(f"""
        <div class="icon-text" style="color: #22c55e;">
            {svg_icon("shield_check", 20)}
            <span><strong>M2-B Enhanced Transfer Learning Model loaded:</strong> AUC {auc_str} (CV) | 95% CI {ci_str} | 129 patients</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Transfer learning from 23,716 NHANES+CHNS (HbA1c, Age, BMI). Optional insulin + C-peptide; medians used when missing.")
        st.caption("Enhanced with direct HbA1c feature")
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

            beta_score = unmethylated  # % Unmethylated (model input)
            if beta_score is not None:
                methylated = 100.0 - float(beta_score)
                st.metric(
                    label="% Methylated (calculated)",
                    value=f"{methylated:.1f}%",
                    help="Calculated as 100% minus % Unmethylated",
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
        st.session_state.patient_data.update({
            "patient_id": patient_id,
            "age": age,
            "sex": sex,
            "race": race,
            "beta_score": unmethylated,  # Model uses % Unmethylated only
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
        mode_info = _get_m2_threshold_info(models)
        clinical_mode = st.radio(
            "Select assessment mode based on clinical context:",
            ["screening", "balanced", "confirmation"],
            format_func=lambda x: _clinical_mode_label(x, mode_info),
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
            
            if "recommendations_t2" in results and "recommendations_t1" in results:
                st.markdown("**If metabolic / type 2 diabetes risk:**")
                for i, rec in enumerate(results["recommendations_t2"], 1):
                    st.markdown(f"{i}. {rec}")
                st.markdown("**If type 1 / autoimmune diabetes concern:**")
                for i, rec in enumerate(results["recommendations_t1"], 1):
                    st.markdown(f"{i}. {rec}")
                st.caption("Use the set that fits clinical context. Beta Score can reflect beta cell damage from either T1D or T2D.")
            else:
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
            <h2 style="margin: 0;">M2-B Transfer Learning Model</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        This model uses transfer learning from large external datasets to improve diabetes risk prediction
        when combined with KiHealth's proprietary Beta Score biomarker.
        """)
        
        # Model Performance Summary
        st.markdown("### Model Performance Summary")
        m2_metrics = models.get("m2_metrics", {})
        auc_val = f"{m2_metrics.get('cv_auc_mean', 0.896):.2f}" if m2_metrics else "0.90"
        ci_lo = m2_metrics.get("ci_lower")
        ci_hi = m2_metrics.get("ci_upper")
        ci_val = f"[{ci_lo:.2f}, {ci_hi:.2f}]" if (ci_lo is not None and ci_hi is not None) else "[0.85, 0.95]"
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cross-Validated AUC", auc_val)
            st.caption("5-fold CV on 129 patients")
        with col2:
            st.metric("95% Confidence Interval", ci_val)
            st.caption("Bootstrap (n=1000)")
        with col3:
            st.metric("Screening sensitivity", "98%")
            st.caption("At screening threshold (50/51 at-risk)")
        st.caption("Enhanced with direct HbA1c feature")
        
        st.divider()
        
        # Dataset Composition
        st.markdown("### Validation Dataset Composition")
        
        dataset_data = {
            "Source": ["Cardinal", "V1 Validation", "T1D Study", "BioIVT Fresh", "**Total**"],
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
        
        # Clinical Modes (from metrics when available)
        st.markdown("### Clinical Mode Performance")
        mode_info = _get_m2_threshold_info(models)
        mode_data = {
            "Mode": ["Screening", "Balanced", "Confirmation"],
            "Threshold": [
                f">{mode_info['screening']['threshold_pct']}%",
                f">{mode_info['balanced']['threshold_pct']}%",
                f">{mode_info['confirmation']['threshold_pct']}%",
            ],
            "Sensitivity": [
                _pct_metric(mode_info["screening"]["sensitivity"]),
                _pct_metric(mode_info["balanced"]["sensitivity"]),
                _pct_metric(mode_info["confirmation"]["sensitivity"]),
            ],
            "Specificity": [
                _pct_metric(mode_info["screening"]["specificity"]),
                _pct_metric(mode_info["balanced"]["specificity"]),
                _pct_metric(mode_info["confirmation"]["specificity"]),
            ],
            "Use Case": [
                "Catch nearly all at-risk patients",
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
        
        1. **Foundation Model** (trained on 23,716 NHANES+CHNS patients)
           - Learns traditional metabolic risk patterns
           - Input: HbA1c, Age, BMI
           - Output: Traditional risk probability
           - **No glucose measurement required**
        
        2. **Final Model** (fine-tuned on KiHealth data)
           - Combines Beta Score with foundation prediction (and optionally insulin + C-peptide; medians used when missing)
           - Input: Beta Score, Foundation Prediction, optional Insulin, optional C-peptide
           - Output: Final risk probability (0-100%)
        
        **Why Transfer Learning?**
        - Foundation model learns from 23,716 patients (vs 129 KiHealth patients)
        - Uses features KiHealth collects (HbA1c, Age, BMI, Beta Score); insulin and C-peptide optional (no extra testing required when missing)
        - More robust to edge cases
        - Better calibrated predictions
        """)
        
        st.divider()
        
        # Foundation Model Demographics
        st.markdown("### Foundation Model Demographics")
        
        st.markdown("""
        The foundation model was trained on **23,716 patients** from two nationally representative datasets:
        - **NHANES** (National Health and Nutrition Examination Survey): 14,486 US patients
        - **CHNS** (China Health and Nutrition Survey): 9,230 Chinese patients
        """)
        
        # Create two columns for pie charts
        demo_col1, demo_col2 = st.columns(2)
        
        with demo_col1:
            st.markdown("#### Race/Ethnicity (NHANES)")
            # Race/ethnicity data
            race_data = {
                "Race/Ethnicity": ["Non-Hispanic White", "Non-Hispanic Black", "Mexican American", 
                                   "Other Hispanic", "Non-Hispanic Asian", "Other"],
                "Count": [5946, 2865, 1926, 1564, 1482, 703],
                "Percentage": ["41.0%", "19.8%", "13.3%", "10.8%", "10.2%", "4.9%"]
            }
            st.table(pd.DataFrame(race_data))
            
            st.success("**White patients are the largest group (41%)** - NHANES is nationally representative, not skewed toward any single demographic.")
        
        with demo_col2:
            st.markdown("#### Data Sources")
            source_data = {
                "Source": ["NHANES (US)", "CHNS (China)"],
                "Patients": ["14,486", "9,230"],
                "Percentage": ["61%", "39%"]
            }
            st.table(pd.DataFrame(source_data))
            
            st.info("**Combined US + Chinese data** provides cross-population validation of metabolic patterns.")
        
        # Additional demographics table
        st.markdown("#### Comprehensive Demographics Summary")
        
        demo_summary = {
            "Demographic": [
                "Age Range", 
                "Mean Age",
                "Female",
                "Male",
                "Normal BMI (18.5-25)",
                "Overweight (25-30)",
                "Obese (≥30)",
                "Pediatric (<18)",
                "Working Age (18-65)",
                "Elderly (65+)"
            ],
            "NHANES (US)": [
                "12-80 years",
                "45.7 years",
                "7,588 (52.4%)",
                "6,898 (47.6%)",
                "4,353 (30.0%)",
                "4,364 (30.1%)",
                "5,293 (36.5%)",
                "1,757 (12.1%)",
                "9,456 (65.3%)",
                "3,273 (22.6%)"
            ],
            "CHNS (China)": [
                "0-99 years",
                "47.2 years",
                "4,873 (52.8%)",
                "4,357 (47.2%)",
                "5,812 (63.0%)",
                "2,401 (26.0%)",
                "1,017 (11.0%)",
                "892 (9.7%)",
                "5,985 (64.8%)",
                "2,353 (25.5%)"
            ]
        }
        st.table(pd.DataFrame(demo_summary))
        
        # Key points about NHANES
        st.markdown("#### Why NHANES is Nationally Representative")
        
        st.markdown("""
        - NHANES is conducted by the **CDC's National Center for Health Statistics**
        - Uses **complex, multi-stage probability sampling** to represent the entire US population
        - Participants are **randomly selected from US households** across all income levels
        - **Intentional oversampling of minorities** ensures statistical power for subgroup analysis
        - This is a **methodological strength**, not a bias - it means the model is validated across all demographic groups
        
        **Comparison to US Census (2020):**
        | Group | US Population | Our NHANES Data |
        |-------|---------------|-----------------|
        | White | ~60% | 41% |
        | Hispanic | ~19% | 24% |
        | Black | ~13% | 20% |
        | Asian | ~6% | 10% |
        
        The slight differences are due to intentional oversampling for statistical validity, ensuring robust predictions across all groups.
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
            "Significance": ["Weak (p=0.15)", "None (p=0.85)", "Weak (p=0.19)", "Moderate (p=0.07)", "Strong (p<0.001)"],
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
        - 95% CI: [0.85, 0.95] - reasonable but would narrow with more data
        - Best for: Beta cell damage detection (T1D, advanced T2D)
        - May miss: Early obesity-driven risk with intact beta cells
        
        **Recommendations:**
        - Use as complementary to traditional metabolic screening
        - Prospective validation recommended before clinical deployment
        - Model now uses Age + BMI which captures obesity-related risk
        """)
        
        st.divider()
        
        # Model Files
        st.markdown("### Model Files")
        
        st.markdown("""
        The following M2-B model files are available in `Diabetes-KiHealth/TL-KiHealth/M2_Models/`:
        
        | File | Description |
        |------|-------------|
        | `foundation_combined.joblib` | Foundation model (NHANES+CHNS) |
        | `foundation_scaler.joblib` | Feature scaler for foundation |
        | `foundation_combined.joblib` | Foundation model (NHANES+CHNS) |
        | `foundation_scaler.joblib` | Feature scaler for foundation |
        | `m2b_final_clean_model_calibrated.joblib` | Final prediction model (5 features) |
        | `m2b_final_clean_scaler.joblib` | Feature scaler for final model |
        | `m2b_final_clean_thresholds.joblib` | Optimized thresholds |
        | `m2b_final_clean_metrics.json` | Performance metrics |
        """)


if __name__ == "__main__":
    main()
