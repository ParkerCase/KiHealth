#!/bin/bash

# PROMPT 4 Runner Script
# Executes comprehensive integrated scoring

echo "=========================================="
echo "PROMPT 4: Comprehensive Integrated Scoring"
echo "=========================================="
echo ""
echo "This will integrate all 6 evidence dimensions:"
echo "  1. DepMap Dependency"
echo "  2. Expression Correlation"
echo "  3. Mutation Context"
echo "  4. Copy Number Variation"
echo "  5. Literature Support"
echo "  6. Experimental Validation"
echo ""
echo "Expected runtime: 30-60 seconds"
echo "=========================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/../.."

# Run the Python script
python3 src/analysis/prompt_4_integrated_scoring.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! PROMPT 4 Complete"
    echo "=========================================="
    echo ""
    echo "📁 Files created:"
    echo "   1. data/processed/final_integrated_rankings.csv"
    echo "   2. data/processed/top_10_evidence_breakdown.csv"
    echo "   3. outputs/reports/integrated_scoring_summary.md"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Review the top 10 rankings"
    echo "   2. Check the integrated_scoring_summary.md"
    echo "   3. Ready for PROMPT 5 (Report Generation)"
    echo ""
    echo " Days until Nov 10: 8 days"
    echo "=========================================="
else
    echo ""
    echo "❌ Error running PROMPT 4"
    echo "Check the error messages above"
    exit 1
fi
