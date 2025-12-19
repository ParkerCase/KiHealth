# Quick Start Guide - Deploy in 5 Minutes

## Step 1: Push to GitHub (2 minutes)

```bash
cd pubmed-literature-mining
git init
git add .
git commit -m "Initial commit: PubMed literature mining system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 2: Test Manually (2 minutes)

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click **"PubMed OA Literature Mining"** workflow
4. Click **"Run workflow"** dropdown
5. Click **"Run workflow"** button
6. Wait 5-10 minutes
7. Check for ✅ green checkmark

## Step 3: Verify It Works (1 minute)

Check these files were created:
- ✅ `data/articles/index.json` - Article index
- ✅ `LATEST_FINDINGS.md` - Daily summary
- ✅ `logs/` directory with log files

## Step 4: Monitor First Week

**Daily**: Check Actions tab for green checkmarks
**After 1 week**: System runs automatically, just check weekly

## That's It! 🎉

The system will now:
- ✅ Run automatically every day at 6 AM UTC
- ✅ Store articles in `data/articles/`
- ✅ Create daily summaries
- ✅ Commit everything to Git
- ✅ Create GitHub issues for important findings

**No further action needed!**

## Optional: Customize

Edit `.github/workflows/pubmed-scraper.yml` to change:
- Schedule time (line 5)
- Max articles per run (line 39)

Edit `config/keywords.json` to adjust:
- Relevance scoring keywords
- Predictive factors to extract

## Troubleshooting

**Workflow fails?**
- Check Actions → Workflow run → Logs
- Most errors are handled gracefully

**No articles found?**
- Normal - depends on PubMed results
- Check search query in `scripts/pubmed_scraper.py` (line 309)

**Questions?**
- Check `README.md` for detailed docs
- Check `DEPLOYMENT_CHECKLIST.md` for monitoring guide

