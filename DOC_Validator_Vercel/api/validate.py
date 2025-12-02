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
        MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        RF_MODEL = joblib.load(os.path.join(MODEL_DIR, "random_forest_calibrated.pkl"))
        SCALER = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        FEATURE_NAMES = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))




class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests"""
        # Load models on first request
        load_models()

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

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
                    self.send_error(400, "No CSV file found")
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
                        self.send_error(400, "No CSV data found")
                        return
                except:
                    self.send_error(400, "Invalid request format")
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
            X_preprocessed = preprocess_data(df, IMPUTER, SCALER, FEATURE_NAMES)

            # Predict
            predictions = RF_MODEL.predict_proba(X_preprocessed)[:, 1]

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
                    "values": risk_counts.values.tolist()
                }
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
                            "label": f"Model (AUC={auc:.3f})"
                        },
                        "random": {
                            "x": [0, 1],
                            "y": [0, 1],
                            "label": "Random"
                        }
                    }
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
                            "label": "Model"
                        },
                        "perfect": {
                            "x": [0, 1],
                            "y": [0, 1],
                            "label": "Perfect Calibration"
                        }
                    }
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

            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": error_msg}).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
