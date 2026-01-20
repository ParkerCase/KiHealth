# Broader Scraping Strategy - Update

## What Changed

### Before:
- ❌ Only searched 2024-2025 (too narrow)
- ❌ Very specific search terms
- ❌ Missing ~19,000 articles
- ❌ Only 19% coverage of PubMed

### After:
- ✅ **No date restrictions** on most queries (search all years)
- ✅ **Broader search terms** (knee OA + general topics)
- ✅ **13 queries** covering different aspects
- ✅ **Targets older articles** (2010-2020) we haven't scraped
- ✅ **Still includes recent** (2024-2025) to catch newest

## New Query Strategy

1. **Core topics** (no date restriction):
   - Knee OA + TKR/TKA
   - Knee OA + progression
   - Knee OA + prediction/prognosis
   - Knee OA + risk factors
   - Knee OA + outcomes

2. **Methodology** (no date restriction):
   - Knee OA + machine learning/AI
   - Knee OA + cohort/registry
   - Knee OA + validation

3. **Specific topics** (no date restriction):
   - Knee OA + biomarker
   - Knee OA + imaging

4. **Time-based** (to ensure coverage):
   - Recent: 2024-2025
   - Mid-range: 2015-2020
   - Older: 2010-2014

## Expected Results

- **Before**: Finding mostly duplicates (already scraped recent/specific)
- **After**: Finding thousands of NEW articles from older years
- **Filtering**: Relevance scoring will filter out irrelevant articles
- **Coverage**: Should reach 50-80% of available PubMed articles

## Next Steps

Run the scraper - it will now find many more new articles because:
1. We're searching all years (not just 2024-2025)
2. We're using broader terms
3. We're targeting time periods we haven't covered

The relevance scoring will filter out articles that aren't useful for your model.
