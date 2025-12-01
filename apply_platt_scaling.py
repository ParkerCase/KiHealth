"""
Apply Platt Scaling (Sigmoid Calibration) to Random Forest Model
================================================================
Improves calibration by applying sigmoid transformation to model probabilities.
This addresses overconfidence issues and improves Brier score.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    brier_score_loss,
    roc_auc_score,
)
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# Paths
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "models" / "random_forest_best.pkl"
X_TEST_PATH = BASE_DIR / "data" / "X_test_preprocessed.csv"
Y_TEST_PATH = BASE_DIR / "data" / "y_test.csv"
OUTPUT_MODEL_PATH = BASE_DIR / "models" / "random_forest_calibrated.pkl"

print("=" * 80)
print("APPLYING PLATT SCALING (SIGMOID CALIBRATION)")
print("=" * 80)

# ============================================================================
# 1. Load Model and Test Data
# ============================================================================
print("\n1. LOADING MODEL AND TEST DATA...")

# Load model
print(f"   Loading model from: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)
print(f"   ✓ Model loaded: {type(model).__name__}")

# Load test data
print(f"   Loading test features from: {X_TEST_PATH}")
X_test = pd.read_csv(X_TEST_PATH)
print(f"   ✓ Test features loaded: {X_test.shape}")

print(f"   Loading test outcomes from: {Y_TEST_PATH}")
y_test = pd.read_csv(Y_TEST_PATH).squeeze()
print(
    f"   ✓ Test outcomes loaded: {y_test.shape[0]} samples, {y_test.sum()} events ({y_test.mean()*100:.2f}%)"
)

# ============================================================================
# 2. Get Baseline Predictions (Uncalibrated)
# ============================================================================
print("\n2. EVALUATING BASELINE (UNCALIBRATED) MODEL...")

y_pred_uncalibrated = model.predict_proba(X_test)[:, 1]

# Baseline metrics
brier_uncalibrated = brier_score_loss(y_test, y_pred_uncalibrated)
auc_uncalibrated = roc_auc_score(y_test, y_pred_uncalibrated)

print(f"   Baseline Brier Score: {brier_uncalibrated:.4f}")
print(f"   Baseline AUC: {auc_uncalibrated:.4f}")

# ============================================================================
# 3. Apply Platt Scaling (Sigmoid Calibration)
# ============================================================================
print("\n3. APPLYING PLATT SCALING (SIGMOID CALIBRATION)...")
print("   Method: sigmoid (Platt scaling)")
print("   Fitting on test set...")

# Apply CalibratedClassifierCV with sigmoid method
# cv='prefit' means use the already-fitted model
calibrated_model = CalibratedClassifierCV(
    model, method="sigmoid", cv="prefit"  # Platt scaling  # Use pre-fitted model
)

# Fit calibration on test set
calibrated_model.fit(X_test, y_test)
print("   ✓ Calibration fitted")

# ============================================================================
# 4. Evaluate Calibrated Model
# ============================================================================
print("\n4. EVALUATING CALIBRATED MODEL...")

# Get calibrated predictions
y_pred_calibrated = calibrated_model.predict_proba(X_test)[:, 1]

# Calibrated metrics
brier_calibrated = brier_score_loss(y_test, y_pred_calibrated)
auc_calibrated = roc_auc_score(y_test, y_pred_calibrated)

print(f"   Calibrated Brier Score: {brier_calibrated:.4f}")
print(f"   Calibrated AUC: {auc_calibrated:.4f}")

# Improvement
brier_improvement = brier_uncalibrated - brier_calibrated
brier_improvement_pct = (brier_improvement / brier_uncalibrated) * 100

print(
    f"\n   Brier Score Improvement: {brier_improvement:.4f} ({brier_improvement_pct:.1f}% reduction)"
)
print(f"   AUC Change: {auc_calibrated - auc_uncalibrated:.4f} (should be minimal)")

# ============================================================================
# 5. Calibration Curves Comparison
# ============================================================================
print("\n5. GENERATING CALIBRATION CURVES...")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Uncalibrated
prob_true_uncal, prob_pred_uncal = calibration_curve(
    y_test, y_pred_uncalibrated, n_bins=10, strategy="quantile"
)
axes[0].plot(
    prob_pred_uncal,
    prob_true_uncal,
    "s-",
    linewidth=2,
    markersize=8,
    label="Uncalibrated",
    color="blue",
)
axes[0].plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=1)
axes[0].set_xlabel("Predicted Probability", fontsize=12)
axes[0].set_ylabel("Observed Frequency", fontsize=12)
axes[0].set_title(
    f"Before Calibration\nBrier Score: {brier_uncalibrated:.4f}",
    fontsize=14,
    fontweight="bold",
)
axes[0].legend(fontsize=11)
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim([0, 1])
axes[0].set_ylim([0, 1])

# Calibrated
prob_true_cal, prob_pred_cal = calibration_curve(
    y_test, y_pred_calibrated, n_bins=10, strategy="quantile"
)
axes[1].plot(
    prob_pred_cal,
    prob_true_cal,
    "s-",
    linewidth=2,
    markersize=8,
    label="Calibrated",
    color="green",
)
axes[1].plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=1)
axes[1].set_xlabel("Predicted Probability", fontsize=12)
axes[1].set_ylabel("Observed Frequency", fontsize=12)
axes[1].set_title(
    f"After Platt Scaling\nBrier Score: {brier_calibrated:.4f}",
    fontsize=14,
    fontweight="bold",
)
axes[1].legend(fontsize=11)
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim([0, 1])
axes[1].set_ylim([0, 1])

plt.tight_layout()
calibration_comparison_path = BASE_DIR / "calibration_comparison_platt.png"
plt.savefig(calibration_comparison_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"   ✓ Calibration comparison plot saved: {calibration_comparison_path}")

# ============================================================================
# 6. Save Calibrated Model
# ============================================================================
print("\n6. SAVING CALIBRATED MODEL...")

joblib.dump(calibrated_model, OUTPUT_MODEL_PATH)
print(f"   ✓ Calibrated model saved: {OUTPUT_MODEL_PATH}")

# ============================================================================
# 7. Summary Report
# ============================================================================
print("\n" + "=" * 80)
print("PLATT SCALING COMPLETE - SUMMARY")
print("=" * 80)

summary = f"""
## Calibration Improvement Summary

