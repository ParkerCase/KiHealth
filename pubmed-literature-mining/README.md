# PubMed Literature Mining System

Automated system for monitoring PubMed for knee osteoarthritis progression studies, analyzing open-access articles, flagging paywalled articles, identifying predictive factors, and notifying via GitHub when actionable insights are found.

## Features

- 🔍 **Automated PubMed Search**: Daily queries for OA progression studies
- 📄 **Open Access Detection**: Checks Unpaywall, PMC, and Europe PMC
- 📊 **Relevance Scoring**: 0-100 score based on keywords, study design, sample size, and journal impact
- 🧬 **Factor Extraction**: NLP-based extraction of predictive factors from abstracts and full-text
- 🔔 **GitHub Notifications**: Creates issues, commits summaries, and workflow annotations
- 💾 **File-Based Storage**: Stores all metadata in version-controlled JSON files (100% free)
- 🧪 **Comprehensive Testing**: Test suite with >80% coverage

## System Architecture

```
pubmed-literature-mining/
├── .github/workflows/     # GitHub Actions automation
├── scripts/               # Core Python scripts
├── tests/                 # Test suite
├── data/pdfs/            # Downloaded PDFs (gitignored)
├── logs/                 # Log files
└── config/               # Configuration files
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- GitHub repository
- (Optional) GitHub token for issue creation

**Note**: No database required! Uses free file-based storage in the repository.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)

Create a `.env` file in the project root (optional - defaults work):

```bash
# Unpaywall Configuration
UNPAYWALL_EMAIL=parker@stroomai.com

# PubMed API Configuration
PUBMED_EMAIL=parker@stroomai.com
PUBMED_TOOL=PubMedLiteratureMining

# Processing Configuration
MAX_ARTICLES_PER_RUN=100
RELEVANCE_THRESHOLD=70

# GitHub Configuration (optional, for issue creation)
GITHUB_REPO_OWNER=your_github_username
GITHUB_REPO_NAME=your_repo_name
GITHUB_TOKEN=your_github_token_here
```

**Note**: No database setup required! Articles are stored in `data/articles/` as JSON files, automatically version-controlled by Git.

### 4. Configure GitHub Secrets (Optional)

Only needed if you want GitHub issue notifications:

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions (no setup needed)

The workflow will automatically use `GITHUB_TOKEN` for repository operations.

### 5. Test Locally

Run the scraper manually:

```bash
python scripts/pubmed_scraper.py
```

Run the analysis and notification:

```bash
python scripts/analyze_and_notify.py
```

Run tests:

```bash
pytest tests/ -v --cov=scripts --cov-report=html
```

## Usage

### Manual Execution

The system can be run manually via:

1. **Command line**:
   ```bash
   python scripts/pubmed_scraper.py
   python scripts/analyze_and_notify.py
   ```

2. **GitHub Actions**: Use the "Run workflow" button in the Actions tab

### Automated Execution

The GitHub Actions workflow runs automatically:
- **Schedule**: Daily at 6 AM UTC (1 AM EST)
- **Manual trigger**: Available via `workflow_dispatch`

## How It Works

### Phase 1: PubMed Search

1. Queries PubMed using Entrez E-utilities API
2. Search terms: `("knee osteoarthritis" OR "knee OA") AND ("progression" OR "total knee replacement" OR "arthroplasty")`
3. Filters: Last 5 years, human studies, clinical trials/cohort studies/systematic reviews
4. Retrieves: PMID, Title, Abstract, Authors, Journal, DOI, Publication Date

### Phase 2: Open Access Detection

1. Checks **Unpaywall API** (primary)
2. Falls back to **PubMed Central (PMC)** if PMCID exists
3. Tertiary check: **Europe PMC**
4. Downloads PDF if open access
5. Extracts text using `pdfplumber` or `PyPDF2`

### Phase 3: Relevance Scoring

Scores each article 0-100 based on:

- **Keywords (40 points)**: Predictive factors, outcomes, imaging, symptoms, statistical terms
- **Study Design (30 points)**: Systematic review (20), Cohort/RCT (15), Case-control (10), Cross-sectional (5)
- **Sample Size (15 points)**: ≥1000 (15), 500-999 (10), 100-499 (5), <100 (2)
- **Journal Impact (15 points)**: Top-tier (15), Mid-tier (10), Other (5)

### Phase 4: Factor Extraction

Extracts predictive factors using:
- Regex patterns for statistical associations (OR, HR, p-values, AUC)
- Keyword matching for known factors
- Context extraction from surrounding text

Target factors:
- Demographics (age, sex, BMI)
- Symptoms (WOMAC, KOOS, pain scores)
- Imaging (KL grade, joint space narrowing)
- Biomarkers (CTX-II, HA, MMP-3)
- Comorbidities, functional measures, psychosocial factors

### Phase 5: Notifications

Creates GitHub notifications when:

1. **5+ paywalled articles** with relevance ≥70 → Creates issue
2. **5+ articles mention same factor** → Creates issue
3. **Daily summary** → Commits to repository
4. **Workflow annotations** → Visible in Actions summary

## Output Files

- `LATEST_FINDINGS.md`: Daily summary of findings
- `logs/pubmed_scraper.log`: Detailed execution log
- `logs/daily_summary.json`: JSON summary of daily run
- `logs/daily_count.txt`: Number of articles processed
- `logs/paywalled_count.txt`: Number of paywalled articles
- `logs/factors_count.txt`: Total predictive factors extracted

## Error Handling

The system is designed for 100% error resilience:

- ✅ Retry failed API calls with exponential backoff
- ✅ Skip malformed data and continue processing
- ✅ Log all errors but never crash
- ✅ Rate limit compliance (PubMed: 3 req/sec, Unpaywall: 100k/day)
- ✅ Handle encoding issues (UTF-8)
- ✅ Validate all data before storage

## Rate Limits

- **PubMed**: 3 requests/second (enforced with 0.34s delay)
- **Unpaywall**: 100,000 requests/day (no limit for this use case)
- **GitHub API**: 5,000 requests/hour (sufficient for daily runs)

## Testing

Run the full test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=scripts --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # macOS
```

