# Deploy Backend Update to Railway

## Status: ⚠️ Backend code updated but NOT YET DEPLOYED

The backend code in `api/validate.py` has been updated with:
- Model selection parameter parsing
- Model verification logging
- `model_type` in response

**But Railway is still running the OLD code** - that's why `model_type` is `undefined` in responses.

## How to Deploy to Railway

### Option 1: Git Push (Recommended)
If Railway is connected to your GitHub repo:

```bash
cd /Users/parkercase/DOC
git add DOC_Validator_Vercel/api/validate.py
git commit -m "Add model selection and verification to backend"
git push origin main
```

Railway will automatically detect the push and redeploy.

### Option 2: Railway CLI
```bash
cd DOC_Validator_Vercel
railway up
```

### Option 3: Manual Deploy via Railway Dashboard
1. Go to https://railway.app
2. Select your project: `doc-production-5888`
3. Go to "Deployments" tab
4. Click "Redeploy" or trigger a new deployment

## How to Verify It's Working

After deployment, check Railway logs. You should see:

```
🔍 Content-Type: multipart/form-data; boundary=...
🔍 Found use_literature_calibration in part X!
🔍 Parsed use_literature_calibration: True
🔍 ===== MODEL LOADING ======
🔍 use_literature_calibration value: True
✓ Using Literature-Calibrated model
  - Model type: CalibratedModelWrapper
  - Model file: random_forest_literature_calibrated_base.pkl
  - Model ID: [unique number]
🔍 Making predictions with model: CalibratedModelWrapper (ID: [number])
🔍 Sending response with model_type: 'Literature-Calibrated'
```

**Key verification:**
- Different model IDs when checkbox is checked vs unchecked
- Different model class names (`CalibratedModelWrapper` vs `RandomForestClassifier`)
- `model_type` appears in response (not `undefined`)

## Current Status

- ✅ Frontend: Updated and working (with fallback)
- ⚠️ Backend: Code updated but NOT deployed to Railway yet
- ❌ Result: Backend not using correct model (still using original)

**Next step: Deploy to Railway!**
