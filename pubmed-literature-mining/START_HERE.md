# 🚀 Start Here - Literature Quality System

## ✅ ASReview Installed Successfully!

The dependency warnings you saw are **minor and won't affect ASReview**. You're all set!

## Quick Start Commands

### Option 1: Run Workflow Directly

```bash
# Navigate to the correct directory
cd /Users/parkercase/DOC/pubmed-literature-mining

# Run workflow (will process 5000 articles)
python scripts/literature_quality_workflow.py
```

### Option 2: Use the Helper Script

```bash
cd /Users/parkercase/DOC/pubmed-literature-mining

# Run with default (5000 articles)
./RUN_WORKFLOW.sh

# Or specify number of articles
./RUN_WORKFLOW.sh 1000
```

## Recommended Workflow (Best Results)

Now that ASReview is installed, here's the **optimal workflow**:

### Step 1: Run Workflow to Export Articles
```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
python scripts/literature_quality_workflow.py
```

This will:
- Fetch articles from PubMed (knee OA related)
- Export to `data/asreview_export.csv` for ASReview screening
- Also process articles directly (you can use either approach)

### Step 2: Screen with ASReview (Optional but Recommended)
```bash
asreview web
```

Then in the browser:
1. Click "New Project"
2. Upload `data/asreview_export.csv`
3. Select "Title" and "Abstract" as text fields
4. Select "pmid" as identifier
5. Start screening - AI will show most relevant articles first
6. Label as Relevant (1) or Irrelevant (0)
7. Export results when done

### Step 3: Monitor Progress
```bash
python monitor_system.py
```

## What the System Does

This system is **specifically for your knee osteoarthritis model**:
- ✅ Searches PubMed for knee OA progression and TKR prediction articles
- ✅ Assesses articles with PROBAST (4-domain risk assessment)
- ✅ Only uses **Low Risk PROBAST articles** in the model
- ✅ Maintains **top 7% PROBAST compliance**

## File Locations

- **Workflow script**: `scripts/literature_quality_workflow.py`
- **Database**: `data/literature.db`
- **ASReview export**: `data/asreview_export.csv`
- **Logs**: `logs/`

## Troubleshooting

**If you get "No such file or directory"**:
- Make sure you're in: `/Users/parkercase/DOC/pubmed-literature-mining`
- Check with: `pwd`

**If ASReview doesn't start**:
- Verify installation: `pip show asreview`
- Try: `python -m asreview web`

## Next Steps

1. **Run the workflow** (see commands above)
2. **Monitor results**: `python monitor_system.py`
3. **Optional**: Screen with ASReview for better quality
4. **Check database**: Articles stored in `data/literature.db`

---

**You're ready to go!** 🎉
