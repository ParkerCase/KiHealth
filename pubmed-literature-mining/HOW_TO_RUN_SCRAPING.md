# How to Run Batch 2 Scraping - Simple Guide

## Quick Start

**Run this command:**
```bash
cd /Users/parkercase/DOC
nohup python pubmed-literature-mining/scripts/scrape_batch_2_robust.py > pubmed-literature-mining/scraping_output.log 2>&1 &
```

**Check if it's running:**
```bash
ps aux | grep scrape_batch_2_robust
```

**Check progress:**
```bash
tail -f pubmed-literature-mining/scraping_output.log
```

**Check how many articles added:**
```bash
cd pubmed-literature-mining
python -c "import sqlite3; conn = sqlite3.connect('data/literature.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM papers'); print(f'Total: {cursor.fetchone()[0]}'); conn.close()"
```

## What It Does

1. **Checks database:** Finds all 4,671 existing articles
2. **Runs 8 different search queries:** To find NEW articles
3. **Filters duplicates:** Only processes articles not in database
4. **Continues until target:** Runs all queries until 5,000 new articles found
5. **Saves progress:** Can resume if interrupted

## Expected Timeline

- **Query 1:** ~30-60 minutes (5,000 articles to check)
- **Queries 2-8:** ~30 minutes each if needed
- **Total:** 1-3 hours to reach 5,000 new articles

## Monitor Progress

**Watch the log file:**
```bash
tail -f pubmed-literature-mining/scraping_output.log
```

**Check database count:**
```bash
cd pubmed-literature-mining
python -c "import sqlite3; conn = sqlite3.connect('data/literature.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM papers'); print(f'Total articles: {cursor.fetchone()[0]}'); conn.close()"
```

## Stop the Script

**If you need to stop it:**
```bash
ps aux | grep scrape_batch_2_robust
kill [PID]
```

## Troubleshooting

**If script stops:**
1. Check the log: `cat pubmed-literature-mining/scraping_output.log`
2. Check for errors: `grep -i error pubmed-literature-mining/scraping_output.log`
3. Restart: Run the command again (it will skip duplicates)

**If no new articles found:**
- The search queries might be finding articles we already have
- Try different search terms or expand date range
- Check if database actually has 4,671 articles (might be more)

---

**The script is designed to run continuously and will not stop until:**
1. Target of 5,000 new articles is reached, OR
2. All 8 queries are exhausted
