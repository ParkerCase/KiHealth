# Walking Distance Implementation Plan

**Date:** 2025-01-23  
**Status:** In Progress

---

## Implementation Steps

### ✅ Step 1: Data Preparation Script
- [x] Add `V00400MTIM` to `womac_vars` list in `notebooks/3_data_preparation.py`
- [ ] Run data preparation script to verify variable exists
- [ ] Check data completeness (should be ~95.2%)

### Step 2: Preprocessing
- [ ] Add walking distance handling in `DOC_Validator_Vercel/preprocessing.py`
- [ ] Make it optional (can be missing)
- [ ] Add to imputation pipeline
- [ ] Add to feature engineering if needed

### Step 3: Model Retraining
- [ ] Retrain model with walking distance included
- [ ] Verify EPV = 15.55 ≥15
- [ ] Check model performance (AUC, calibration)
- [ ] Save new model files

### Step 4: Frontend Updates
- [ ] Add walking distance input field to form
- [ ] Make it optional
- [ ] Add validation (reasonable range)
- [ ] Update form submission

### Step 5: API Updates
- [ ] Update validation to accept walking distance
- [ ] Update preprocessing call
- [ ] Test API endpoint

### Step 6: Documentation
- [ ] Update PROBAST compliance report
- [ ] Update data dictionary
- [ ] Update EPV calculation
- [ ] Update predictor selection rationale

---

## Variable Details

**OAI Variable:** `V00400MTIM`
- **Description:** Time (seconds) to walk 400 meters
- **Type:** Continuous
- **Range:** Typically 200-600 seconds (3-10 minutes)
- **Missing:** ~4.8% (231/4,796 patients)
- **Clinical Name:** "Walking Distance" or "400m Walk Time"

---

## Notes

- Walking distance is **optional** - model should work without it
- Missing values will be imputed using MICE (same as other variables)
- EPV will drop from 17.10 to 15.55 (still compliant ≥15)
- Frontend should allow users to skip this field


