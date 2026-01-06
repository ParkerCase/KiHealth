# Walking Distance Implementation Status

**Date:** 2025-01-23  
**Status:** ✅ Code Updates Complete - Model Retraining Required

---

## ✅ Completed Steps

### 1. Data Preparation Script ✅
- **File:** `notebooks/3_data_preparation.py`
- **Change:** Added `V00400MTIM` to `womac_vars` list
- **Status:** ✅ Code updated

### 2. Preprocessing ✅
- **File:** `DOC_Validator_Vercel/preprocessing.py`
- **Changes:**
  - Added walking distance handling (optional field)
  - Added to continuous variables list
  - Added validation (60-1200 seconds range)
  - Will be imputed if missing
- **Status:** ✅ Code updated

---

## ⏳ Next Steps (Require Execution)

### 3. Run Data Preparation Script
**Command:**
```bash
cd /Users/parkercase/DOC
python notebooks/3_data_preparation.py
```

**Expected Results:**
- Verify `V00400MTIM` exists in AllClinical00
- Check data completeness (~95.2%)
- Updated `data/baseline_modeling.csv` with walking distance
- Updated EPV calculation (should show 11 predictors, EPV = 15.55)

### 4. Retrain Model
**Command:**
```bash
# This will need to be run after data preparation
# Check for model training script location
```

**Expected Results:**
- New model trained with 11 predictors (including walking distance)
- EPV = 15.55 ≥15 ✅
- Model performance metrics (AUC, calibration)
- Updated model files saved

### 5. Frontend Updates
**File:** `DOC_Validator_Vercel/public/index.html`
**File:** `DOC_Validator_Vercel/public/static/js/main.js`

**Changes Needed:**
- Add "Walking Distance (400m walk time)" input field
- Make it optional
- Add validation (60-1200 seconds)
- Update form submission to include walking_distance

### 6. API Updates
**File:** `DOC_Validator_Vercel/api/validate.py`

**Changes Needed:**
- Accept `walking_distance` in form data
- Pass to preprocessing function
- Handle optional field

### 7. Documentation Updates
- Update PROBAST compliance report
- Update data dictionary
- Update EPV calculation document
- Update predictor selection rationale

---

## Variable Details

**OAI Variable:** `V00400MTIM`
- **Description:** Time (seconds) to walk 400 meters
- **Type:** Continuous
- **Range:** 60-1200 seconds (1-20 minutes)
- **Missing:** ~4.8% (will be imputed)
- **Clinical Name:** "Walking Distance" or "400m Walk Time"
- **Units:** Seconds

---

## EPV Compliance

**Current:** EPV = 17.10 (10 predictors, 171 events)  
**With Walking Distance:** EPV = 15.55 (11 predictors, 171 events)  
**Status:** ✅ Still compliant (≥15 required)

---

## Notes

- Walking distance is **optional** - model works without it
- Missing values handled via MICE imputation
- Frontend should allow users to skip this field
- Validation range: 60-1200 seconds (reasonable for 400m walk)

---

## Testing Checklist

- [ ] Verify V00400MTIM exists in AllClinical00
- [ ] Run data preparation script
- [ ] Verify EPV = 15.55
- [ ] Retrain model
- [ ] Test model performance
- [ ] Update frontend
- [ ] Test API endpoint
- [ ] Update documentation


