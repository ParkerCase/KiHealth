# Quick Start Guide - Literature Quality System

## What This System Does

This system is **specifically designed for the knee osteoarthritis (OA) model**. It:
- Searches PubMed for knee OA progression and TKR prediction articles
- Assesses articles with PROBAST (4-domain risk assessment)
- Stores articles in SQLite database
- **Only uses Low Risk PROBAST articles in the model** (maintains top 7% PROBAST compliance)

## Two Workflow Options

### Option 1: Quick Start (No ASReview) ⚡

**Best for**: Getting started quickly, testing the system

```bash
# Just run the workflow - it will process articles directly
python scripts/literature_quality_workflow.py
```

**What happens**:
1. Fetches 5000 articles from PubMed (knee OA related)
2. PROBAST assesses all articles
3. Stores in database
4. Marks Low Risk articles as usable

**Pros**: Fast, no setup needed  
**Cons**: All articles go through PROBAST (including lower-quality ones)

---

### Option 2: Best Results (With ASReview) 🎯 **RECOMMENDED**

**Best for**: Maximum quality, processing thousands of articles efficiently

**Step 1: Install ASReview** (one-time setup)
```bash
pip install asreview
```

**Step 2: Run workflow to export articles**
```bash
python scripts/literature_quality_workflow.py
```
This creates `data/asreview_export.csv` with all articles.

**Step 3: Screen with ASReview LAB**
```bash
asreview web
```

Then in the web interface:
1. Click "New Project"
2. Upload `data/asreview_export.csv`
3. Select "Title" and "Abstract" as text fields
4. Select "pmid" as identifier
5. Start screening - AI will prioritize most relevant articles
6. Label articles as Relevant (1) or Irrelevant (0)
7. Export results when done

**Step 4: Import ASReview results** (if you want to use them)
The workflow will automatically use ASReview-screened articles if available.

**Pros**: 
- AI prioritizes most relevant articles first
- Saves time (screen 1000s efficiently)
- Better quality filtering before PROBAST
- Only high-quality articles get PROBAST assessed

**Cons**: Requires ASReview installation (but it's free and optional)

---

## Recommended Workflow

**For best results, use Option 2**:

1. **First time**: Install ASReview
   ```bash
   pip install asreview
   ```

2. **Run workflow** (exports articles for ASReview)
   ```bash
   python scripts/literature_quality_workflow.py
   ```

3. **Screen with ASReview** (filters to high-quality articles)
   ```bash
   asreview web
   ```

4. **Re-run workflow** (processes ASReview-screened articles through PROBAST)

This gives you:
- ✅ AI-filtered high-quality articles
- ✅ PROBAST assessment on relevant articles only
- ✅ Maximum efficiency
- ✅ Best quality for the knee OA model

---

## What Gets Processed

The system searches PubMed for:
- **Knee osteoarthritis** progression studies
- **Total knee replacement (TKR)** prediction studies
- **Prognostic factors** for knee OA
- **Cohort studies**, **systematic reviews**, **longitudinal studies**

All articles are assessed with PROBAST across 4 domains:
1. **Participants** (Selection bias)
2. **Predictors** (Measurement bias)
3. **Outcome** (Measurement bias)
4. **Analysis** (Statistical bias)

Only articles with **Low Risk** on all 4 domains (or 3 Low + 1 Moderate with justification) are used in the knee OA model.

---

## Monitoring

Check system status:
```bash
python monitor_system.py
```

This shows:
- Total articles in database
- Low Risk PROBAST count
- Articles usable for model
- Quality metrics

---

## Summary

**Yes, this is for the knee osteoarthritis model!**

**Should you run ASReview first?**
- **Recommended**: Yes, for best quality and efficiency
- **Optional**: No, workflow works without it (just processes more articles)

**Quick start**: Just run `python scripts/literature_quality_workflow.py`  
**Best results**: Install ASReview first, then run workflow
