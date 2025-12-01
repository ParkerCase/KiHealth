# Vercel Deployment Setup Guide

## Quick Start

### 1. Install Vercel CLI

```bash
npm i -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Test Locally

```bash
cd DOC_Validator_Vercel
vercel dev
```

Access at: `http://localhost:3000`

### 4. Deploy to Production

```bash
vercel deploy --prod
```

## Custom Domain Setup

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Domains
4. Add domain: `validator.stroomai.com`
5. Add CNAME record in DNS:
   - Name: `validator`
   - Value: `[vercel-provided-domain]`

## File Structure

```
DOC_Validator_Vercel/
├── api/                    # Serverless functions
│   ├── validate.py        # Main prediction endpoint
│   └── template.py        # CSV template download
├── public/                # Static files
│   └── index.html
├── static/                # Static assets
│   ├── css/
│   └── js/
├── models/                # Model files (~2 MB total)
│   ├── random_forest_calibrated.pkl
│   ├── scaler.pkl
│   └── feature_names.pkl
├── preprocessing.py       # Shared preprocessing
├── requirements.txt       # Python dependencies
└── vercel.json           # Vercel configuration
```

## Model Files Size

- ✅ `random_forest_calibrated.pkl`: 1.1 MB
- ✅ `scaler.pkl`: 1.2 KB
- ✅ `feature_names.pkl`: 389 B
- ✅ **Total: ~1.1 MB** (well under Vercel's 50MB limit)

**Note:** Large imputer (182 MB) removed - using simple imputation instead.

## Environment Variables

No environment variables needed for basic deployment.

## Testing Checklist

- [ ] Test CSV upload locally
- [ ] Verify predictions are correct
- [ ] Check all plots render
- [ ] Test download functionality
- [ ] Verify error handling
- [ ] Test on production URL
- [ ] Verify custom domain works
- [ ] Test mobile responsiveness

## Troubleshooting

### Cold Start Issues

First request may be slow (model loading). Subsequent requests should be fast.

### Memory Limits

If you get out-of-memory errors:

- Reduce batch size
- Optimize model loading
- Consider upgrading Vercel plan

### File Size Limits

Vercel serverless functions have a 50MB limit. Current deployment is ~1.1 MB ✅

## Support

Contact: parker@stroomai.com
