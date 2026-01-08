# ASReview LAB - Frequently Asked Questions

## How Long Will It Take?

### Time Estimates for Screening 4,671 Articles

**With ASReview AI Prioritization:**
- **First 50-100 articles**: ~30-60 minutes (manual review to train AI)
- **Remaining articles**: Much faster (AI shows most relevant first)
- **Total time**: ~2-4 hours for full screening (vs. weeks manually)

**Without ASReview:**
- Would take **weeks** to manually review 4,671 articles

**Recommendation**: 
- Screen **200-500 articles** initially (1-2 hours)
- Export results
- Review more later if needed

## Will It Only Look at Open Source Articles?

**No!** ASReview will screen **ALL 4,671 articles** including:
- ✅ **2,483 Open Access** articles (53.2%)
- ✅ **2,188 Paywalled** articles (46.8%)

**Why this is good:**
- You can identify **paywalled articles worth exploring** during screening
- Mark them as "Relevant" even if you can't access full text yet
- Later, you can upload PDFs via the Review Dashboard

## Will It Flag Paywalled Articles Worth Exploring?

**Yes!** Here's how:

### During ASReview Screening:
1. **All articles shown** (open access + paywalled)
2. **You can see**:
   - Title
   - Abstract
   - Authors, Journal, DOI
   - **Access type** (if you add it to the export)

3. **When you see a paywalled article that's relevant:**
   - Mark it as **✅ Relevant**
   - Note the PMID
   - Later upload the PDF via Review Dashboard

### After Screening:
- Export results will show which paywalled articles you marked as relevant
- You can prioritize these for PDF upload
- Upload them via Review Dashboard for PROBAST assessment

## How to Add Access Type to ASReview Export

The current export includes all articles. To see access type in ASReview:

1. **Option 1**: Add access_type column to export (we can update the export)
2. **Option 2**: Check in database after screening
3. **Option 3**: Use Review Dashboard to see paywalled articles

## Recommended Workflow

### Step 1: Screen with ASReview (2-4 hours)
```bash
# Start ASReview (see correct command below)
asreview lab
```

Screen articles:
- Mark **Relevant**: Knee OA prediction/progression articles
- Mark **Irrelevant**: Not related to your model
- **Note paywalled articles** that are relevant

### Step 2: Export Results
- Export from ASReview
- Save as CSV

### Step 3: Upload Paywalled PDFs
- Go to Review Dashboard
- Upload PDFs for paywalled articles you marked as relevant
- System will assess with PROBAST

### Step 4: Manual PROBAST Review
- Review Moderate Risk articles from relevant set
- Add justification for Low Risk
- Build Low Risk database

## Time Investment Summary

| Task | Time | Benefit |
|------|------|---------|
| ASReview screening (200-500 articles) | 1-2 hours | Identifies relevant articles |
| Full screening (all 4,671) | 2-4 hours | Complete dataset |
| Upload paywalled PDFs | 30 min - 1 hour | Access high-value articles |
| Manual PROBAST review | 2-4 hours | Build Low Risk database |
| **Total** | **5-11 hours** | **Complete literature base** |

## What You'll Get

After ASReview + manual review:
- **~500-1,000 relevant articles** (from 4,671)
- **~200-400 Low Risk PROBAST** articles
- **List of paywalled articles** worth exploring
- **Strong literature base** for knee OA model

---

**Bottom Line**: ASReview screens ALL articles (open + paywalled), helps you identify relevant ones efficiently, and flags paywalled articles worth exploring!
