#!/bin/bash
# Start DOC Risk Calculator on Port 3003

cd "$(dirname "$0")"
cd ..

source venv/bin/activate

echo "=========================================="
echo "DOC Risk Calculator - Starting on Port 3003"
echo "=========================================="
echo ""
echo "Model: Pure Data-Driven (Original)"
echo "To use Literature-Calibrated model:"
echo "  USE_LITERATURE_CALIBRATION=true python risk_calculator/app.py"
echo ""
echo "Access the calculator at: http://localhost:3003"
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

cd risk_calculator
python app.py
