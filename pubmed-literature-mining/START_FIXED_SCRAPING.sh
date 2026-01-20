#!/bin/bash
# Start scraping with the FIXED version that saves to database

cd /Users/parkercase/DOC
source venv/bin/activate

echo "=========================================="
echo "Starting Batch 2 Scraping - FIXED VERSION"
echo "=========================================="
echo ""
echo "This version now saves articles to the SQLite database!"
echo "You'll see the database count increase as articles are added."
echo ""
echo "Starting..."
echo ""

python pubmed-literature-mining/scripts/scrape_batch_2_robust.py

echo ""
echo "=========================================="
echo "Scraping completed!"
echo "=========================================="
echo ""
echo "Check database count:"
echo "cd pubmed-literature-mining"
echo "python -c \"import sqlite3; conn = sqlite3.connect('data/literature.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM papers'); print(f'Total: {cursor.fetchone()[0]}'); conn.close()\""
