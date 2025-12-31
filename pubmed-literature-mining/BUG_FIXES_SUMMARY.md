# Critical Bug Fixes - December 29, 2025

## Issues Fixed

### 1. ✅ UnboundLocalError: relevance_score variable scope
**Problem**: `relevance_score` variable was only defined in the except block, causing errors when enhanced scoring succeeded.

**Fix**: Changed to use `article_data.get('relevance_score', 0)` instead of the local variable.

**File**: `scripts/pubmed_scraper.py` line 328

### 2. ✅ Paywalled Articles Not Showing
**Problem**: 
- 122 paywalled articles in file storage but 0 shown in reports
- Default threshold was 70, filtering out lower-scored articles
- Google Sheets quota errors preventing proper querying

**Fixes**:
- Changed default threshold from 70 to 0 in `generate_paywalled_list.py` to show ALL paywalled articles
- Changed default threshold from 70 to 0 in `analyze_and_notify.py` 
- Fixed paywalled detection to only count explicitly marked as 'paywalled' (not empty strings)
- HybridStorage now prioritizes file storage (more reliable) over Google Sheets

**Files**: 
- `scripts/generate_paywalled_list.py`
- `scripts/analyze_and_notify.py`
- `scripts/google_sheets_storage.py` (line 306)

### 3. ✅ Google Sheets Quota Errors
**Problem**: 
- Many 429 quota errors when saving to Google Sheets
- Articles not being saved due to quota limits
- No retry logic for quota errors

**Fixes**:
- Added `_retry_with_backoff()` method with exponential backoff for quota errors
- File storage is now PRIMARY storage (always saves)
- Google Sheets is SECONDARY storage (failures don't prevent saving)
- HybridStorage returns success if file storage succeeds, even if Google Sheets fails
- Better error handling and logging for quota errors

**Files**: 
- `scripts/google_sheets_storage.py`
  - Added retry logic to `get_article_by_pmid()`
  - Added retry logic to `insert_article()`
  - Fixed `HybridStorage.insert_article()` to prioritize file storage

### 4. ✅ Articles Not Being Saved
**Problem**: Articles were failing to save due to errors, causing "0 processed" even though articles were found.

**Fixes**:
- Enhanced error handling in `process_article()` 
- File storage always saves (primary storage)
- Better exception handling to ensure articles are saved even if individual steps fail
- More detailed logging

**Files**: 
- `scripts/pubmed_scraper.py`
- `scripts/google_sheets_storage.py`

## Key Changes

### Storage Priority
1. **File Storage** (PRIMARY): Always saves, no quota limits, reliable
2. **Google Sheets** (SECONDARY): Saves if available, failures don't prevent operation

### Paywalled Articles
- Default threshold changed from 70 to 0 (shows ALL paywalled articles)
- Can still use `--threshold 70` to filter for high-relevance only
- File storage is queried first (more reliable)
- Google Sheets is queried second (may hit quota limits)

### Error Handling
- Retry logic with exponential backoff for quota errors
- Graceful degradation (file storage works even if Google Sheets fails)
- Better logging to identify issues

## Testing Recommendations

1. **Run scraper**: Should process articles successfully even with Google Sheets quota errors
2. **Check file storage**: Articles should be in `data/articles/` directory
3. **Check paywalled list**: Should show all 122+ paywalled articles (not just high-scoring ones)
4. **Check Google Sheets**: Articles should eventually sync when quota resets

## Expected Behavior

### After Fixes:
- ✅ Articles are saved to file storage even if Google Sheets fails
- ✅ All paywalled articles are shown (not just score >= 70)
- ✅ No more UnboundLocalError crashes
- ✅ Better handling of Google Sheets quota limits
- ✅ More reliable article storage and retrieval

### Workflow:
1. Scraper finds articles
2. Articles are saved to file storage (always succeeds)
3. Articles are saved to Google Sheets (may fail due to quota, but that's OK)
4. Paywalled articles are queried from file storage first
5. All paywalled articles are shown (threshold=0 by default)

## Next Steps

1. Deploy these fixes
2. Monitor next run for:
   - Successful article processing
   - All paywalled articles showing in reports
   - File storage containing all articles
   - Google Sheets syncing when quota allows

