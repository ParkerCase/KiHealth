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


def load_models():
    """Lazy load models on first request"""
    global RF_MODEL, SCALER, FEATURE_NAMES, MODEL_DIR
    if RF_MODEL is None:
        try:
            # In Vercel, files are relative to the function's directory
            # Try multiple possible paths
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "models"),
                os.path.join(os.getcwd(), "models"),
                os.path.join("/var/task", "models"),
                "models",  # Relative to current working directory
            ]
            
            MODEL_DIR = None
            for path in possible_paths:
                test_file = os.path.join(path, "random_forest_calibrated.pkl")
                if os.path.exists(test_file):
                    MODEL_DIR = path
                    break
            
            if MODEL_DIR is None:
                # Debug: list what's actually available
                cwd = os.getcwd()
                files_in_cwd = os.listdir(cwd) if os.path.exists(cwd) else []
                func_dir = os.path.dirname(__file__)
                files_in_func_dir = os.listdir(func_dir) if os.path.exists(func_dir) else []
                parent_dir = os.path.dirname(func_dir)
                files_in_parent = os.listdir(parent_dir) if os.path.exists(parent_dir) else []
                
                raise Exception(
                    f"Models directory not found. Tried: {possible_paths}\n"
                    f"Current working directory: {cwd}\n"
                    f"Files in cwd: {files_in_cwd}\n"
                    f"Function directory: {func_dir}\n"
                    f"Files in function dir: {files_in_func_dir}\n"
                    f"Parent directory: {parent_dir}\n"
                    f"Files in parent: {files_in_parent}"
                )
            
            RF_MODEL = joblib.load(
                os.path.join(MODEL_DIR, "random_forest_calibrated.pkl")
            )
            SCALER = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
            FEATURE_NAMES = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
        except Exception as e:
            raise Exception(f"Failed to load models: {str(e)}")


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
                for part in parts:
                    if b"filename=" in part and b".csv" in part:
                        # Extract CSV content
                        content_start = part.find(b"\r\n\r\n") + 4
                        csv_data = part[content_start:].strip()
                        # Remove trailing boundary
                        if csv_data.endswith(b"--"):
                            csv_data = csv_data[:-2]
                        break

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

            # Calculate summary statistics
            summary = {
                "total_patients": int(len(df)),
                "avg_risk": float(predictions.mean() * 100),
                "high_risk_count": int((predictions > 0.15).sum()),
                "high_risk_pct": float((predictions > 0.15).mean() * 100),
                "risk_distribution": df["risk_category"].value_counts().to_dict(),
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

            # Send response
            response = {
                "success": True,
                "summary": summary,
                "validation_metrics": validation_metrics,
                "plots": {
                    "risk_distribution": risk_dist_plot,
                    "roc_curve": roc_plot,
                    "calibration": calibration_plot,
                },
                "predictions_csv": predictions_csv,
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
            traceback_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

            # For production, show user-friendly message
            error_msg = str(e)
            if "Failed to load models" in error_msg or "Model loading error" in error_msg:
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
