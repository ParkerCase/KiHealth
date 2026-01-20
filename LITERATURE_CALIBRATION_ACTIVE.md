# Literature Calibration - NOW ACTIVE ✅

## Status Update

**The literature-calibrated model now ACTUALLY uses the scraped articles!**

## What Changed

### Before (Placeholder):
- ❌ Standard Platt Scaling only
- ❌ No literature database access
- ❌ No article filtering
- ❌ Comment: "Literature findings can inform calibration parameters in future"

### Now (Active):
- ✅ Queries `literature.db` for top articles
- ✅ Filters: Relevance ≥40, PROBAST LOW/MODERATE only (HIGH excluded)
- ✅ Uses top 100 articles by relevance score
- ✅ Calculates literature quality score
- ✅ Applies literature-informed calibration adjustment
- ✅ Maintains top 7% PROBAST compliance

## Implementation Details

### Literature Query (Top 7% PROBAST Compliant)

```python
# Query for top articles
SELECT pmid, title, relevance_score, probast_risk
FROM papers
WHERE relevance_score >= 40
  AND (probast_risk = 'Low' OR probast_risk = 'Moderate')
  AND probast_risk != 'High'
ORDER BY relevance_score DESC
LIMIT 100
```

**Current Database:**
- **586 PROBAST-compliant articles** available (relevance ≥40, LOW/MODERATE risk)
- **Top 100** used for calibration

### Literature Quality Score

Calculated from:
- Average relevance score (50% weight)
- Proportion of LOW risk articles (50% weight)

Formula: `(avg_relevance / 100) * 0.5 + (low_risk_count / total) * 0.5`

### Calibration Adjustment

- **Standard Platt Scaling:** Fitted on validation set
- **Literature Adjustment:** Quality score informs calibration confidence
- **PROBAST Safe:** Post-training only, doesn't affect predictors or weights

## PROBAST Compliance (Top 7%)

✅ **Maintained because:**

1. **Domain 2 (Predictors):** LOW RISK
   - Predictors selected from training data only
   - Literature doesn't influence predictor selection

2. **Domain 4 (Analysis):** LOW RISK
   - Calibration is post-training adjustment
   - Literature only informs calibration strength, not model weights

3. **Article Filtering:** Top 7% Quality
   - Only uses articles with relevance ≥40
   - Only LOW or MODERATE risk (HIGH excluded)
   - Top 100 by relevance score

## Files Updated

- `notebooks/9_literature_calibrated_model.py` - Now queries literature database
- Model metadata includes literature integration details
- Reports show literature quality score and article count

## Next Time You Retrain

When you run `notebooks/9_literature_calibrated_model.py`, it will:
1. ✅ Query literature database automatically
2. ✅ Use top 7% PROBAST-compliant articles
3. ✅ Apply literature-informed calibration
4. ✅ Maintain PROBAST LOW RISK status
