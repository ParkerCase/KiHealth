# DOC Model Validator - Vercel Deployment

Web-based validator for the DOC (Digital Osteoarthritis Counseling) knee replacement prediction model.

## Features

- **Batch Processing:** Upload CSV with multiple patients
- **Real-time Predictions:** Get risk predictions for all patients
- **Validation Metrics:** If outcomes provided, calculate AUC, Brier score, calibration plots
- **Visualizations:** Risk distribution, ROC curves, calibration plots
- **Privacy-First:** No data storage, all processing in memory

## Local Testing

```bash
# Install Vercel CLI
npm i -g vercel

# Install Python dependencies
pip install -r requirements.txt

# Test locally
vercel dev
```

Access at: `http://localhost:3000`

## Deploy to Vercel

```bash
# Deploy to production
vercel deploy --prod
```

## Custom Domain Setup

1. Go to Vercel Dashboard → Settings → Domains
2. Add: `validator.stroomai.com`
3. Add CNAME in DNS: `validator` → `[vercel-domain]`

## File Structure

```
DOC_Validator_Vercel/
├── api/
│   ├── validate.py      # Main prediction endpoint
│   └── template.py      # CSV template download
├── public/
│   └── index.html       # Main page
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── models/              # Model files (copy from ../models/)
├── preprocessing.py     # Shared preprocessing logic
├── requirements.txt     # Python dependencies
└── vercel.json         # Vercel configuration
```

## Model Files Required

Copy these files from `../models/` to `models/`:

- `random_forest_calibrated.pkl` (1.1 MB)
- `scaler.pkl`
- `imputer_numeric.pkl`
- `feature_names.pkl`

## CSV Format

Required columns:

- `age` (45-79)
- `sex` (1=Male, 0=Female)
- `bmi` (15-50)
- `womac_r` (0-96)
- `womac_l` (0-96)
- `kl_r` (0-4)
- `kl_l` (0-4)
- `fam_hx` (1=Yes, 0=No)
- `tkr_outcome` (1=Yes, 0=No) - Optional, for validation

## Testing Checklist

1. ✅ Test locally with `vercel dev`
2. ✅ Upload sample CSV
3. ✅ Verify predictions match notebook
4. ✅ Check all plots render
5. ✅ Test download functionality
6. ✅ Deploy to production

## Deployment Size

- Models: ~2-3 MB total
- Well under Vercel's 50MB limit ✅

## Privacy

- **No data storage:** All processing in memory
- **No logging:** Patient data never logged
- **Stateless:** Each request is independent
- **GDPR compliant:** No data retention

## Support

Contact: parker@stroomai.com
