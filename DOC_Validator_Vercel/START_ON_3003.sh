#!/bin/bash
# Start DOC Validator on Port 3003

cd "$(dirname "$0")"
cd ..

source venv/bin/activate

echo "=========================================="
echo "DOC Model Validator - Starting on Port 3003"
echo "=========================================="
echo ""
echo "Access at: http://localhost:3003"
echo "Model toggle available in the form"
echo "Press Ctrl+C to stop"
echo ""
echo "=========================================="
echo ""

cd DOC_Validator_Vercel
python main.py 3003
