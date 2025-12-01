#!/bin/bash
# Start DOC Risk Calculator

echo "=========================================="
echo "DOC Risk Calculator - Starting Server"
echo "=========================================="
echo ""
echo "Access the calculator at: http://localhost:5001"
echo "(Port 5000 may be in use by macOS AirPlay)"
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

cd "$(dirname "$0")"
python app.py