## Monitoring

### GitHub Actions

Check workflow runs in the Actions tab:
- ✅ Green: Successful run
- ⚠️ Yellow: Warnings (e.g., no new articles)
- ❌ Red: Errors (check logs)

### Article Database

Monitor article storage:
- View articles in `data/articles/` directory
- Each article stored as JSON file
- Index file at `data/articles/index.json` for fast lookups
- All data version-controlled in Git

### Log Files

Review `logs/pubmed_scraper.log` for:
- Articles processed
- Errors encountered
- Relevance scores
- Factors extracted

## Troubleshooting

### No articles found

- Check PubMed API is accessible
- Verify search query syntax
- Check date filters (last 5 years)

### Xata connection errors

- Verify `XATA_API_KEY` and `XATA_DATABASE_URL` are correct
- Check Xata service status
- Verify table schema matches expected format

### PDF download failures

- Check network connectivity
- Verify PDF URLs are accessible
- Some publishers may block automated downloads

### Low relevance scores

- Adjust keyword weights in `config/keywords.json`
- Modify scoring thresholds in `.env`
- Review sample articles to identify missing keywords

## Configuration

### Adjusting Search Query

Edit `scripts/pubmed_scraper.py`:

```python
query = '("knee osteoarthritis" OR "knee OA") AND ("progression" OR ...)'
```

### Modifying Relevance Scoring

Edit `config/keywords.json` to add/remove keywords or adjust categories.

### Changing Notification Thresholds

Edit `.env`:

```bash
RELEVANCE_THRESHOLD=70  # Minimum score for notifications
```

Or edit `scripts/analyze_and_notify.py`:

```python
self.relevance_threshold = 70  # Change threshold
```

## Deployment Checklist

Before enabling daily schedule:

- [ ] All tests pass (`pytest tests/`)
- [ ] GitHub Secrets configured
- [ ] Xata database schema created
- [ ] Manual workflow run successful
- [ ] Emails/notifications received
- [ ] Logs reviewed for errors
- [ ] Relevance scores validated
- [ ] PDF downloads working

## License

This project is for research purposes. Ensure compliance with:
- PubMed API terms of service
- Unpaywall API terms of service
- Publisher copyright policies for PDF downloads

## Support

For issues or questions:
1. Check logs in `logs/pubmed_scraper.log`
2. Review GitHub Actions workflow logs
3. Verify environment variables are set correctly
4. Test individual components (see Testing section)

## Future Enhancements

Potential improvements:
- Machine learning for relevance scoring
- Advanced NLP for factor extraction
- Integration with reference managers
- Automated literature review generation
- Multi-disease support

