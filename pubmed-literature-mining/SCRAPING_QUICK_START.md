# Quick Start: Run Batch 2 Scraping

## ✅ Simple Command (Copy & Paste)

```bash
cd /Users/parkercase/DOC
python pubmed-literature-mining/scripts/scrape_batch_2_robust.py
```

**That's it!** The script will:
- ✅ Check all 4,671 existing articles in database
- ✅ Run 8 different search queries
- ✅ Find and process NEW articles only
- ✅ Continue until 5,000 new articles found
- ✅ Show progress in real-time

## Run in Background (Recommended)

If you want to run it in the background:

```bash
cd /Users/parkercase/DOC
nohup python pubmed-literature-mining/scripts/scrape_batch_2_robust.py > pubmed-literature-mining/scraping.log 2>&1 &
```

Then check progress:
```bash
tail -f pubmed-literature-mining/scraping.log
```

## Check Progress

**See how many articles are in database:**
```bash
cd pubmed-literature-mining
python -c "import sqlite3; conn = sqlite3.connect('data/literature.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM papers'); print(f'Total articles: {cursor.fetchone()[0]}'); conn.close()"
```

**Expected:** Starts at 4,671, increases as new articles are added.

## What to Expect

- **Script runs continuously** - won't stop until target reached
- **Progress updates** every 100 articles
- **8 different queries** - finds articles from different angles
- **Error handling** - continues even if individual articles fail
- **Takes 1-3 hours** - processing thousands of articles

## If It Stops

1. **Check the output** - look for error messages
2. **Restart it** - it will skip duplicates automatically
3. **Check database** - see how many articles were added

---

**The script is designed to work continuously. Just run it and let it work!**
