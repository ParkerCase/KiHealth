# Platt Scaling (Sigmoid Calibration) Summary

**Date:** 2026-01-05 11:53:58


## Calibration Improvement Summary

### Before Calibration (Uncalibrated)
- Brier Score: 0.0808
- AUC: 0.8517

### After Platt Scaling (Calibrated)
- Brier Score: 0.0311
- AUC: 0.8517

### Improvement
- Brier Score Reduction: 0.0497 (61.5% improvement)
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
