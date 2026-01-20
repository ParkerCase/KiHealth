# Final Instructions: Run Batch 2 Scraping

## ✅ The Script is Fixed and Working!

The script now correctly finds **4,671 existing articles** in the database and will find NEW ones.

## How to Run

**Simple command:**
```bash
cd /Users/parkercase/DOC
python pubmed-literature-mining/scripts/scrape_batch_2_robust.py
```

**Or use the helper script:**
```bash
cd /Users/parkercase/DOC
./pubmed-literature-mining/START_SCRAPING.sh
```

## What It Does

1. ✅ **Finds 4,671 existing articles** in database
2. ✅ **Runs 8 different search queries** to find NEW articles
3. ✅ **Filters duplicates** before processing (faster)
4. ✅ **Processes only new articles**
5. ✅ **Continues until 5,000 new articles found**
6. ✅ **Shows progress** after each query

## Expected Behavior

- **Query 1:** Finds 5,000 articles, most are duplicates (skipped quickly)
- **Queries 2-8:** Find different articles, more will be NEW
- **Progress:** Updates every 100 articles processed
- **Time:** 1-3 hours total

## Monitor Progress

**Check how many articles:**
```bash
cd pubmed-literature-mining
python -c "import sqlite3; conn = sqlite3.connect('data/literature.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM papers'); print(f'Total: {cursor.fetchone()[0]}'); conn.close()"
```

**Watch the output:**
The script will show:
- "Found X PMIDs in database" (should be 4,671)
- "New (not in database): X PMIDs" (these will be processed)
- "Progress: X new articles" (increases as new ones are found)

## Why It Looks Like It Stopped

- **Most articles are duplicates** - skipped in <1 second
- **Processing takes time** - even with fast skipping, thousands of articles take hours
- **Progress updates** every 100 articles - might not see updates if processing duplicates quickly

## The Script WILL Continue

The script is designed to:
- ✅ Process ALL articles from each query
- ✅ Continue to next query automatically
- ✅ Not stop until target reached or all queries exhausted

---

**Just run it and let it work!** It will continue running until it finds 5,000 new articles or exhausts all 8 queries.
