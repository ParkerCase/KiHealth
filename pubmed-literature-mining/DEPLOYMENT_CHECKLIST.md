# Deployment Checklist - What You Need to Do

## ✅ Automatic (No Action Required)

Once you push to GitHub, these happen automatically:

1. ✅ **Daily runs** - Workflow runs at 6 AM UTC (1 AM EST) every day
2. ✅ **Article storage** - Articles saved to `data/articles/` automatically
3. ✅ **Git commits** - Article data and summaries committed automatically
4. ✅ **Logs** - All logs saved as GitHub Actions artifacts
5. ✅ **Error handling** - System continues even if some articles fail

## ⚠️ Optional Setup (Recommended but Not Required)

### 1. GitHub Issue Notifications (Optional)

**If you want GitHub issues created for paywalled articles:**

- **Action**: None needed! `GITHUB_TOKEN` is automatically provided by GitHub Actions
- **Result**: Issues will be created automatically when 5+ paywalled articles are found

**If you DON'T want issues:**
- System still works, just won't create issues
- You'll still get daily summary commits

### 2. Manual Testing (Recommended First Time)

**Before relying on daily runs, test once manually:**

1. Go to GitHub → Actions tab
2. Click "PubMed OA Literature Mining" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait 5-10 minutes
5. Check that:
   - ✅ Workflow completes successfully (green checkmark)
   - ✅ Articles appear in `data/articles/` directory
   - ✅ `LATEST_FINDINGS.md` is created/updated
   - ✅ No errors in logs

## 📊 What to Monitor

### Daily (First Week)

Check GitHub Actions tab:
- ✅ Green checkmark = Success
- ⚠️ Yellow = Warnings (may be normal)
- ❌ Red = Errors (check logs)

### Weekly (After First Week)

1. **Review `LATEST_FINDINGS.md`** - See what articles were found
2. **Check `data/articles/`** - Verify articles are being stored
3. **Review any GitHub issues** - If paywalled articles found

### Monthly

1. **Review relevance scores** - Are they reasonable?
2. **Check article count** - Is it growing as expected?
3. **Review extracted factors** - Are they useful?

## 🚨 When to Take Action

### Red Flags (Take Action):

1. **Workflow fails repeatedly** → Check logs, may need to adjust search query
2. **No articles found for days** → Check PubMed API status
3. **Storage errors** → Check repository size (unlikely)
4. **Rate limit errors** → Reduce `MAX_ARTICLES_PER_RUN` in workflow

### Normal (No Action Needed):

- ⚠️ Some articles fail to process (normal - system continues)
- ⚠️ No new articles some days (normal - depends on PubMed)
- ⚠️ Warnings in logs (normal - system handles gracefully)

## 📝 Summary

### Minimum Setup (Just Push):
1. Push code to GitHub
2. Monitor Actions tab for first few runs
3. That's it!

### Recommended Setup (5 minutes):
1. Push code to GitHub
2. Run workflow manually once to test
3. Verify it works
4. Monitor for first week
5. Then just check weekly

## 🎯 Bottom Line

**After pushing to GitHub:**
- ✅ System runs automatically daily
- ✅ No ongoing maintenance needed
- ✅ Just monitor for the first week
- ✅ Then check weekly/monthly

**You don't need to:**
- ❌ Set up any databases
- ❌ Configure any API keys (for storage)
- ❌ Manually trigger runs (unless testing)
- ❌ Monitor daily (after first week)

**It's truly "set it and forget it"!** 🚀

