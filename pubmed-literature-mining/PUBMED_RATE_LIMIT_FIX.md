# PubMed Rate Limit Fix

## Problem
PubMed API was returning 500 Server Errors due to:
1. **Too many complex queries** hitting rate limits
2. **Too many requests too fast**
3. **Queries too complex** (too many OR conditions)

## Solution Applied

### 1. Simplified Queries
- Removed complex MeSH terms and multiple OR conditions
- Simplified to basic keyword searches
- Reduced from 8 complex queries to 8 simpler ones

### 2. Reduced Request Size
- Changed `max_results=5000` → `max_results=2000`
- Changed `date_range_years=20` → `date_range_years=10`
- Less data per request = less likely to timeout

### 3. Added Rate Limiting
- 2 second delay after each search
- 30 second delay after errors
- 0.5 second delay every 10 articles
- 2 second delay every 50 articles

### 4. Better Error Handling
- Script continues to next query if one fails
- Waits longer after errors before retrying

## How to Run Now

```bash
cd /Users/parkercase/DOC
python pubmed-literature-mining/scripts/scrape_batch_2_robust.py
```

## Expected Behavior

- **Slower but more reliable** - won't hit rate limits
- **Will process all queries** - even if some fail
- **Will add new articles** - as long as queries succeed
- **Takes longer** - but actually completes

## If Still Getting Errors

1. **Wait 10-15 minutes** - PubMed may have temporary rate limits
2. **Run during off-peak hours** - less API traffic
3. **Reduce queries further** - comment out some queries in the script

---

**The script is now optimized to avoid rate limits while still finding new articles.**
