#!/bin/bash
# Quick script to run the literature quality workflow
# Usage: ./RUN_WORKFLOW.sh [number_of_articles]

cd "$(dirname "$0")"

# Default to 5000 articles, or use first argument
MAX_ARTICLES=${1:-5000}

echo "=========================================="
echo "Literature Quality Workflow"
echo "=========================================="
echo "Max articles: $MAX_ARTICLES"
echo "Starting workflow..."
echo ""

python scripts/literature_quality_workflow.py --max-articles $MAX_ARTICLES 2>&1 | tee logs/workflow_$(date +%Y%m%d_%H%M%S).log

echo ""
echo "=========================================="
echo "Workflow complete!"
echo "=========================================="
echo ""
echo "Check results:"
echo "  python monitor_system.py"
echo ""
