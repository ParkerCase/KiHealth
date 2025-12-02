# Matplotlib Removal - Size Optimization

## Problem
Vercel serverless functions have a 250 MB unzipped size limit. The function exceeded this due to large Python dependencies, particularly matplotlib (~50-100 MB).

## Solution
Removed matplotlib and moved all plotting to client-side using Chart.js.

## Changes Made

### Backend (`api/validate.py`)
- ✅ Removed `matplotlib` and `matplotlib.pyplot` imports
- ✅ Removed `plot_to_base64()` function
- ✅ Replaced all plot generation with data structures:
  - Risk distribution: JSON with labels and values
  - ROC curve: JSON with x/y coordinates for model and random lines
  - Calibration plot: JSON with x/y coordinates for model and perfect calibration lines

### Frontend (`static/js/main.js`)
- ✅ Added `renderCharts()` function using Chart.js
- ✅ Updated `displayResults()` to create canvas elements instead of img tags
- ✅ Implemented three chart types:
  - Bar chart for risk distribution
  - Line chart for ROC curve
  - Scatter chart for calibration plot

### HTML (`public/index.html`)
- ✅ Added Chart.js CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`

### Dependencies (`requirements.txt`)
- ✅ Removed `matplotlib>=3.7.2`

## Benefits

1. **Size Reduction**: ~50-100 MB saved (matplotlib + dependencies)
2. **No Functionality Lost**: All plots still rendered, just client-side
3. **Better Performance**: Charts render faster in browser
4. **Interactive Charts**: Chart.js provides hover tooltips and interactivity
5. **No Upgrade Needed**: Works within Hobby plan limits

## Estimated Bundle Size (After Optimization)

- pandas: ~50 MB
- numpy: ~30 MB
- scikit-learn: ~40 MB
- joblib: ~5 MB
- Models: ~1.1 MB
- Code: < 1 MB
- **Total: ~127 MB** ✅ (well under 250 MB limit)

## Testing

After deployment, verify:
1. Risk distribution bar chart renders correctly
2. ROC curve displays with model and random lines
3. Calibration plot shows model vs perfect calibration
4. All charts are interactive (hover for values)

