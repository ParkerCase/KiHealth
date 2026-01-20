"""
Vercel serverless function for DOC model validation
Handles CSV upload, preprocessing, prediction, and visualization
"""

from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import numpy as np
import joblib
import io
from sklearn.metrics import roc_auc_score, roc_curve, brier_score_loss
from sklearn.calibration import calibration_curve
import sys
import os

# Add parent directory to path to import preprocessing
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from preprocessing import preprocess_data, validate_data
from api.success_calculation import (
    calculate_success_metrics,
    calculate_success_category,
    get_success_probability,
)

# Load models lazily (only when needed) to reduce initial bundle size
MODEL_DIR = None
RF_MODEL = None
RF_MODEL_ORIGINAL = None  # Original pure data-driven model
RF_MODEL_CALIBRATED = None  # Literature-calibrated model
SCALER = None
IMPUTER = None
FEATURE_NAMES = None
OUTCOME_MODEL = None


def _initialize_model_dir():
    """Initialize MODEL_DIR by finding the models directory"""
    global MODEL_DIR
    if MODEL_DIR is not None:
        return
    
    func_dir = os.path.dirname(__file__)
    api_models_path = os.path.join(func_dir, "models")
    root_models_path = os.path.join(os.path.dirname(func_dir), "models")
    
    # Check which path exists (look for any model file)
    if os.path.exists(api_models_path) and os.listdir(api_models_path):
        MODEL_DIR = api_models_path
    elif os.path.exists(root_models_path) and os.listdir(root_models_path):
        MODEL_DIR = root_models_path
    else:
        raise Exception(f"Models directory not found. Checked: {api_models_path}, {root_models_path}")


def _load_original_model():
    """Load the original pure data-driven model"""
    global RF_MODEL_ORIGINAL, MODEL_DIR, SCALER, FEATURE_NAMES
    
    if MODEL_DIR is None:
        _initialize_model_dir()
    
    # Try to load original model (random_forest_best.pkl)
    original_model_path = os.path.join(MODEL_DIR, "random_forest_best.pkl")
    
    # Also check parent directory
    if not os.path.exists(original_model_path):
        parent_models = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "random_forest_best.pkl")
        if os.path.exists(parent_models):
            original_model_path = parent_models
    
    if os.path.exists(original_model_path):
        RF_MODEL_ORIGINAL = joblib.load(original_model_path)
        print(f"✓ Loaded original model: {original_model_path}")
    else:
        # Fallback to calibrated model if original not found
        print("⚠️  Original model not found, using calibrated model as fallback")
        _load_calibrated_model()
        RF_MODEL_ORIGINAL = RF_MODEL_CALIBRATED


def _load_calibrated_model():
    """Load the literature-calibrated model"""
    global RF_MODEL_CALIBRATED, MODEL_DIR
    
    if MODEL_DIR is None:
        _initialize_model_dir()
    
    # Try to load literature-calibrated model components
    base_path = os.path.join(MODEL_DIR, "random_forest_literature_calibrated_base.pkl")
    platt_path = os.path.join(MODEL_DIR, "random_forest_literature_calibrated_platt.pkl")
    
    # Also check parent directory
    if not os.path.exists(base_path):
        parent_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        base_path = os.path.join(parent_dir, "random_forest_literature_calibrated_base.pkl")
        platt_path = os.path.join(parent_dir, "random_forest_literature_calibrated_platt.pkl")
    
    if os.path.exists(base_path) and os.path.exists(platt_path):
        # Load components and create wrapper
        import sys
        parent_utils = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils")
        sys.path.insert(0, parent_utils)
        from calibrated_model_wrapper import CalibratedModelWrapper
        
        base_model = joblib.load(base_path)
        platt_scaler = joblib.load(platt_path)
        RF_MODEL_CALIBRATED = CalibratedModelWrapper(base_model, platt_scaler)
        print(f"✓ Loaded literature-calibrated model: {base_path}")
    else:
        # Fallback to old calibrated model or original
        calibrated_path = os.path.join(MODEL_DIR, "random_forest_calibrated.pkl")
        if os.path.exists(calibrated_path):
            RF_MODEL_CALIBRATED = joblib.load(calibrated_path)
            print(f"✓ Loaded fallback calibrated model: {calibrated_path}")
        else:
            # Last resort: try to load original
            _load_original_model()
            RF_MODEL_CALIBRATED = RF_MODEL_ORIGINAL
            print("⚠️  Literature-calibrated model not found, using original model")


