# KiHealth Presentation Readiness Checklist

**Last updated:** Pre-demo verification

---

## Data & Pipeline

| Item | Status | Notes |
|------|--------|-------|
| Unified dataset with C-peptide | ✅ | 38,509 rows; 9,501 with C-peptide (NHANES 1999-2004) |
| C-Pep NHANES integrated | ✅ | 99-00, 01-02, 03-04 cycles in `NIHANES/C-Pep/` |
| Transfer learning training | ✅ | 33,078 HOMA-eligible samples |
| KiHealth patient CSV | ✅ | `kihealth_patients.csv` (from TSV) |
| Predictions output | ✅ | `kihealth_predictions.csv` |

---

## Model Features

- **Core:** age, sex, BMI, glucose, insulin, HOMA-IR, HOMA-beta, HbA1c
- **KiHealth-style:** HBP, C-peptide, Ins/C-peptide ratio
- **Prediabetic tier:** A1c 5.7–6.4 (ADA)
- **KiHealth at-risk flags:** BMI≥30, HBP, A1c 5.7–6.4, Ins/Cpep out-of-range, % methylated

---

## Quick Run Commands

```bash
# 1. Convert TSV → CSV (if you add more patients)
python scripts/tsv_to_csv_kihealth.py

# 2. Regenerate unified dataset (if needed)
python -c "from src.data.load_kihealth import build_unified_kihealth; from pathlib import Path; build_unified_kihealth(save_path=Path('data/processed/unified_kihealth.csv'))"

# 3. Run predictions
python scripts/kihealth_diabetes_prediction.py
```

---

## Pre-Demo Verification

- [ ] Run `python scripts/kihealth_diabetes_prediction.py` — no errors
- [ ] Open `kihealth_predictions.csv` — columns: predicted_diabetes_label, risk_tier, kihealth_at_risk_flags
- [ ] Verify prediction counts: Diabetic, Prediabetic, Non-diabetic
- [ ] Have `kihealth_patients_raw.tsv` ready if you need to add patients

---

## File Locations

| File | Path |
|------|------|
| KiHealth patients (input) | `Diabetes-KiHealth/TL-KiHealth/kihealth_patients.csv` |
| Predictions (output) | `Diabetes-KiHealth/TL-KiHealth/kihealth_predictions.csv` |
| Raw TSV | `Diabetes-KiHealth/TL-KiHealth/kihealth_patients_raw.tsv` |
| Unified training data | `data/processed/unified_kihealth.csv` |
| C-Pep NHANES | `Diabetes-KiHealth/TL-KiHealth/NIHANES/C-Pep/` |

---

## Optional: Configurable Ranges

When C-peptide reference ranges are available, update in `scripts/kihealth_diabetes_prediction.py`:

```python
INSULIN_CPEP_RATIO_MIN = 0.5   # adjust
INSULIN_CPEP_RATIO_MAX = 15.0  # adjust
```

---

## Known Limitations

- Patients without A1c, Insulin, or Glucose are excluded from predictions
- % methylated is shown in flags but no risk threshold applied yet
- C-Pep NHANES (1999-2004) has no HbA1c or BMI in the source files
