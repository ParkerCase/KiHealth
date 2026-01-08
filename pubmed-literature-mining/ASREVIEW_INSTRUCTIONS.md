# ASReview LAB - Step-by-Step Instructions

## What is ASReview?

ASReview LAB is an AI-powered tool that helps you **screen thousands of articles efficiently**. It uses machine learning to show you the **most relevant articles first**, so you don't waste time on irrelevant papers.

## Why Use ASReview?

- ✅ **Saves time**: Screen 1000s of articles in hours instead of weeks
- ✅ **AI prioritization**: Most relevant articles shown first
- ✅ **Learns from you**: Gets smarter as you label articles
- ✅ **Free and local**: No data sent anywhere, complete privacy

## Step-by-Step Guide

### Step 1: Run Workflow to Create Export File

```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
python scripts/literature_quality_workflow.py
```

This creates: `data/asreview_export.csv` with all your articles.

### Step 2: Start ASReview Web Interface

```bash
asreview web
```

This will:
- Open a web browser automatically
- Show the ASReview LAB interface
- Usually at: `http://127.0.0.1:5000`

### Step 3: Create New Project

1. In the ASReview web interface, click **"New Project"** button
2. Give it a name (e.g., "Knee OA Literature Review")
3. Click **"Create"**

### Step 4: Upload Your Articles

1. Click **"Add Data"** or **"Import"** button
2. Select **"CSV"** as file type
3. Click **"Browse"** and navigate to:
   ```
   /Users/parkercase/DOC/pubmed-literature-mining/data/asreview_export.csv
   ```
4. Click **"Upload"**

### Step 5: Configure Fields

ASReview will ask you to map your CSV columns:

- **Title field**: Select `title`
- **Abstract field**: Select `abstract`
- **Identifier field**: Select `pmid` (this is the PubMed ID)

Click **"Next"** or **"Continue"**

### Step 6: Start Screening

1. Click **"Start Reviewing"** or **"Begin Screening"**
2. ASReview will show you articles **one at a time**
3. For each article, you'll see:
   - Title
   - Abstract
   - Authors, Journal, etc.

### Step 7: Label Articles

For each article, click:
- **✅ Relevant** (or press `1`) - If the article is relevant to knee OA prediction/progression
- **❌ Irrelevant** (or press `0`) - If the article is not relevant

**Tips**:
- Start with 50-100 labels for best AI performance
- The AI learns from your decisions and improves
- Most relevant articles appear first (AI prioritization)

### Step 8: Export Results (When Done)

1. Click **"Export"** or **"Download Results"**
2. Choose **"CSV"** format
3. Save the file (e.g., `asreview_results.csv`)

The exported file will have:
- All articles you screened
- Labels (Relevant/Irrelevant)
- Priority scores

### Step 9: Use Results in Workflow

You can then import the ASReview results back into the system (this feature can be added if needed).

## Visual Guide

```
ASReview Web Interface:
┌─────────────────────────────────────┐
│  ASReview LAB                       │
├─────────────────────────────────────┤
│                                     │
│  [New Project]  [Open Project]     │
│                                     │
│  Projects:                          │
│  • Knee OA Review (1000 articles)  │
│                                     │
│  [Start Reviewing]                  │
│                                     │
└─────────────────────────────────────┘

When Reviewing:
┌─────────────────────────────────────┐
│  Article 1 of 1000                  │
├─────────────────────────────────────┤
│  Title: Predictors of TKR...        │
│  Abstract: We conducted a...        │
│                                     │
│  [✅ Relevant]  [❌ Irrelevant]     │
│                                     │
└─────────────────────────────────────┘
```

## What "Upload and Screen" Means

**"Upload data/asreview_export.csv"** means:
1. Open ASReview web interface (`asreview web`)
2. Create a new project
3. Click "Add Data" / "Import"
4. Select the CSV file: `data/asreview_export.csv`
5. Map the fields (title, abstract, pmid)
6. Start screening articles

**"Screen articles"** means:
- Review each article shown by ASReview
- Label as Relevant (✅) or Irrelevant (❌)
- The AI learns and shows better articles first
- Continue until you've screened enough (50-100 minimum recommended)

## Time Investment

- **Without ASReview**: Would take weeks to manually review 1000 articles
- **With ASReview**: Can screen 1000 articles in a few hours
  - First 50-100 articles: ~30-60 minutes (manual review)
  - Remaining articles: AI prioritizes, much faster

## Next Steps After ASReview

After screening with ASReview:
1. Export your results
2. The workflow can then process only the "Relevant" articles through PROBAST
3. This saves time by only assessing articles you've already determined are relevant

## Troubleshooting

**ASReview doesn't open browser**:
- Manually go to: `http://127.0.0.1:5000`

**Can't find CSV file**:
- Make sure you ran the workflow first
- Check: `ls -lh data/asreview_export.csv`

**Import fails**:
- Make sure CSV has columns: `pmid`, `title`, `abstract`
- Check file isn't corrupted

---

**Remember**: ASReview is **optional** but **highly recommended** for processing large numbers of articles efficiently!