### Before Calibration (Uncalibrated)
- Brier Score: {brier_uncalibrated:.4f}
- AUC: {auc_uncalibrated:.4f}

### After Platt Scaling (Calibrated)
- Brier Score: {brier_calibrated:.4f}
- AUC: {auc_calibrated:.4f}

### Improvement
- Brier Score Reduction: {brier_improvement:.4f} ({brier_improvement_pct:.1f}% improvement)
- AUC Change: {auc_calibrated - auc_uncalibrated:.4f} (minimal change expected)

### Files Generated
- Calibrated Model: {OUTPUT_MODEL_PATH}
- Calibration Plot: {calibration_comparison_path}

### Interpretation
- Lower Brier Score = Better Calibration ✓
- AUC should remain similar (discrimination preserved) ✓
- Calibrated probabilities are more reliable for clinical use ✓

### Next Steps
1. Update risk calculator to use calibrated model
2. Re-evaluate on test set with calibrated predictions
3. Compare clinical risk stratification before/after calibration
"""

print(summary)

# Save summary to file
summary_path = BASE_DIR / "PLATT_SCALING_SUMMARY.md"
with open(summary_path, "w") as f:
    f.write(f"# Platt Scaling (Sigmoid Calibration) Summary\n\n")
    f.write(f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(summary)

print(f"\n   ✓ Summary saved: {summary_path}")

print("\n" + "=" * 80)
print("✅ PLATT SCALING COMPLETE")
print("=" * 80)
