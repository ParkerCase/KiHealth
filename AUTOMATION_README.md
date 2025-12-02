# 🤖 Automated Monitoring System - Complete Guide

## Overview

This system automatically monitors PubMed and LINCS for new research relevant to StarX Therapeutics targets, analyzes papers with AI, and recalculates rankings when new data arrives.

**No API keys required for PubMed or LINCS** - both use public APIs!

---

## 📋 System Components

### 1. **PubMed Monitor** (`scripts/pubmed-monitor.js`)

- ✅ Searches PubMed for articles about target genes and cancer types
- ✅ No API key required (uses public E-utilities API)
- ✅ Extracts article metadata
- ✅ Stores in Xata `papers` table

### 2. **LINCS Monitor** (`scripts/lincs-monitor.js`)

- ✅ Searches LINCS L1000 database for drug-gene interactions
- ✅ No API key required (uses public LINCS API)
- ✅ Extracts compound efficacy data
- ✅ Stores in Xata `lincs_data` table

### 3. **AI Analysis** (`scripts/ai-analyze-papers.js`)

- ✅ Uses Claude API to analyze papers
- ✅ Generates relevance scores (0-1)
- ✅ Extracts key findings
- ✅ Identifies mentioned cancer types and targets
- ⚠️ **Requires ANTHROPIC_API_KEY**

### 4. **Auto-Recalculation** (`scripts/auto-recalculate.js`)

- ✅ Detects new high-relevance data
- ✅ Triggers ranking recalculation
- ✅ Tracks changes in rankings
- ✅ Creates dashboard alerts

### 5. **GitHub Actions** (`.github/workflows/daily-monitoring.yml`)

- ✅ Runs daily at 2 AM EST
- ✅ Can be manually triggered
- ✅ Executes all monitoring scripts in sequence

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
cd scripts
npm install
```

This installs:

- `@xata.io/client` - Xata database client
- `@anthropic-ai/sdk` - Claude API client
- `axios` - HTTP requests
- `dotenv` - Environment variables
- `xml2js` - XML parsing

### Step 2: Configure Environment Variables

Create `scripts/.env`:

```env
# Required
XATA_API_KEY=your_xata_api_key
XATA_DB_URL=https://your-workspace.region.xata.sh/db/your-db-name:main

# Required for AI analysis
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**Note**: No API keys needed for PubMed or LINCS!

### Step 3: Create Xata Tables

Import the CSV files to create tables:

- `scripts/papers.csv` → Creates `papers` table
- `scripts/lincs_data.csv` → Creates `lincs_data` table

See `XATA_CSV_IMPORT_GUIDE.md` for details.

### Step 4: Configure GitHub Secrets

Add these secrets to your GitHub repository:

1. Go to: **Settings → Secrets and variables → Actions**
2. Add:
   - `XATA_API_KEY`
   - `XATA_DB_URL`
   - `ANTHROPIC_API_KEY` (for AI analysis)

---

## 🧪 Manual Testing

### Test PubMed Monitor

```bash
cd scripts
npm run monitor
```

**Expected output:**

- Searches PubMed for articles
- Logs to `../logs/pubmed-YYYY-MM-DD.log`
- Stores articles in Xata `papers` table

### Test LINCS Monitor

```bash
cd scripts
node lincs-monitor.js
```

**Expected output:**

- Searches LINCS for drug-gene interactions
- Logs to `../logs/lincs-YYYY-MM-DD.log`
- Stores records in Xata `lincs_data` table

### Test AI Analysis

```bash
cd scripts
node ai-analyze-papers.js
```

**Expected output:**

- Analyzes unscored papers with Claude
- Updates `papers` table with relevance scores
- Logs to `../logs/ai-analyze-YYYY-MM-DD.log`

### Test Auto-Recalculation

```bash
cd scripts
node auto-recalculate.js
```

**Expected output:**

- Checks for new data
- Recalculates rankings if needed
- Logs changes to `../logs/recalculate-YYYY-MM-DD.log`

---

## 📊 What Gets Monitored

### PubMed Searches

**Target Genes:**

- STK17A
- MYLK4
- TBK1
- CLK4
- STK17B

**Cancer Types (Top 20):**

- Acute Myeloid Leukemia
- Diffuse Glioma
- Extra Gonadal Germ Cell Tumor
- Melanoma
- Esophagogastric Adenocarcinoma
- Non-Small Cell Lung Cancer
- Mature T and NK Neoplasms
- Colorectal Adenocarcinoma
- Endometrial Carcinoma
- Head and Neck Squamous Cell Carcinoma
- Leiomyosarcoma
- Bladder Urothelial Carcinoma
- Ovarian Epithelial Tumor
- Pancreatic Adenocarcinoma
- Ocular Melanoma
- B-Cell Acute Lymphoblastic Leukemia
- Mature B-Cell Neoplasms
- Myeloproliferative Neoplasms
- Lung Neuroendocrine Tumor
- Osteosarcoma

