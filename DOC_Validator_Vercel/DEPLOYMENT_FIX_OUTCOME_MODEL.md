# Fix for Outcome Model Not Found Error

## Issue
Error: `Outcome model file not found at: /var/task/api/models/outcome_rf_regressor.pkl`

## Root Cause
The outcome model file exists locally but may not be included in Vercel's deployment bundle, or the path resolution isn't finding it correctly.

## Solution Applied

### 1. Updated `vercel.json`
- Changed `includeFiles` to explicitly include `api/models/**`
- This ensures all model files in `api/models/` are included in the deployment

### 2. Improved Path Resolution in `api/validate.py`
- Updated `load_outcome_model()` to check multiple possible paths:
  1. `api/models/outcome_rf_regressor.pkl` (relative to function directory)
  2. `models/outcome_rf_regressor.pkl` (root models directory)
  3. Uses `MODEL_DIR` if already set from surgery model loading
- Added comprehensive debug information if model not found

### 3. Verified File Exists
- ✅ File exists at: `DOC_Validator_Vercel/api/models/outcome_rf_regressor.pkl`
- ✅ File size: 454 KB
- ✅ All model files present in `api/models/`:
  - `outcome_rf_regressor.pkl`
  - `random_forest_calibrated.pkl`
  - `scaler.pkl`
  - `feature_names.pkl`

## Deployment Steps

1. **Commit the changes:**
   ```bash
   git add DOC_Validator_Vercel/api/models/outcome_rf_regressor.pkl
   git add DOC_Validator_Vercel/vercel.json
   git add DOC_Validator_Vercel/api/validate.py
   git commit -m "Add outcome model and fix path resolution"
   git push
   ```

2. **Redeploy on Vercel:**
   - Vercel should auto-deploy on push, or
   - Manually trigger deployment in Vercel dashboard

3. **Verify deployment:**
   - Check Vercel build logs to ensure `api/models/**` files are included
   - Test the outcome prediction button after deployment

## Alternative: Manual File Check

If the issue persists after deployment, you can verify the file is included by:

1. Check Vercel build logs for file inclusion
2. Add temporary debug endpoint to list files in `/var/task/api/models/`
3. Ensure `.vercelignore` doesn't exclude `api/models/`

## Notes

- The `includeFiles` pattern `api/models/**` should include all files in that directory
- Path resolution now tries multiple locations for maximum compatibility
- Debug information will help identify the exact issue if it persists

