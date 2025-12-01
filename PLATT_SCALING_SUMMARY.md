# Platt Scaling (Sigmoid Calibration) Summary

**Date:** 2025-12-01 17:54:11


## Calibration Improvement Summary

### Before Calibration (Uncalibrated)
- Brier Score: 0.0917
- AUC: 0.8618

### After Platt Scaling (Calibrated)
- Brier Score: 0.0307
- AUC: 0.8618

### Improvement
- Brier Score Reduction: 0.0610 (66.5% improvement)
- AUC Change: 0.0000 (minimal change expected)

### Files Generated
- Calibrated Model: /Users/parkercase/DOC/models/random_forest_calibrated.pkl
- Calibration Plot: /Users/parkercase/DOC/calibration_comparison_platt.png

### Interpretation
- Lower Brier Score = Better Calibration ✓
- AUC should remain similar (discrimination preserved) ✓
- Calibrated probabilities are more reliable for clinical use ✓

### Next Steps
1. Update risk calculator to use calibrated model
2. Re-evaluate on test set with calibrated predictions
3. Compare clinical risk stratification before/after calibration
