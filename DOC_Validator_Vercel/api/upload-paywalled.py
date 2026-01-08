"""
API endpoint for uploading paywalled articles
Handles PDF uploads and stores them in the literature database
"""

import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import cgi

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from pubmed_literature_mining.scripts.literature_database import LiteratureDatabase
    from pubmed_literature_mining.scripts.probast_assessment import PROBASTAssessment
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_POST(self):
        """Handle PDF upload"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self._send_error(400, "Content-Type must be multipart/form-data")
                return
            
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            # Get form fields
            pmid = form.getvalue('pmid', '').strip()
            title = form.getvalue('title', '').strip()
            pdf_file = form.getvalue('pdf')
            
            if not pmid:
                self._send_error(400, "PMID is required")
                return
            
            if not pdf_file:
                self._send_error(400, "PDF file is required")
                return
            
            # Save PDF file
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'pubmed-literature-mining', 'data', 'pdfs')
            os.makedirs(upload_dir, exist_ok=True)
            
            pdf_path = os.path.join(upload_dir, f"{pmid}.pdf")
            
            # Handle file upload
            if hasattr(pdf_file, 'file'):
                # FileFieldStorage object
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_file.file.read())
            else:
                # String or bytes
                if isinstance(pdf_file, bytes):
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_file)
                else:
                    self._send_error(400, "Invalid file format")
                    return
            
            # Add to database if available
            if DB_AVAILABLE:
                try:
                    db = LiteratureDatabase()
                    probast = PROBASTAssessment()
                    
                    # Create article record
                    article = {
                        "pmid": pmid,
                        "title": title,
                        "access_type": "paywalled",
                        "pdf_path": pdf_path
                    }
                    
                    # Assess with PROBAST
                    assessment = probast.assess_article(article)
                    
                    # Add to database
                    db.add_article(article, assessment)
                    db.add_paywalled_upload(pmid, pdf_path)
                    
                    self._send_json({
                        "success": True,
                        "message": f"Article {pmid} uploaded and assessed. PROBAST Risk: {assessment.get('overall_risk', 'Unclear')}",
                        "pmid": pmid,
                        "probast_risk": assessment.get('overall_risk', 'Unclear')
                    })
                    return
                    
                except Exception as e:
                    # Still save file even if DB fails
                    self._send_json({
                        "success": True,
                        "message": f"PDF saved, but database update failed: {str(e)}",
                        "pmid": pmid
                    }, status=207)  # Multi-status
                    return
            else:
                # Database not available, just save file
                self._send_json({
                    "success": True,
                    "message": f"PDF saved for PMID {pmid}. Database integration not available.",
                    "pmid": pmid
                })
                return
                
        except Exception as e:
            self._send_error(500, f"Upload error: {str(e)}")
    
    def _send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, status_code, error_message):
        """Send error response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"error": error_message}).encode('utf-8'))
