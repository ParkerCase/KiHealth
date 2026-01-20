#!/bin/bash
# Simple script to run batch 2 scraping with progress monitoring

cd "$(dirname "$0")/../.."
cd pubmed-literature-mining

echo "=========================================="
echo "Starting Batch 2 Scraping"
echo "=========================================="
echo ""
echo "This will scrape 5,000 new articles."
echo "Expected time: 1-3 hours"
echo ""
echo "Press Ctrl+C to stop (safely)"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Run the script and show progress
python scripts/scrape_batch_2.py 2>&1 | tee scraping_log_$(date +%Y%m%d_%H%M%S).txt

echo ""
echo "=========================================="
echo "Scraping completed!"
echo "=========================================="
