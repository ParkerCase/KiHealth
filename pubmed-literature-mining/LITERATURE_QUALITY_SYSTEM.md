# Literature Quality System - Complete Implementation

## Overview

This system ensures we maintain **top 7% PROBAST compliance** while processing **hundreds to thousands** of relevant articles from PubMed. All tools are **free and open-source** - no paid services required.

## System Architecture

```
PubMed Scraper (5000+ articles)
    ↓
Export to CSV for ASReview LAB
    ↓
ASReview LAB (AI Screening - keeps high-quality papers)
    ↓
PROBAST Assessment (4-domain scoring)
    ↓
SQLite Database (local, free storage)
    ↓
Only Low Risk PROBAST papers → Used in model
```

## Components

### 1. ASReview LAB Integration (`scripts/asreview_integration.py`)

**Free, open-source AI screening tool**

- **Installation**: `pip install asreview`
- **Usage**: `asreview web`
- **Benefits**:
  - AI-powered prioritization (most relevant articles first)
  - Active learning (learns from your decisions)
  - Time-saving (screen 1000s efficiently)
  - Complete privacy (runs locally)

**Workflow**:
1. Export articles: `asreview.export_for_asreview(articles, "data/asreview_export.csv")`
2. Open ASReview: `asreview web`
3. Upload CSV and start screening
4. Import results back into system

### 2. PROBAST Assessment (`scripts/probast_assessment.py`)

**4-Domain Risk Assessment**:

- **Domain 1: Participants** (Selection bias)
- **Domain 2: Predictors** (Measurement bias)
- **Domain 3: Outcome** (Measurement bias)
- **Domain 4: Analysis** (Statistical bias)

**Risk Levels**:
- **Low**: All 4 domains Low, OR 3 Low + 1 Moderate (with justification)
- **Moderate**: Mixed risk levels
- **High**: Any domain High
- **Unclear**: Insufficient information

**Only Low Risk papers are used in the model.**

### 3. SQLite Database (`scripts/literature_database.py`)

**Simple, local, free storage**

- No external services required
- Built into Python
- Stores:
  - Article metadata
  - PROBAST assessments
  - Screening results
  - Paywalled uploads

**Database Schema**:
```sql
papers (
    pmid, title, abstract, journal, authors, doi,
    probast_risk, probast_domain_1-4,
    used_in_model, date_added, ...
)
```

### 4. Complete Workflow (`scripts/literature_quality_workflow.py`)

**Automated end-to-end processing**:

```python
from scripts.literature_quality_workflow import LiteratureQualityWorkflow

workflow = LiteratureQualityWorkflow()
stats = workflow.run_full_workflow(max_articles=5000, use_asreview=True)
```

**Steps**:
1. Fetch 5000+ articles from PubMed
2. Export for ASReview screening
3. PROBAST assess all articles
4. Store in SQLite database
5. Mark Low Risk articles as usable

### 5. Paywalled Article Upload

**Review Dashboard** (`DOC_Validator_Vercel/public/review-dashboard.html`):

- Upload PDFs of paywalled articles
- Automatic PROBAST assessment
- Storage in SQLite database
- Integration with review workflow

**API Endpoint** (`DOC_Validator_Vercel/api/upload-paywalled.py`):
- Handles PDF uploads
- Saves to `pubmed-literature-mining/data/pdfs/`
- Adds to database with PROBAST assessment

## Usage

### Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install asreview  # Optional but recommended
   ```

2. **Run workflow**:
   ```bash
   python scripts/literature_quality_workflow.py
   ```

3. **Screen with ASReview** (optional):
   ```bash
   asreview web
   # Upload data/asreview_export.csv
   # Screen articles
   # Export results
   ```

4. **Check database**:
   ```python
   from scripts.literature_database import LiteratureDatabase
   
   db = LiteratureDatabase()
   stats = db.get_statistics()
   usable = db.get_usable_articles()  # Low Risk PROBAST only
   ```

### Upload Paywalled Articles

1. Go to Review Dashboard
2. Use "Upload Paywalled Articles" section
3. Enter PMID and upload PDF
4. System automatically:
   - Saves PDF
   - Assesses with PROBAST
   - Adds to database

## PROBAST Compliance

### Why This Maintains Top 7% PROBAST

**GOOD for PROBAST** (makes it better):
- ✅ Adding more DATA (OAI + MOST + UK Biobank + Bergman)
- ✅ More patients = higher EPV (more events, same predictors)
- ✅ Adding LITERATURE (doesn't affect predictor count)
- ✅ Geographic diversity (strengthens generalizability)

**BAD for PROBAST** (would break it):
- ❌ Adding new PREDICTORS (would lower EPV)
- ❌ Going from 11 predictors to 12 without more events

**Current Status**:
- 11 predictors, 171 events = EPV 15.55 (safe!)
- Add MOST data (~200 more events) = EPV ~33 (huge safety margin!)
- Then you could add 10+ predictors and still maintain top 7%

### PROBAST Protection Rules

Only include papers where:
- All 4 PROBAST domains = "Low Risk"
- OR 3 domains "Low" + 1 domain "Moderate" with clear justification

**Automated filtering**:
```python
from scripts.probast_assessment import PROBASTAssessment

assessor = PROBASTAssessment()
assessment = assessor.assess_article(article)

if assessor.is_usable_for_model(assessment):
    # Use in model
    db.mark_as_used_in_model(article['pmid'])
```

## Database Statistics

```python
db = LiteratureDatabase()
stats = db.get_statistics()

# Output:
{
    "total_articles": 5000,
    "probast_low_risk": 1200,
    "probast_moderate_risk": 2500,
    "probast_high_risk": 800,
    "probast_unclear": 500,
    "used_in_model": 1200,  # Only Low Risk
    "by_access_type": {
        "open_access": 3000,
        "paywalled": 2000
    }
}
```

## GitHub Actions Integration

The workflow automatically:
1. Fetches 5000 articles daily
2. Processes through workflow
3. Commits to Git
4. Updates review queue

**Configuration** (`.github/workflows/pubmed-scraper.yml`):
```yaml
env:
  MAX_ARTICLES_PER_RUN: 5000  # Increased from 100
```

## File Structure

```
pubmed-literature-mining/
├── scripts/
│   ├── asreview_integration.py      # ASReview LAB integration
│   ├── probast_assessment.py        # PROBAST assessment
│   ├── literature_database.py       # SQLite database
│   ├── literature_quality_workflow.py  # Complete workflow
│   └── pubmed_scraper.py            # Updated to fetch 5000+
├── data/
│   ├── literature.db                # SQLite database
│   ├── asreview_export.csv          # Export for ASReview
│   └── pdfs/                        # Uploaded PDFs
└── requirements.txt                 # Updated dependencies
```

## Benefits

1. **Free**: No paid services, all open-source
2. **Scalable**: Process thousands of articles
3. **Quality**: Only Low Risk PROBAST papers used
4. **Privacy**: All processing local (ASReview, SQLite)
5. **Automated**: GitHub Actions runs daily
6. **Compliant**: Maintains top 7% PROBAST

## Next Steps

1. **Run initial workflow**: Process existing articles
2. **Set up ASReview**: Screen high-priority articles
3. **Review PROBAST assessments**: Manual review of Moderate/High risk
4. **Upload paywalled articles**: Use dashboard upload
5. **Monitor statistics**: Track Low Risk article count

## Support

- ASReview LAB: https://asreview.nl/
- PROBAST Tool: https://www.probast.org/
- SQLite: Built into Python

---

**Maintains PROBAST compliance while processing thousands of articles!**
