#!/usr/bin/env python3
"""
Railway-compatible server for DOC Validator
Serves static files and handles API routes
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json

# Add paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))

# Import API handlers
from api.validate import handler as ValidateHandler
from api.template import handler as TemplateHandler

class RailwayHandler(BaseHTTPRequestHandler):
    """Handler for Railway deployment"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Health check
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
        
        # API routes
        if parsed_path.path == '/api/template':
            h = TemplateHandler(self, self.client_address, self.server)
            h.do_GET()
            return
        
        # Static files
        if parsed_path.path.startswith('/static/'):
            self.serve_static_file(parsed_path.path[1:])
            return
        
        # Root and HTML files
        if parsed_path.path == '/' or parsed_path.path.endswith('.html'):
            self.serve_static_file('public/index.html')
            return
        
        # Default: serve from public directory
        self.serve_static_file('public' + parsed_path.path)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/validate':
            h = ValidateHandler(self, self.client_address, self.server)
            h.do_POST()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_static_file(self, file_path):
        """Serve a static file"""
        possible_paths = [
            file_path,
            os.path.join('public', file_path),
            os.path.join('static', file_path.lstrip('/static/')),
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                    
                    # Determine content type
                    if path.endswith('.css'):
                        content_type = 'text/css; charset=utf-8'
                    elif path.endswith('.js'):
                        content_type = 'application/javascript; charset=utf-8'
                    elif path.endswith('.html'):
                        content_type = 'text/html; charset=utf-8'
                    elif path.endswith('.png'):
                        content_type = 'image/png'
                    elif path.endswith('.jpg') or path.endswith('.jpeg'):
                        content_type = 'image/jpeg'
                    else:
                        content_type = 'application/octet-stream'
                    
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    print(f"Error serving {path}: {e}")
        
        # File not found
        self.send_error(404)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def run(port=None):
    """Run the server"""
    if port is None:
        port = int(os.environ.get('PORT', 8000))
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, RailwayHandler)
    
    print("=" * 60)
    print("DOC VALIDATOR - RAILWAY SERVER")
    print("=" * 60)
    print(f"✓ Server running on {server_address[0]}:{server_address[1]}")
    print(f"✓ PORT environment variable: {os.environ.get('PORT', 'not set')}")
    print(f"✓ Serving static files from public/")
    print(f"✓ API endpoints: /api/validate, /api/template, /health")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped")
    except Exception as e:
        print(f"Server crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()

