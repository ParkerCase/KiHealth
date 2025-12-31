# Export Paywalled Articles to Logs

## Overview

Since Google Sheets has quota limitations and isn't always reliable, we've created a dedicated script that exports a comprehensive, sorted list of all paywalled articles directly to the logs directory.

## Script: `export_paywalled_to_logs.py`

This script:
- **Prioritizes file storage** (more reliable, no quota issues)
- **Falls back to Google Sheets** (if available and not hitting quota)
- **Sorts articles by relevance score** (best to least valuable)
- **Exports detailed information** to `logs/paywalled_articles_sorted.log`

## Usage

### Command Line

```bash
# Export all paywalled articles (default threshold=0)
python scripts/export_paywalled_to_logs.py

# Export only high-relevance paywalled articles (score ≥ 70)
python scripts/export_paywalled_to_logs.py --threshold 70

# Custom output directory
python scripts/export_paywalled_to_logs.py --output-dir custom_logs
```

### In GitHub Actions

The script runs automatically in the workflow after analysis, exporting all paywalled articles to the logs directory.

## Output Format

The log file (`logs/paywalled_articles_sorted.log`) contains:

1. **Header**: Generation timestamp, total count
2. **Summary Statistics**:
   - Highest/Lowest/Average relevance scores
   - Distribution by score ranges (≥70, 50-69, <50)
3. **Detailed List**: Each article includes:
   - Relevance score (sorted highest to lowest)
   - Title, Journal, PMID
   - DOI and links (DOI link, PubMed link)
   - Authors, Publication Date
   - Predictive Factors (if extracted)
   - Abstract Preview (first 500 characters)

## Example Output

```
====================================================================================================
PAYWALLED ARTICLES - SORTED BY RELEVANCE (BEST TO LEAST VALUABLE)
====================================================================================================
Generated: 2025-12-31 13:26:40
Total Articles: 124

SUMMARY STATISTICS:
  - Highest Score: 85.0/100
  - Lowest Score: 5.0/100
  - Average Score: 42.3/100
  - Articles with Score ≥ 70: 12
  - Articles with Score ≥ 50: 45
  - Articles with Score ≥ 30: 89

====================================================================================================
#1 - RELEVANCE SCORE: 85.0/100
====================================================================================================
Title: [Article Title]
Journal: [Journal Name]
PMID: [PMID]
DOI: [DOI]
...
```

## Benefits

1. **Reliable**: Uses file storage as primary source (no quota issues)
2. **Complete**: Merges from both file storage and Google Sheets
3. **Sorted**: Automatically sorted by relevance (best first)
4. **Detailed**: Includes all important article information
5. **Accessible**: Saved in logs directory, easy to find and review

## File Location

- **Log File**: `pubmed-literature-mining/logs/paywalled_articles_sorted.log`
- **Artifact**: Available in GitHub Actions artifacts after each run

## Integration

The script is automatically run in the GitHub Actions workflow:
- After article analysis
- Before generating summary files
- Logs are included in workflow artifacts

---

**Note**: This script is designed to work even when Google Sheets has quota errors, ensuring you always have access to the complete list of paywalled articles sorted by value.

