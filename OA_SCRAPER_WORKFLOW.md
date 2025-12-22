# ✅ OA Literature Mining Workflow - Updated

## What Changed

The workflow has been **switched from cancer monitoring to OA (Osteoarthritis) literature mining**.

### Before:
- ❌ Node.js cancer monitoring (`scripts/pubmed-monitor.js`)
- ❌ LINCS drug-gene interaction monitoring
- ❌ Cancer-focused searches (STK17A, MYLK4, TBK1, CLK4 genes)
- ❌ Google Sheets storage (for cancer monitoring)

### After:
- ✅ **Python OA scraper** (`pubmed-literature-mining/scripts/pubmed_scraper.py`)
- ✅ **OA-focused searches**: Knee osteoarthritis progression studies
- ✅ **File-based storage** (100% free, version-controlled in Git)
- ✅ **Automatic analysis and notifications**

## What the Workflow Does

1. **Searches PubMed** for:
   - Knee osteoarthritis progression studies
   - Total knee replacement (TKR) / arthroplasty studies
   - Clinical trials, cohort studies, systematic reviews
   - Human studies only

2. **Processes Articles**:
   - Checks open access status (Unpaywall, PMC, Europe PMC)
   - Downloads PDFs for open-access articles
   - Calculates relevance scores
   - Extracts predictive factors (biomarkers, risk factors, etc.)

3. **Stores Data**:
   - Saves articles as JSON files in `pubmed-literature-mining/data/articles/`
   - Automatically commits to Git
   - Creates daily summaries

4. **Analyzes & Notifies**:
   - Identifies high-relevance articles
   - Flags paywalled articles above threshold
   - Detects common predictive factors
   - Creates GitHub issues/notifications

## Schedule

- **Frequency**: Weekly (every Monday at 2 AM EST / 7 AM UTC)
- **Manual Trigger**: Available via GitHub Actions UI
- **Timeout**: 30 minutes per run

## Storage

- **Type**: File-based (JSON files in Git)
- **Location**: `pubmed-literature-mining/data/articles/`
- **Cost**: $0 (100% free)
- **Benefits**: 
  - Full version history in Git
  - No external dependencies
  - Easy to query and analyze
  - Transparent and auditable

## No Secrets Required!

The OA scraper uses:
- ✅ **Public PubMed API** (no key needed)
- ✅ **File storage** (no database needed)
- ✅ **GitHub Actions** (built-in GITHUB_TOKEN)

**Optional** (for notifications):
- `GITHUB_TOKEN` - Auto-provided by GitHub Actions
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` - Only if you want AI analysis (currently not in workflow)

## Output

After each run, you'll find:

1. **Article Data**: `pubmed-literature-mining/data/articles/` (committed to Git)
2. **Logs**: `pubmed-literature-mining/logs/` (uploaded as artifacts)
3. **Summary**: `pubmed-literature-mining/LATEST_FINDINGS.md` (committed to Git)
4. **Metrics**:
   - `logs/daily_count.txt` - Articles processed
   - `logs/paywalled_count.txt` - Paywalled articles
   - `logs/factors_count.txt` - Predictive factors found

## Next Steps

1. ✅ **Workflow is ready** - Just trigger it manually or wait for Monday
2. ✅ **No setup needed** - Everything is configured
3. ✅ **Monitor results** - Check the workflow runs and commit history

## Differences from Cancer Monitoring

| Feature | Cancer Monitoring | OA Scraper |
|---------|------------------|------------|
| **Language** | Node.js | Python |
| **Focus** | Cancer genes (STK17A, etc.) | Knee OA progression |
| **Storage** | Google Sheets / File | File only |
| **LINCS** | Yes | No |
| **AI Analysis** | Separate job | Built-in analysis |
| **Cost** | Google Sheets API | $0 (100% free) |

## Testing

To test the workflow:

1. Go to: https://github.com/ParkerCase/doc/actions
2. Click "OA Literature Mining - Weekly"
3. Click "Run workflow" → "Run workflow"
4. Monitor the run and check logs

The workflow will:
- Install Python dependencies
- Run the OA scraper
- Analyze results
- Commit data to Git
- Upload logs as artifacts

## Questions?

- **Why file storage instead of Google Sheets?** The OA scraper was built with file storage for simplicity and cost-effectiveness. If you want Google Sheets integration, we can add it.
- **Can I change the schedule?** Yes! Edit the `cron` expression in the workflow file.
- **What if I want daily runs?** Change `cron: "0 7 * * 1"` to `cron: "0 7 * * *"` (daily at 7 AM UTC).

