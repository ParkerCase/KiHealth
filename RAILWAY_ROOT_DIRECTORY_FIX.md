# Railway Root Directory Fix

## Problem
Railway is looking at the repo root (`/`), but the code is in `DOC_Validator_Vercel/`. This causes:
- `railway.json` in `DOC_Validator_Vercel/` is skipped
- No start command found
- Deployment fails

## Solution: Set Root Directory in Railway Dashboard

**You need to configure Railway to use `DOC_Validator_Vercel` as the root directory:**

### Step 1: Go to Railway Dashboard
1. Open https://railway.app
2. Select your **DOC** project
3. Click on the **DOC** service

### Step 2: Set Root Directory
1. Go to **Settings** tab
2. Scroll to **"Source"** section
3. Find **"Root Directory"** setting
4. Change it from `/` (root) to: **`DOC_Validator_Vercel`**
5. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest deployment
3. Or trigger a new deployment

### Step 4: Verify
After deployment, check the build logs. You should see:
- ✅ Finding `railway.json` in `DOC_Validator_Vercel/`
- ✅ Running `pip install -r requirements.txt`
- ✅ Starting with `python main.py`
- ✅ Deployment successful

## Alternative: Use Railway CLI (if logged in)

If you're logged into Railway CLI:

```bash
cd /Users/parkercase/DOC/DOC_Validator_Vercel
railway link  # Link to your project
railway up   # Deploy
```

But the **dashboard method is easier** - just set the root directory in Settings.

## Current Status

- ✅ `railway.json` exists at root (fallback)
- ⚠️ Railway needs root directory set to `DOC_Validator_Vercel` in dashboard
- ❌ Deployment failing because Railway is looking at wrong directory

**Fix: Set Root Directory = `DOC_Validator_Vercel` in Railway Settings**
