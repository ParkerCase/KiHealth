# DOC Validator - Model Toggle Ready ✅

## Status

✅ **DOC Validator is running on port 3003**
✅ **Model toggle added to UI**
✅ **Both models available**

## Access

**URL:** http://localhost:3003

## How to Use the Model Toggle

1. Open http://localhost:3003 in your browser
2. Fill in patient information
3. **Check the box:** "Use Literature-Calibrated Model" (in the form)
4. Click "Analyze Patient"
5. Results will show which model was used

## Available Models

### Pure Data-Driven (Original) - Default
- **File:** `random_forest_best.pkl`
- **AUC:** 0.852
- **Brier Score:** 0.0808
- **Status:** PROBAST LOW RISK compliant

### Literature-Calibrated
- **Files:** 
  - `random_forest_literature_calibrated_base.pkl`
  - `random_forest_literature_calibrated_platt.pkl`
- **AUC:** 0.852 (unchanged)
- **Brier Score:** 0.0311 (61.5% improvement)
- **Status:** PROBAST LOW RISK compliant

## Technical Details

- Model selection is sent via `use_literature_calibration` form field
- Backend loads the appropriate model based on the checkbox
- Response includes `model_type` field showing which model was used
- Both models use the same 11 predictors
- Only calibration differs (Platt Scaling)

## Files Updated

1. `api/validate.py` - Model loading with toggle support
2. `public/index.html` - Added model selection checkbox
3. `public/static/js/main.js` - Added model selection to form data
4. `main.py` - Updated to run on port 3003

## Next Steps

The platform is ready to test! You can now:
- Compare both models side-by-side
- See which model gives better predictions
- Test the literature-calibrated model's improved calibration
