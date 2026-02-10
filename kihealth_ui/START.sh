#!/bin/bash
# Run KiHealth Pipeline UI from project root
cd "$(dirname "$0")/.."
streamlit run kihealth_ui/app.py --server.port 8502
