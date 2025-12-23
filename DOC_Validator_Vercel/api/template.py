"""
Vercel serverless function to download CSV template
"""

from http.server import BaseHTTPRequestHandler
import pandas as pd


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Return CSV template"""
        template_data = {
            "patient_id": ["P001", "P002", "P003", "P004", "P005"],
            "age": [52, 67, 58, 71, 49],
            "sex": [1, 0, 1, 0, 1],  # 1=Male, 0=Female
            "bmi": [28.5, 31.2, 25.8, 33.6, 27.3],
            "womac_r": [45.2, 62.3, 22.4, 71.2, 35.6],  # Symptom score (0-96, higher = more symptoms)
            "womac_l": [38.1, 58.7, 19.8, 68.4, 41.2],  # Symptom score (0-96, higher = more symptoms)
            "kl_r": [2, 3, 1, 3, 2],
            "kl_l": [2, 3, 1, 4, 2],
            "fam_hx": [0, 1, 0, 1, 0],  # 1=Yes, 0=No
            "tkr_outcome": [0, 1, 0, 1, 0],  # Optional: 1=Yes, 0=No
        }
        df = pd.DataFrame(template_data)
        csv_content = df.to_csv(index=False)

        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", 'attachment; filename="DOC_template.csv"')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(csv_content.encode("utf-8"))
