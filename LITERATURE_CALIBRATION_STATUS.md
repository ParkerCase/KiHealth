# Literature Calibration Status

## Current Implementation

**The literature-calibrated model currently does NOT directly use the scraped articles.**

### How It Currently Works:

1. **Base Model**: Uses the same Random Forest model as the original (pure data-driven)
2. **Calibration Method**: Standard Platt Scaling (sigmoid calibration)
3. **Calibration Data**: Fitted on validation set (20% of training data)
4. **Literature Integration**: **NOT YET IMPLEMENTED** - placeholder for future enhancement

### Code Evidence:

From `notebooks/9_literature_calibrated_model.py` (line 99-102):
```python
print("   Note: Literature findings can inform calibration parameters in future")
```

The calibration is currently:
- **Standard Platt Scaling**: Fits logistic regression to map uncalibrated probabilities to calibrated ones
- **No literature database access**: Does not query `literature.db`
- **No relevance score filtering**: Does not use PROBAST-filtered articles
- **No article-based parameters**: Calibration parameters come purely from validation set

## Future Enhancement (Not Yet Implemented)

The system is designed to support literature-informed calibration, but this feature is **not yet active**. When implemented, it would:

1. Query `literature.db` for top articles (relevance ≥40, PROBAST LOW/MODERATE)
2. Extract calibration insights from those articles
3. Inform Platt Scaling parameters based on literature findings
4. Maintain PROBAST compliance

## Current Model Performance

- **AUC**: 0.852 (same as original - calibration doesn't change discrimination)
- **Brier Score**: 0.0311 (improved from 0.0808 - 61.5% improvement)
- **Calibration Method**: Standard Platt Scaling (not literature-informed)

## Summary

**Answer to your question**: No, the top results from the scraping run are **NOT currently influencing the calibrated model**. The calibrated model uses standard Platt Scaling fitted on validation data, not literature findings. The literature integration is a planned future enhancement.
