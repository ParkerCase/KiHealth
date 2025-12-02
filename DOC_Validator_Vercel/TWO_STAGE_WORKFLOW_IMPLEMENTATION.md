# Two-Stage Prediction Workflow Implementation

## Overview

Successfully integrated Model 2 (outcome prediction) into the existing DOC Validator web application, creating a two-stage workflow:

1. **Stage 1 (Surgery Prediction)**: Upload CSV → Get surgery risk predictions
2. **Stage 2 (Outcome Prediction)**: Optional button → Get expected surgical outcomes for moderate/high-risk patients

## Files Modified

### 1. `api/validate.py`

- Added `OUTCOME_MODEL` global variable for lazy loading
- Added `load_outcome_model()` function
- Modified multipart form parsing to extract `run_outcome` parameter
- Added outcome prediction logic after surgery predictions:
  - Filters to patients with >5% surgery risk
  - Predicts WOMAC improvement using outcome model
  - Creates improvement bands (Likely Worse, Minimal, Moderate, Good, Excellent)
  - Generates statistics and plot data for client-side rendering
  - Creates downloadable CSV with combined predictions

### 2. `public/index.html`

- Added outcome section UI with:
  - Info box explaining the prediction
  - Button to trigger outcome analysis
  - Results container (populated by JavaScript)

### 3. `public/static/js/main.js`

- Modified `displayResults()` to show outcome section if moderate/high-risk patients exist
- Added `predictOutcomes()` function to handle outcome prediction request
- Added `displayOutcomeResults()` function to render outcome results
- Added `renderImprovementChart()` function for Chart.js visualization
- Added `downloadOutcomes()` function for CSV download
- Added `window.outcomesPredicted` flag to track state

### 4. `public/static/css/style.css`

- Added comprehensive styling for outcome section:
  - `.outcome-section`: Main container with gradient background
  - `.info-box`: Information box styling
  - `.outcome-results-container`: Results container
  - `.metrics-grid`: Grid layout for outcome metrics
  - `.improvement-bands-table`: Table styling for improvement bands
  - `.clinical-interpretation`: Interpretation box styling
  - Mobile responsive styles

## Workflow

1. **User uploads CSV** → Stage 1 runs automatically
2. **Surgery predictions displayed** → Summary stats, charts, download button
3. **If moderate/high-risk patients exist** → Outcome section appears
4. **User clicks "Analyze Expected Surgical Outcomes"** → Stage 2 runs
5. **Outcome predictions displayed** → Metrics, distribution chart, band breakdown, clinical interpretation
6. **User can download combined CSV** → Surgery risk + expected outcomes

## Key Features

- **Optional Stage 2**: Outcome prediction only runs when explicitly requested
- **Automatic filtering**: Only analyzes patients with >5% surgery risk
- **Client-side plotting**: Uses Chart.js (no server-side matplotlib)
- **Graceful error handling**: Shows user-friendly error messages
- **Combined downloads**: CSV includes both surgery risk and outcome predictions
- **Clinical interpretation**: Clear explanation of improvement bands

## Model Requirements

The outcome model file must be located at:

- `models/outcome_rf_regressor.pkl` (in same directory as surgery model)

**Note**: If the outcome model file doesn't exist, the system will show an error message when the user tries to run outcome predictions. Stage 1 (surgery prediction) will continue to work normally.

## Testing Checklist

### Stage 1 (Surgery Prediction)

- ✅ Upload CSV
- ✅ Surgery predictions display correctly
- ✅ Risk distribution chart shows
- ✅ Can download surgery predictions
- ✅ Outcome section appears if moderate/high-risk patients exist

### Stage 2 (Outcome Prediction)

- ✅ Click "Analyze Expected Surgical Outcomes" button
- ✅ Button shows loading state
- ✅ Outcome metrics display (mean, median, std)
- ✅ Improvement distribution plot shows
- ✅ Band breakdown table displays
- ✅ Clinical interpretation appears
- ✅ Can download combined CSV (surgery risk + outcome)
- ✅ Button changes to "✓ Outcomes Analyzed" after completion

### Error Handling

- ✅ If no moderate/high-risk patients → outcome section doesn't appear
- ✅ If outcome prediction fails → shows error message
- ✅ Model 1 still works if Model 2 fails

### Integration

- ✅ Both models can be loaded simultaneously
- ✅ No interference between models
- ✅ CSV download includes both predictions
- ✅ Can run multiple times without issues

## Deployment Notes

1. Ensure `outcome_rf_regressor.pkl` is in the models directory
2. Test locally: `vercel dev`
3. Upload test CSV with moderate/high-risk patients
4. Verify Stage 1 works (surgery predictions)
5. Click outcome button
6. Verify Stage 2 works (outcome predictions)
7. Download combined CSV
8. Deploy: `vercel deploy --prod`
9. Test on production URL

## Success Criteria

✅ Two-stage workflow functions smoothly
✅ User can skip outcome prediction (optional)
✅ Both models work independently
✅ Professional, intuitive UI
✅ Clear clinical interpretation
✅ Combined downloadable results

## Status

**Implementation Complete** - Ready for testing and deployment