def load_models(use_literature_calibration=False):
    """Lazy load models on first request
    
    Args:
        use_literature_calibration: If True, load literature-calibrated model
                                    If False, load original pure data-driven model
    """
    global RF_MODEL, RF_MODEL_ORIGINAL, RF_MODEL_CALIBRATED, SCALER, FEATURE_NAMES, MODEL_DIR
    
    # Initialize MODEL_DIR and load scaler/features first
    if MODEL_DIR is None or SCALER is None:
        _initialize_model_dir()
        scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
        features_path = os.path.join(MODEL_DIR, "feature_names.pkl")
        
        if not os.path.exists(scaler_path):
            raise Exception(f"Scaler file not found at: {scaler_path}")
        if not os.path.exists(features_path):
            raise Exception(f"Features file not found at: {features_path}")
        
        SCALER = joblib.load(scaler_path)
        FEATURE_NAMES = joblib.load(features_path)
    
    # Determine which model to load
    if use_literature_calibration:
        if RF_MODEL_CALIBRATED is None:
            _load_calibrated_model()
        RF_MODEL = RF_MODEL_CALIBRATED
    else:
        if RF_MODEL_ORIGINAL is None:
            _load_original_model()
        RF_MODEL = RF_MODEL_ORIGINAL


def load_outcome_model():
    """Lazy load outcome model on first request"""
    global OUTCOME_MODEL, MODEL_DIR
    if OUTCOME_MODEL is None:
        try:
            # Get the directory where this file is located (api/)
            func_dir = os.path.dirname(__file__)

            # Try multiple possible locations
            possible_paths = [
                os.path.join(
                    func_dir, "models", "outcome_rf_regressor.pkl"
                ),  # api/models/
                os.path.join(
                    os.path.dirname(func_dir), "models", "outcome_rf_regressor.pkl"
                ),  # root/models/
            ]

            # Also try using MODEL_DIR if it's already set
            if MODEL_DIR is not None:
                possible_paths.insert(
                    0, os.path.join(MODEL_DIR, "outcome_rf_regressor.pkl")
                )
            else:
                # Try to load models to set MODEL_DIR
                try:
                    load_models()
                    if MODEL_DIR is not None:
                        possible_paths.insert(
                            0, os.path.join(MODEL_DIR, "outcome_rf_regressor.pkl")
                        )
                except:
                    pass  # Continue with other paths

            outcome_model_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    outcome_model_path = path
                    break

            if outcome_model_path is None:
                # Debug info
                import json

                debug_info = {
                    "func_dir": func_dir,
                    "checked_paths": possible_paths,
                    "func_dir_contents": (
                        os.listdir(func_dir) if os.path.exists(func_dir) else []
                    ),
                    "api_models_exists": os.path.exists(
                        os.path.join(func_dir, "models")
                    ),
                    "api_models_contents": (
                        os.listdir(os.path.join(func_dir, "models"))
                        if os.path.exists(os.path.join(func_dir, "models"))
                        else []
                    ),
                }
                raise Exception(
                    f"Outcome model file not found. Checked: {possible_paths}. Debug: {json.dumps(debug_info, indent=2)}"
                )

            OUTCOME_MODEL = joblib.load(outcome_model_path)
        except Exception as e:
            raise Exception(f"Failed to load outcome model: {str(e)}")


