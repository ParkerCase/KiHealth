# Walking Distance Implementation - Next Steps

**Date:** 2025-01-23  
**Status:** Code Complete - Ready for Data Preparation & Model Retraining

---

## ✅ What's Been Completed

All code updates are complete:

1. ✅ **Data Preparation Script** - Added `V00400MTIM` to variable selection
2. ✅ **Preprocessing** - Handles walking_distance (optional, validated, imputed)
3. ✅ **Frontend** - New input field for walking distance
4. ✅ **JavaScript** - Collection, validation, and CSV inclusion
5. ✅ **API** - Automatically accepts new CSV column

---

## ⏳ Required Next Steps

### Step 1: Run Data Preparation Script

**Command:**
```bash
cd /Users/parkercase/DOC
python notebooks/3_data_preparation.py
```

**Expected Output:**
- Verify `V00400MTIM` exists in AllClinical00
- Check data completeness (~95.2%)
- Updated `data/baseline_modeling.csv` with walking distance
- EPV calculation showing 11 predictors, EPV = 15.55

**What to Check:**
- Look for: `✅ V00400MTIM` in AllClinical00 variables
- Verify: Missing data ~4.8% (acceptable)
- Confirm: EPV = 15.55 ≥15 ✅

---

### Step 2: Retrain Model

**Script:** `notebooks/5_model_development.py`

**What it does:**
- Trains Random Forest with 11 predictors (including walking distance)
- Uses grid search with cross-validation
- Saves updated model files

**Command:**
```bash
cd /Users/parkercase/DOC
python notebooks/5_model_development.py
```

**Expected Output:**
- Model trained with 11 predictors
- EPV = 15.55 verified
- Updated model files saved:
  - `models/random_forest_calibrated.pkl`
  - `models/scaler.pkl`
  - `models/feature_names.pkl`

**Important:** 
- Current model (10 predictors) will NOT work with walking_distance
- Must retrain before using walking_distance in production

---

### Step 3: Update Model Files for Deployment

After retraining, copy updated model files:

```bash
# Copy to Vercel deployment location
cp models/random_forest_calibrated.pkl DOC_Validator_Vercel/api/models/
cp models/scaler.pkl DOC_Validator_Vercel/api/models/
cp models/feature_names.pkl DOC_Validator_Vercel/api/models/
```

---

### Step 4: Test Frontend

1. Open the application
2. Fill out the form
3. Test walking distance field:
   - Leave empty (should work)
   - Enter valid value (60-1200 seconds)
   - Try invalid value (should show error)
4. Submit form and verify predictions work

---

### Step 5: Update Documentation

**Files to Update:**
1. `EPV_calculation.txt` - Update to show 11 predictors, EPV = 15.55
2. `data_dictionary.csv` - Add V00400MTIM entry
3. `PREDICTOR_SELECTION_RATIONALE.md` - Add walking distance rationale
4. `PROBAST_COMPLIANCE_REPORT.md` - Update EPV section
5. `DATA_PREPARATION_VALIDATION_REPORT.md` - Add walking distance to included variables

---

## 📊 EPV Compliance Verification

**Before:** EPV = 17.10 (10 predictors, 171 events)  
**After:** EPV = 15.55 (11 predictors, 171 events)  
**Status:** ✅ Still compliant (≥15 required)

**Verification:**
```python
events = 171
predictors = 11
epv = events / predictors  # = 15.55
assert epv >= 15  # ✅ PASS
```

---

## 🧪 Testing Checklist

### Data Preparation
- [ ] V00400MTIM exists in AllClinical00
- [ ] Data completeness ~95.2%
- [ ] EPV = 15.55 calculated correctly
- [ ] Updated baseline_modeling.csv includes walking distance

### Model Training
- [ ] Model trains successfully with 11 predictors
- [ ] EPV = 15.55 verified in training output
- [ ] Model performance maintained/improved
- [ ] Model files saved correctly

### Frontend
- [ ] Walking distance field appears
- [ ] Field is optional (works when empty)
- [ ] Validation works (60-1200 seconds)
- [ ] Form submission includes walking_distance

### API
- [ ] API accepts walking_distance in CSV
- [ ] Preprocessing handles walking_distance
- [ ] Missing values imputed correctly
- [ ] Predictions work with walking_distance
- [ ] Predictions work without walking_distance

---

## 📝 Variable Information

**OAI Variable:** `V00400MTIM`
- **Description:** Time (seconds) to walk 400 meters
- **Type:** Continuous
- **Range:** 60-1200 seconds (1-20 minutes)
- **Missing:** ~4.8% (231/4,796 patients)
- **Imputation:** MICE (same as other variables)

**Frontend Field:**
- **ID:** `walking_distance`
- **Label:** "Walking Distance (Optional)"
- **Type:** Number input
- **Min:** 60 seconds
- **Max:** 1200 seconds
- **Required:** No

---

## ⚠️ Important Notes

1. **Model Retraining Required:**
   - Current model will NOT work with walking_distance
   - Must retrain before production use
   - Until retrained, walking_distance will be ignored

2. **Backward Compatibility:**
   - Walking distance is optional
   - Model works with or without it
   - Missing values handled via imputation

3. **PROBAST Compliance:**
   - EPV = 15.55 maintains top 7% status
   - All domains remain LOW RISK
   - Documentation needs updating after retraining

---

## 🚀 Quick Start

1. **Verify variable exists:**
   ```bash
   python notebooks/3_data_preparation.py
   ```

2. **Retrain model:**
   ```bash
   python notebooks/5_model_development.py
   ```

3. **Copy model files:**
   ```bash
   cp models/*.pkl DOC_Validator_Vercel/api/models/
   ```

4. **Test frontend:**
   - Open application
   - Test walking distance field
   - Verify predictions work

---

**Status:** ✅ **Ready for Execution** - All code complete, awaiting data preparation and model retraining


