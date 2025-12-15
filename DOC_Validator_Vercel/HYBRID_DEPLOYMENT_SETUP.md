# Hybrid Deployment Setup: Vercel Frontend + Railway Backend

## Overview

This setup deploys:
- **Frontend** (HTML/CSS/JS) → Vercel (fast CDN, no size limits for static files)
- **Backend API** (Python/ML models) → Railway (no size limits, full functionality)

## Architecture

```
User Browser
    ↓
Vercel (Frontend)
    ↓ (API calls)
Railway (Backend API)
    ↓
ML Models & Predictions
```

## Railway Backend

**URL:** `https://doc-production-5888.up.railway.app`

**Endpoints:**
- `POST /api/validate` - Main prediction endpoint
- `GET /api/template` - CSV template download
- `GET /health` - Health check

**Status:** ✅ Already deployed and running

## Vercel Frontend Deployment

### Option 1: Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import from GitHub: `ParkerCase/doc`
4. Configure:
   - **Root Directory:** `DOC_Validator_Vercel`
   - **Framework Preset:** `Other`
   - **Build Command:** Leave empty
   - **Output Directory:** `public`
   - **Install Command:** Leave empty (no dependencies needed)
5. Click "Deploy"

### Option 2: Deploy via CLI

```bash
cd DOC_Validator_Vercel
vercel --prod
```

When prompted:
- Set root directory to: `DOC_Validator_Vercel`
- Output directory: `public`
- No build command needed

## Configuration

The frontend automatically detects the environment:
- **Local development** (`localhost`): Uses relative URLs (`/api/validate`)
- **Production** (Vercel): Uses Railway API URL (`https://doc-production-5888.up.railway.app/api/validate`)

This is configured in `public/static/js/main.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? '' // Use relative URLs for local development
  : 'https://doc-production-5888.up.railway.app'; // Railway API URL for production
```

## Benefits

✅ **Fast static file serving** - Vercel's global CDN  
✅ **No size limits** - Backend on Railway, frontend is tiny  
✅ **Full functionality** - All ML models work perfectly  
✅ **Easy updates** - Update frontend or backend independently  
✅ **Cost effective** - Both platforms have free tiers  

## Testing

### Local Development

1. Start Railway backend (already running)
2. Open `public/index.html` in browser
3. Frontend will use relative URLs and work with Railway API

### Production

1. Frontend deployed to Vercel
2. Backend running on Railway
3. Frontend automatically uses Railway API URL

## Troubleshooting

### CORS Issues

Railway backend already has CORS headers configured:
```python
self.send_header('Access-Control-Allow-Origin', '*')
```

### API Not Responding

1. Check Railway logs: `railway logs`
2. Verify Railway URL is correct in `main.js`
3. Test Railway API directly: `curl https://doc-production-5888.up.railway.app/health`

### Frontend Not Loading

1. Check Vercel deployment logs
2. Verify `public/` directory structure
3. Check browser console for errors

## Updating Railway URL

If Railway URL changes, update in:
1. `public/static/js/main.js` - `API_BASE_URL` constant
2. `public/index.html` - Template download link

## Status

- ✅ Railway backend deployed
- ✅ Frontend configured for Railway API
- ⏳ Vercel frontend deployment ready

