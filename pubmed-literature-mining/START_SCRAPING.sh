#!/bin/bash
# Simple script to start batch 2 scraping

cd "$(dirname "$0")/../.."

echo "=========================================="
echo "Starting Batch 2 Scraping"
echo "=========================================="
echo ""
echo "This will scrape 5,000 new articles."
echo "The script will run continuously until complete."
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "Starting..."
echo ""

# Run the script
python pubmed-literature-mining/scripts/scrape_batch_2_robust.py

echo ""
echo "=========================================="
echo "Scraping completed!"
echo "=========================================="