class handler(BaseHTTPRequestHandler):
    def _send_error(self, status_code, error_message):
        """Helper to send JSON error response"""
        try:
            self.send_response(status_code)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": error_message}).encode())
        except:
            pass  # If we can't send response, fail silently

    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read request body first to check for model selection
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length == 0:
                    self._send_error(400, "Empty request body")
                    return
                post_data = self.rfile.read(content_length)
            except Exception as e:
                self._send_error(400, f"Error reading request: {str(e)}")
                return

            # Parse multipart form data (CSV file)
            content_type = self.headers.get("Content-Type", "")
            use_literature_calibration = False
            
            if "boundary=" in content_type:
                boundary = content_type.split("boundary=")[1].encode()
                parts = post_data.split(b"--" + boundary)

                csv_data = None
                run_outcome = False
                for part in parts:
                    if b"filename=" in part and b".csv" in part:
                        # Extract CSV content
                        content_start = part.find(b"\r\n\r\n") + 4
                        csv_data = part[content_start:].strip()
                        # Remove trailing boundary
                        if csv_data.endswith(b"--"):
                            csv_data = csv_data[:-2]
                    elif b'name="run_outcome"' in part:
                        # Extract run_outcome parameter
                        content_start = part.find(b"\r\n\r\n") + 4
                        value = (
                            part[content_start:]
                            .strip()
                            .decode("utf-8", errors="ignore")
                        )
                        run_outcome = value.lower() == "true"
                    elif b'name="use_literature_calibration"' in part:
                        # Extract use_literature_calibration parameter
                        content_start = part.find(b"\r\n\r\n") + 4
                        value = (
                            part[content_start:]
                            .strip()
                            .decode("utf-8", errors="ignore")
                        )
                        use_literature_calibration = value.lower() == "true"

                if not csv_data:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"error": "No CSV file found in request"}).encode()
                    )
                    return

                # Parse CSV
                df = pd.read_csv(io.BytesIO(csv_data))
            else:
                # Try JSON body
                try:
                    body = json.loads(post_data.decode("utf-8"))
                    if "csv_data" in body:
                        df = pd.read_csv(io.StringIO(body["csv_data"]))
                    else:
                        self.send_response(400)
                        self.send_header("Content-type", "application/json")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps(
                                {"error": "No CSV data found in request"}
                            ).encode()
                        )
                        return
                except Exception as e:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {"error": f"Invalid request format: {str(e)}"}
                        ).encode()
                    )
                    return

            # Load models on first request (with model selection)
            try:
                load_models(use_literature_calibration=use_literature_calibration)
            except Exception as e:
                self._send_error(500, f"Model loading error: {str(e)}")
                return

            # Validate
            is_valid, message = validate_data(df)
            if not is_valid:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": message}).encode())
                return

            # Check if outcomes provided
            has_outcomes = "tkr_outcome" in df.columns

            # Preprocess
            try:
                X_preprocessed = preprocess_data(df, IMPUTER, SCALER, FEATURE_NAMES)
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": f"Preprocessing error: {str(e)}"}).encode()
                )
                return

            # Predict
            try:
                predictions = RF_MODEL.predict_proba(X_preprocessed)[:, 1]
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": f"Prediction error: {str(e)}"}).encode()
                )
                return

            # Add predictions to dataframe
            df["predicted_risk"] = predictions
            df["risk_category"] = pd.cut(
                predictions,
                bins=[0, 0.05, 0.15, 0.30, 1.0],
                labels=["Low", "Moderate", "High", "Very High"],
            )

            # Check for missing pain scores
            has_womac_r = "womac_r" in df.columns
            has_womac_l = "womac_l" in df.columns
            has_vas_r = "vas_r" in df.columns
            has_vas_l = "vas_l" in df.columns

            # Count patients without pain scores
            patients_without_pain_scores = 0
            if has_womac_r and has_womac_l:
                # Check if both WOMAC are missing
                patients_without_pain_scores = (
                    (df["womac_r"].isna()) & (df["womac_l"].isna())
                ).sum()
            elif has_vas_r and has_vas_l:
                # Check if both VAS are missing
                patients_without_pain_scores = (
                    (df["vas_r"].isna()) & (df["vas_l"].isna())
                ).sum()
            elif has_womac_r or has_womac_l or has_vas_r or has_vas_l:
                # Mixed case - check if all available pain scores are missing
                pain_cols = []
                if has_womac_r:
                    pain_cols.append("womac_r")
                if has_womac_l:
                    pain_cols.append("womac_l")
                if has_vas_r:
                    pain_cols.append("vas_r")
                if has_vas_l:
                    pain_cols.append("vas_l")
                if pain_cols:
                    patients_without_pain_scores = (
                        df[pain_cols].isna().all(axis=1).sum()
                    )
            else:
                # No pain score columns at all
                patients_without_pain_scores = len(df)

            # Check for missing KL grades (single knee imaging)
            # Convert "na" strings to NaN if present
            if "kl_r" in df.columns:
                df["kl_r"] = df["kl_r"].replace(["na", "NA", ""], np.nan)
            if "kl_l" in df.columns:
                df["kl_l"] = df["kl_l"].replace(["na", "NA", ""], np.nan)

            # Count patients with single knee imaging (one KL grade missing)
            patients_with_single_knee_imaging = 0
            if "kl_r" in df.columns and "kl_l" in df.columns:
                patients_with_single_knee_imaging = (
                    (df["kl_r"].isna() & df["kl_l"].notna())
                    | (df["kl_r"].notna() & df["kl_l"].isna())
                ).sum()

            # Calculate summary statistics
            summary = {
                "total_patients": int(len(df)),
                "avg_risk": float(predictions.mean() * 100),
                "high_risk_count": int((predictions > 0.15).sum()),
                "high_risk_pct": float((predictions > 0.15).mean() * 100),
                "risk_distribution": df["risk_category"].value_counts().to_dict(),
                "patients_without_pain_scores": int(patients_without_pain_scores),
                "patients_with_single_knee_imaging": int(
                    patients_with_single_knee_imaging
                ),
            }

            # Prepare risk distribution data for client-side chart
            risk_counts = df["risk_category"].value_counts()
            risk_dist_plot = {
                "type": "bar",
                "title": "Patient Distribution by Risk Category",
                "xlabel": "Risk Category",
                "ylabel": "Number of Patients",
                "data": {
                    "labels": risk_counts.index.tolist(),
                    "values": risk_counts.values.tolist(),
                },
            }

            # If outcomes provided, calculate validation metrics
            validation_metrics = None
            roc_plot = None
            calibration_plot = None

            if has_outcomes:
                y_true = df["tkr_outcome"]

                # Check if we have at least 2 classes for AUC calculation
                unique_classes = y_true.unique()
                n_events = int(y_true.sum())
                n_no_events = int((y_true == 0).sum())
                has_both_classes = len(unique_classes) >= 2 and n_events > 0 and n_no_events > 0

                validation_metrics = {
                    "event_rate": float(y_true.mean() * 100),
                    "n_events": n_events,
                }

                if has_both_classes:
                    # Can calculate AUC and other metrics
                    auc = roc_auc_score(y_true, predictions)
                    brier = brier_score_loss(y_true, predictions)
                    
                    validation_metrics["auc"] = float(auc)
                    validation_metrics["brier_score"] = float(brier)

                    # ROC Curve data for client-side rendering
                    fpr, tpr, _ = roc_curve(y_true, predictions)
                    roc_plot = {
                        "type": "line",
                        "title": "ROC Curve",
                        "xlabel": "False Positive Rate",
                        "ylabel": "True Positive Rate",
                        "data": {
                            "model": {
                                "x": fpr.tolist(),
                                "y": tpr.tolist(),
                                "label": f"Model (AUC={auc:.3f})",
                            },
                            "random": {"x": [0, 1], "y": [0, 1], "label": "Random"},
                        },
                    }

                    # Calibration Plot data for client-side rendering
                    prob_true, prob_pred = calibration_curve(
                        y_true, predictions, n_bins=10, strategy="quantile"
                    )
                    calibration_plot = {
                        "type": "scatter",
                        "title": "Calibration Plot",
                        "xlabel": "Predicted Probability",
                        "ylabel": "Observed Frequency",
                        "data": {
                            "model": {
                                "x": prob_pred.tolist(),
                                "y": prob_true.tolist(),
                                "label": "Model",
                            },
                            "perfect": {
                                "x": [0, 1],
                                "y": [0, 1],
                                "label": "Perfect Calibration",
                            },
                        },
                    }
                else:
                    # Only one class present - can't calculate AUC
                    validation_metrics["auc"] = None
                    validation_metrics["brier_score"] = None

                # Risk stratification
                risk_strat = df.groupby("risk_category").agg(
                    {"tkr_outcome": ["count", "sum", "mean"]}
                )
                risk_strat.columns = ["n_patients", "n_events", "event_rate"]
                risk_strat["event_rate_pct"] = (risk_strat["event_rate"] * 100).round(1)
                # Replace NaN with 0 for event_rate when no patients in category
                risk_strat["event_rate"] = risk_strat["event_rate"].fillna(0.0)
                risk_strat["event_rate_pct"] = risk_strat["event_rate_pct"].fillna(0.0)
                validation_metrics["risk_stratification"] = risk_strat.to_dict("index")

            # Prepare downloadable predictions
            if "patient_id" in df.columns:
                download_df = df[
                    ["patient_id", "predicted_risk", "risk_category"]
                ].copy()
            else:
                download_df = df[["predicted_risk", "risk_category"]].copy()
                download_df.insert(0, "patient_number", range(1, len(df) + 1))

            # Format risk as percentage
            download_df["predicted_risk_pct"] = (
                download_df["predicted_risk"] * 100
            ).round(1)
            download_df = download_df.drop("predicted_risk", axis=1)
            
            # Rename columns to be surgeon-friendly
            column_rename_map = {
                "patient_id": "Patient ID",
                "patient_number": "Patient Number",
                "predicted_risk_pct": "Surgery Risk (%)",
                "risk_category": "Risk Category",
            }
            download_df = download_df.rename(columns=column_rename_map)
            
            # Reorder columns
            if "Patient ID" in download_df.columns:
                download_df = download_df[["Patient ID", "Surgery Risk (%)", "Risk Category"]]
            else:
                download_df = download_df[["Patient Number", "Surgery Risk (%)", "Risk Category"]]

            predictions_csv = download_df.to_csv(index=False)

            # NEW: Outcome predictions (if requested)
            outcome_predictions = None
            if run_outcome:
                try:
                    # Load outcome model
                    load_outcome_model()

                    # Run outcome predictions for ALL patients (not just moderate/high risk)
                    # User wants to see outcomes for all risk categories
                    X_all_patients = X_preprocessed

                    if len(X_all_patients) > 0:
                        # Predict improvement
                        improvement_pred = OUTCOME_MODEL.predict(X_all_patients)

                        # Calculate success metrics for each patient
                        success_metrics_list = []
                        success_categories = []
                        success_probabilities = []
                        
                        for improvement in improvement_pred:
                            metrics = calculate_success_metrics(float(improvement))
                            success_metrics_list.append(metrics)
                            success_categories.append(metrics["success_category"])
                            success_probabilities.append(metrics["success_probability"])

                        # Create success category distribution
                        success_category_series = pd.Series(success_categories)
                        success_distribution = success_category_series.value_counts().to_dict()
                        
                        # Calculate statistics
                        mean_success_prob = float(np.mean(success_probabilities))
                        median_success_prob = float(np.median(success_probabilities))
                        
                        # Count successful outcomes (≥30 points = Successful or Excellent)
                        successful_count = sum(
                            1 for cat in success_categories 
                            if cat in ["Successful Outcome", "Excellent Outcome"]
                        )
                        success_rate = (successful_count / len(success_categories)) * 100

                        outcome_predictions = {
                            "n_analyzed": int(len(X_all_patients)),
                            "mean_improvement": float(improvement_pred.mean()),
                            "median_improvement": float(np.median(improvement_pred)),
                            "std_improvement": float(improvement_pred.std()),
                            # Success metrics (primary display)
                            "mean_success_probability": round(mean_success_prob, 1),
                            "median_success_probability": round(median_success_prob, 1),
                            "success_rate": round(success_rate, 1),  # % with ≥30 improvement
                            "success_distribution": {
                                str(k): int(v) for k, v in success_distribution.items()
                            },
                            # Keep old distribution for backward compatibility (hidden in UI)
                            "improvement_distribution": {
                                "Minimal Improvement": success_distribution.get("Minimal Improvement", 0),
                                "Limited Improvement": success_distribution.get("Limited Improvement", 0),
                                "Moderate Improvement": success_distribution.get("Moderate Improvement", 0),
                                "Successful Outcome": success_distribution.get("Successful Outcome", 0),
                                "Excellent Outcome": success_distribution.get("Excellent Outcome", 0),
                            },
                            # Per-patient success data
                            "patient_success_data": success_metrics_list,
                        }

                        # Create plot data for success category distribution (client-side rendering)
                        category_order = [
                            "Excellent Outcome",
                            "Successful Outcome",
                            "Moderate Improvement",
                            "Limited Improvement",
                            "Minimal Improvement",
                        ]
                        category_counts = [
                            success_distribution.get(cat, 0) for cat in category_order
                        ]
                        outcome_predictions["success_plot"] = {
                            "type": "bar",
                            "title": "Surgical Success Probability Distribution",
                            "xlabel": "Success Category",
                            "ylabel": "Number of Patients",
                            "data": {
                                "labels": category_order,
                                "values": category_counts,
                            },
                        }
                        # Keep old plot for backward compatibility
                        outcome_predictions["improvement_plot"] = outcome_predictions["success_plot"]

                        # Add to patient data for download
                        df_all_patients = df.copy()
                        df_all_patients["predicted_improvement_points"] = [round(float(x), 1) for x in improvement_pred]
                        df_all_patients["success_category"] = success_categories
                        df_all_patients["success_probability"] = [round(p, 1) for p in success_probabilities]
                        
                        # Create per-patient data for filtering/sorting (include patient identifiers)
                        patient_outcomes_list = []
                        for i, row in df_all_patients.iterrows():
                            patient_outcome = {
                                "patient_id": row.get("patient_id", f"Patient {i+1}"),
                                "patient_number": i + 1 if "patient_id" not in row else None,
                                "age": row.get("age"),
                                "sex": row.get("sex"),
                                "bmi": row.get("bmi"),
                                "surgery_risk": float(row.get("predicted_risk", 0) * 100) if "predicted_risk" in row else None,
                                "risk_category": row.get("risk_category"),
                                "success_category": success_categories[i],
                                "success_probability": round(success_probabilities[i], 1),
                                "category_color": success_metrics_list[i].get("category_color", {}),
                                "category_description": success_metrics_list[i].get("category_description", ""),
                                "_womac_improvement": round(float(improvement_pred[i]), 1),
                            }
                            patient_outcomes_list.append(patient_outcome)
                        
                        outcome_predictions["patient_outcomes"] = patient_outcomes_list
                        
                        # Keep WOMAC improvement band for internal reference (hidden column)
                        improvement_pred_series = pd.Series(improvement_pred)
                        bands = pd.cut(
                            improvement_pred_series,
                            bins=[-100, 0, 10, 20, 30, 100],
                            labels=[
                                "Likely Worse",
                                "Minimal (0-10)",
                                "Moderate (10-20)",
                                "Good (20-30)",
                                "Excellent (>30)",
                            ],
                        )
                        df_all_patients["_womac_improvement_band"] = bands.astype(str)

                        # Merge with original predictions
                        if "patient_id" in df_all_patients.columns:
                            outcome_download = df_all_patients[
                                [
                                    "patient_id",
                                    "predicted_risk",
                                    "risk_category",
                                    "success_category",
                                    "success_probability",
                                    # Keep WOMAC data for reference (internal use)
                                    "predicted_improvement_points",
                                ]
                            ].copy()
                        else:
                            outcome_download = df_all_patients[
                                [
                                    "predicted_risk",
                                    "risk_category",
                                    "success_category",
                                    "success_probability",
                                    "predicted_improvement_points",
                                ]
                            ].copy()
                            outcome_download.insert(
                                0, "patient_number", range(1, len(df_all_patients) + 1)
                            )

                        # Format risk as percentage
                        outcome_download["predicted_risk_pct"] = (
                            outcome_download["predicted_risk"] * 100
                        ).round(1)
                        outcome_download = outcome_download.drop(
                            "predicted_risk", axis=1
                        )
                        
                        # Rename columns to be surgeon-friendly
                        column_rename_map = {
                            "patient_id": "Patient ID",
                            "patient_number": "Patient Number",
                            "predicted_risk_pct": "Surgery Risk (%)",
                            "risk_category": "Risk Category",
                            "success_category": "Expected Outcome",
                            "success_probability": "Success Probability (%)",
                            "predicted_improvement_points": "Technical: Symptom Improvement Score",
                        }
                        outcome_download = outcome_download.rename(columns=column_rename_map)
                        
                        # Reorder columns: primary info first, technical last
                        primary_columns = []
                        if "Patient ID" in outcome_download.columns:
                            primary_columns.append("Patient ID")
                        elif "Patient Number" in outcome_download.columns:
                            primary_columns.append("Patient Number")
                        primary_columns.extend([
                            "Surgery Risk (%)",
                            "Risk Category",
                            "Expected Outcome",
                            "Success Probability (%)",
                        ])
                        technical_columns = [
                            col for col in outcome_download.columns 
                            if col.startswith("Technical:") or (col not in primary_columns and col not in ["Patient ID", "Patient Number"])
                        ]
                        outcome_download = outcome_download[primary_columns + technical_columns]

                        outcome_predictions["csv"] = outcome_download.to_csv(
                            index=False
                        )

                    else:
                        outcome_predictions = {
                            "error": "No patients to analyze"
                        }

                except Exception as e:
                    outcome_predictions = {
                        "error": f"Error predicting outcomes: {str(e)}"
                    }

            # Convert NaN values to None (null in JSON) for valid JSON
            def clean_nan(obj):
                """Recursively replace NaN with None"""
                if isinstance(obj, dict):
                    return {k: clean_nan(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_nan(item) for item in obj]
                elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                    return None
                return obj

            # Send response
            response = {
                "success": True,
                "summary": clean_nan(summary),
                "validation_metrics": (
                    clean_nan(validation_metrics) if validation_metrics else None
                ),
                "plots": {
                    "risk_distribution": clean_nan(risk_dist_plot),
                    "roc_curve": clean_nan(roc_plot) if roc_plot else None,
                    "calibration": (
                        clean_nan(calibration_plot) if calibration_plot else None
                    ),
                },
                "predictions_csv": predictions_csv,
                "outcome_predictions": (
                    clean_nan(outcome_predictions) if outcome_predictions else None
                ),  # NEW
                "model_type": "Literature-Calibrated" if use_literature_calibration else "Pure Data-Driven (Original)",
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            import traceback
            import sys

            # Get full traceback for debugging
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_str = "".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            )

            # For production, show user-friendly message
            error_msg = str(e)
            if (
                "Failed to load models" in error_msg
                or "Model loading error" in error_msg
            ):
                error_msg = f"Model loading error: {str(e)}"
            elif "Preprocessing error" in error_msg:
                error_msg = f"Preprocessing error: {str(e)}"
            elif "Prediction error" in error_msg:
                error_msg = f"Prediction error: {str(e)}"
            else:
                # Include more detail for debugging
                error_msg = f"Processing error: {str(e)}"
                # Log full traceback to console (will appear in Vercel logs)
                print(f"Full error traceback:\n{traceback_str}")

            try:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": error_msg}).encode())
            except Exception as send_error:
                # If we can't send response, log it
                print(f"Failed to send error response: {send_error}")

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
