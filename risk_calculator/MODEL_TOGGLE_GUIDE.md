# Model Toggle Guide - Testing Literature-Calibrated Model

## Platform Running on Port 3003

✅ **Server is running at:** http://localhost:3003

## How to Test the Literature-Calibrated Model

### Option 1: Use the UI Toggle (Easiest)

1. Open http://localhost:3003 in your browser
2. Fill in the patient information
3. **Check the box:** "Use Literature-Calibrated Model"
4. Click "Calculate Risk"
5. The results will show which model was used

### Option 2: Use Environment Variable

Start the server with the calibrated model by default:

```bash
cd /Users/parkercase/DOC/risk_calculator
USE_LITERATURE_CALIBRATION=true python app.py
```

### Option 3: Use the API Directly

Send a POST request to `/calculate` with `use_literature_calibration: true`:

```bash
curl -X POST http://localhost:3003/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "age": 65,
    "sex": "Female",
    "bmi": 28,
    "womac_right": 45,
    "womac_left": 50,
    "kl_right": 3,
    "kl_left": 3,
    "family_history": "No",
    "use_literature_calibration": true
  }'
```

## Model Comparison

### Pure Data-Driven (Original)
- **AUC:** 0.852
- **Brier Score:** 0.0808
- **Status:** PROBAST LOW RISK compliant
- **Use case:** Standard predictions

### Literature-Calibrated
- **AUC:** 0.852 (unchanged - discrimination same)
- **Brier Score:** 0.0311 (61.5% improvement - better calibration)
- **Status:** PROBAST LOW RISK compliant
- **Use case:** More accurate probability estimates

## API Endpoints

- **GET /** - Main calculator page
- **POST /calculate** - Calculate risk (supports `use_literature_calibration` parameter)
- **GET /model/info** - Get information about available models

## Notes

- Both models use the same 11 predictors
- Literature calibration improves probability accuracy (Brier score)
- AUC remains the same (discrimination unchanged)
- You can switch between models instantly via the toggle
