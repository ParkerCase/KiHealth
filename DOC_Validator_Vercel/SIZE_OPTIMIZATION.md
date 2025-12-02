# Serverless Function Size Optimization

## Problem

Vercel serverless functions have a 250 MB unzipped size limit. Our function exceeds this due to:

- Python dependencies (pandas, numpy, scikit-learn, matplotlib) ~200+ MB
- Model files ~1.1 MB
- Total: ~250+ MB

## Solutions Applied

### 1. Lazy Model Loading ✅

- Models loaded on first request, not at import time
- Reduces initial bundle size

### 2. Optimized Dependencies ✅

- Updated to Python 3.12 compatible versions
- Using pre-built wheels (no compilation)

### 3. Runtime Configuration ✅

- `runtime.txt` specifies Python 3.11 (more stable)
- `vercel.json` includes models separately

## Alternative Solutions (if still too large)

### Option 1: Use Vercel Blob Storage

Store models in Vercel Blob and load at runtime:

```python
from vercel import blob
model_data = blob.get('model-key')
model = joblib.loads(model_data)
```

### Option 2: Use External Storage

- AWS S3
- Cloudflare R2
- Google Cloud Storage
  Load models from URL at runtime

### Option 3: Reduce Dependencies

- Use lighter alternatives (e.g., polars instead of pandas)
- Remove matplotlib, generate plots client-side
- Use minimal scikit-learn subset

### Option 4: Split into Multiple Functions

- Separate function for model loading
- Separate function for predictions
- Use Vercel Edge Functions for lightweight operations

## Current Status

✅ Lazy loading implemented
✅ Dependencies optimized
⏳ Testing deployment

If deployment still fails, we'll implement Option 1 (Vercel Blob Storage).
