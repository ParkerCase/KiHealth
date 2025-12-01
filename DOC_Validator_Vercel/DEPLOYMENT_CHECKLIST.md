# DOC Validator - Deployment Checklist

## Pre-Deployment

- [x] All files created
- [x] Model files copied to `models/` directory
- [x] Preprocessing matches training pipeline
- [x] API endpoints tested
- [x] Frontend HTML/CSS/JS complete

## Local Testing

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Test locally
cd DOC_Validator_Vercel
vercel dev
```

- [ ] Test CSV upload
- [ ] Verify predictions are correct
- [ ] Check all plots render
- [ ] Test download functionality
- [ ] Verify error handling

## Production Deployment

```bash
# Deploy to production
vercel deploy --prod
```

- [ ] Deploy successful
- [ ] Test on production URL
- [ ] Verify custom domain (validator.stroomai.com)
- [ ] Test from different devices
- [ ] Check mobile responsiveness

## Post-Deployment

- [ ] Monitor error logs
- [ ] Test with real data (anonymized)
- [ ] Gather user feedback
- [ ] Document any issues

## File Verification

```bash
# Check all required files exist
ls -la DOC_Validator_Vercel/api/*.py
ls -la DOC_Validator_Vercel/public/index.html
ls -la DOC_Validator_Vercel/static/css/style.css
ls -la DOC_Validator_Vercel/static/js/main.js
ls -la DOC_Validator_Vercel/models/*.pkl
```

## Model Files Size Check

- `random_forest_calibrated.pkl`: ~1.1 MB ✅
- `scaler.pkl`: ~1.2 KB ✅
- `imputer_numeric.pkl`: ~182 MB ⚠️ (may need optimization)
- `feature_names.pkl`: ~389 B ✅

**Total:** ~183 MB (may exceed Vercel's 50MB limit for serverless functions)

## Potential Issues

1. **Large imputer file (182 MB):**

   - May need to use smaller imputer or exclude it
   - Most data should be complete anyway
   - Consider using mode imputation for missing values

2. **Cold start time:**

   - First request may be slow (model loading)
   - Subsequent requests should be fast

3. **Memory limits:**
   - Vercel serverless functions have memory limits
   - Monitor for out-of-memory errors

## Optimization Options

If deployment fails due to size:

1. **Remove imputer:** Use mode imputation instead
2. **Compress models:** Use joblib compression
3. **Use external storage:** Store models in S3/Cloudflare R2
4. **Alternative platform:** Consider Railway or AWS Lambda

## Status

✅ **Ready for local testing**
⏳ **Awaiting deployment**