**Combination Queries:**

- Each target gene × Top 5 cancer types

### LINCS Searches

**Target Genes:**

- STK17A (Entrez ID: 9263)
- MYLK4 (Entrez ID: 340156)
- TBK1 (Entrez ID: 29110)
- CLK4 (Entrez ID: 57396)
- STK17B (Entrez ID: 9262)

---

## 🔄 Automation Schedule

### Daily Workflow (GitHub Actions)

**Runs at:** 2 AM EST (7 AM UTC) daily

**Job Sequence:**

1. **PubMed Monitoring** (5-10 minutes)
2. **LINCS Monitoring** (5-10 minutes)
3. **AI Analysis** (10-20 minutes, depends on paper count)
4. **Auto-Recalculation** (if new data found, 1-5 minutes)

**Total time:** ~20-45 minutes

### Manual Trigger

You can manually trigger the workflow:

1. Go to **Actions** tab in GitHub
2. Select **Daily Monitoring System**
3. Click **Run workflow**

---

## 📝 Logging

All scripts log to `logs/` directory:

- `pubmed-YYYY-MM-DD.log` - PubMed monitoring logs
- `lincs-YYYY-MM-DD.log` - LINCS monitoring logs
- `ai-analyze-YYYY-MM-DD.log` - AI analysis logs
- `recalculate-YYYY-MM-DD.log` - Recalculation logs

Logs include:

- Timestamps
- Success/failure messages
- Error details
- Data counts (new vs. updated records)

---

## 🐛 Troubleshooting

### Error: "XATA_API_KEY is not set"

→ Add `XATA_API_KEY` to `scripts/.env` or GitHub secrets

### Error: "ANTHROPIC_API_KEY is not set"

→ Add `ANTHROPIC_API_KEY` to `scripts/.env` or GitHub secrets (only needed for AI analysis)

### Error: "Table papers not found"

→ Import `scripts/papers.csv` into Xata first

### Error: "Table lincs_data not found"

→ Import `scripts/lincs_data.csv` into Xata first

### PubMed rate limit errors

→ Script handles this automatically with retries and rate limiting

### LINCS API timeout

→ LINCS API can be slow. Script has 30-second timeout and retries.

### AI analysis taking too long

→ Processes 10 papers at a time with 1 request/second rate limit. Large backlogs may take hours.

---

## 🔧 Customization

### Change Search Parameters

Edit `scripts/pubmed-monitor.js`:

- `DAYS_BACK` - How many days to look back (default: 30)
- `MAX_ARTICLES_PER_SEARCH` - Articles per query (default: 50)
- `TOP_CANCER_TYPES` - Which cancers to search

### Change AI Analysis Settings

Edit `scripts/ai-analyze-papers.js`:

- `BATCH_SIZE` - Papers per batch (default: 10)
- `REQUESTS_PER_SECOND` - Claude API rate limit (default: 1)

### Change Recalculation Thresholds

Edit `scripts/auto-recalculate.js`:

- `SCORE_CHANGE_THRESHOLD` - Flag score changes > this (default: 0.05)
- `RANK_CHANGE_THRESHOLD` - Flag rank changes > this (default: 5)

---

## 📈 Expected Results

### After First Run

**PubMed:**

- 50-200 new articles (depending on recent publications)
- Stored in `papers` table with metadata

**LINCS:**

- 10-50 drug-gene interaction records
- Stored in `lincs_data` table

**AI Analysis:**

- Relevance scores for all papers
- Key findings extracted
- Cancer types and targets identified

**Recalculation:**

- Rankings updated if significant new data
- Change history stored
- Dashboard alerts created

---

## ✅ Verification Checklist

- [ ] Dependencies installed (`npm install` in `scripts/`)
- [ ] Environment variables configured (`.env` file)
- [ ] Xata tables created (`papers` and `lincs_data`)
- [ ] GitHub secrets added (XATA_API_KEY, XATA_DB_URL, ANTHROPIC_API_KEY)
- [ ] Tested locally (all scripts run successfully)
- [ ] GitHub Actions workflow enabled
- [ ] First workflow run successful

---

## Next Steps

1. **Run first manual test** - Verify all scripts work
2. **Check Xata tables** - Confirm data is being stored
3. **Review logs** - Check for any errors
4. **Enable GitHub Actions** - Let it run automatically
5. **Monitor dashboard** - Watch for new data and alerts

---

## 📚 Additional Resources

- **PubMed API Docs**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **LINCS API Docs**: http://api.lincscloud.org/
- **Claude API Docs**: https://docs.anthropic.com/
- **Xata Docs**: https://xata.io/docs

---

## 🆘 Support

If you encounter issues:

1. Check the log files in `logs/` directory
2. Verify environment variables are set correctly
3. Ensure Xata tables exist and have correct schema
4. Check GitHub Actions logs for workflow errors

---

**Status**: ✅ All components ready to use!
**No API keys needed for PubMed or LINCS** - just Xata and Claude (for AI analysis).
