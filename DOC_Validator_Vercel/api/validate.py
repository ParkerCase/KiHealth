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

# Load models lazily (only when needed) to reduce initial bundle size
MODEL_DIR = None
RF_MODEL = None
SCALER = None
IMPUTER = None
FEATURE_NAMES = None
OUTCOME_MODEL = None


def load_models():
    """Lazy load models on first request"""
    global RF_MODEL, SCALER, FEATURE_NAMES, MODEL_DIR
    if RF_MODEL is None:
        try:
            # Get the directory where this file is located (api/)
            func_dir = os.path.dirname(__file__)

            # Try api/models/ first (most reliable in Vercel)
            api_models_path = os.path.join(func_dir, "models")

            # Also try root models/ directory
            root_models_path = os.path.join(os.path.dirname(func_dir), "models")

            # Check which path exists
            if os.path.exists(
                os.path.join(api_models_path, "random_forest_calibrated.pkl")
            ):
                MODEL_DIR = api_models_path
            elif os.path.exists(
                os.path.join(root_models_path, "random_forest_calibrated.pkl")
            ):
                MODEL_DIR = root_models_path
            else:
                # Debug: show what's available
                import json

                debug_info = {
                    "func_dir": func_dir,
                    "api_models_exists": os.path.exists(api_models_path),
                    "root_models_exists": os.path.exists(root_models_path),
                    "cwd": os.getcwd(),
                    "func_dir_contents": (
                        os.listdir(func_dir) if os.path.exists(func_dir) else []
                    ),
                    "parent_dir": os.path.dirname(func_dir),
                    "parent_dir_contents": (
                        os.listdir(os.path.dirname(func_dir))
                        if os.path.exists(os.path.dirname(func_dir))
                        else []
                    ),
                }
                raise Exception(
                    f"Models not found. Debug info: {json.dumps(debug_info, indent=2)}"
                )

            model_path = os.path.join(MODEL_DIR, "random_forest_calibrated.pkl")
            scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
            features_path = os.path.join(MODEL_DIR, "feature_names.pkl")

            if not os.path.exists(model_path):
                raise Exception(f"Model file not found at: {model_path}")
            if not os.path.exists(scaler_path):
                raise Exception(f"Scaler file not found at: {scaler_path}")
            if not os.path.exists(features_path):
                raise Exception(f"Features file not found at: {features_path}")

            RF_MODEL = joblib.load(model_path)
            SCALER = joblib.load(scaler_path)
            FEATURE_NAMES = joblib.load(features_path)
        except Exception as e:
            raise Exception(f"Failed to load models: {str(e)}")


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
            # Load models on first request
            try:
                load_models()
            except Exception as e:
                self._send_error(500, f"Model loading error: {str(e)}")
                return

            # Read request body
            # Read request body
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

            # Calculate summary statistics
            summary = {
                "total_patients": int(len(df)),
                "avg_risk": float(predictions.mean() * 100),
                "high_risk_count": int((predictions > 0.15).sum()),
                "high_risk_pct": float((predictions > 0.15).mean() * 100),
                "risk_distribution": df["risk_category"].value_counts().to_dict(),
                "patients_without_pain_scores": int(patients_without_pain_scores),
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

                auc = roc_auc_score(y_true, predictions)
                brier = brier_score_loss(y_true, predictions)
                event_rate = y_true.mean() * 100

                validation_metrics = {
                    "auc": float(auc),
                    "brier_score": float(brier),
                    "event_rate": float(event_rate),
                    "n_events": int(y_true.sum()),
                }

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

            predictions_csv = download_df.to_csv(index=False)

            # NEW: Outcome predictions (if requested)
            outcome_predictions = None
            if run_outcome:
                try:
                    # Load outcome model
                    load_outcome_model()

                    # Filter to moderate/high-risk patients (>5% surgery risk)
                    high_risk_mask = predictions > 0.05
                    X_high_risk = X_preprocessed[high_risk_mask]

                    if len(X_high_risk) > 0:
                        # Predict improvement
                        improvement_pred = OUTCOME_MODEL.predict(X_high_risk)

                        # Create improvement bands
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

                        # Calculate statistics
                        outcome_predictions = {
                            "n_analyzed": int(len(X_high_risk)),
                            "mean_improvement": float(improvement_pred.mean()),
                            "median_improvement": float(np.median(improvement_pred)),
                            "std_improvement": float(improvement_pred.std()),
                            "improvement_distribution": {
                                str(k): int(v)
                                for k, v in bands.value_counts().to_dict().items()
                            },
                        }

                        # Create plot data for improvement distribution (client-side rendering)
                        band_counts = bands.value_counts().sort_index()
                        outcome_predictions["improvement_plot"] = {
                            "type": "bar",
                            "title": "Expected Surgical Outcome Distribution",
                            "xlabel": "Expected Improvement Band",
                            "ylabel": "Number of Patients",
                            "data": {
                                "labels": [str(x) for x in band_counts.index.tolist()],
                                "values": band_counts.values.tolist(),
                            },
                        }

                        # Add to patient data for download
                        df_high_risk = df[high_risk_mask].copy()
                        df_high_risk["predicted_improvement"] = improvement_pred
                        df_high_risk["improvement_band"] = bands.astype(str)

                        # Merge with original predictions
                        if "patient_id" in df_high_risk.columns:
                            outcome_download = df_high_risk[
                                [
                                    "patient_id",
                                    "predicted_risk",
                                    "risk_category",
                                    "predicted_improvement",
                                    "improvement_band",
                                ]
                            ].copy()
                        else:
                            outcome_download = df_high_risk[
                                [
                                    "predicted_risk",
                                    "risk_category",
                                    "predicted_improvement",
                                    "improvement_band",
                                ]
                            ].copy()
                            outcome_download.insert(
                                0, "patient_number", range(1, len(df_high_risk) + 1)
                            )

                        # Format risk as percentage
                        outcome_download["predicted_risk_pct"] = (
                            outcome_download["predicted_risk"] * 100
                        ).round(1)
                        outcome_download = outcome_download.drop(
                            "predicted_risk", axis=1
                        )

                        outcome_predictions["csv"] = outcome_download.to_csv(
                            index=False
                        )

                    else:
                        outcome_predictions = {
                            "error": "No moderate/high-risk patients (>5% surgery risk) to analyze"
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
