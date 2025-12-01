# Vercel Deployment Instructions

## Quick Setup Steps

### 1. Import from GitHub

- Repository: `ParkerCase/doc`
- Branch: `main`

### 2. Configure Project Settings

**IMPORTANT:** Change the Root Directory!

- **Root Directory:** `DOC_Validator_Vercel` ⚠️ (NOT `./`)
- **Project Name:** `doc-validator` (or keep `doc`)
- **Framework Preset:** `Other` ✅ (correct - we're using Python)
- **Vercel Team:** Your team (Hobby plan is fine)

### 3. Build and Output Settings (Optional - Expand if needed)

- **Build Command:** Leave empty (auto-detected)
- **Output Directory:** Leave empty (uses `public/` automatically)
- **Install Command:** Leave empty (Vercel installs from `requirements.txt`)

### 4. Environment Variables (Optional)

No environment variables needed for basic deployment.

### 5. Deploy

Click **"Deploy"** button.

---

## After Deployment

### 1. Test the Deployment

Visit your deployment URL (e.g., `doc-validator.vercel.app`)

### 2. Set Custom Domain

1. Go to **Settings → Domains**
2. Add: `validator.stroomai.com`
3. Configure DNS CNAME record

### 3. Verify Functionality

- Upload sample CSV
- Test predictions
- Verify all plots render
- Test download functionality

---

## Troubleshooting

### If deployment fails:

1. **Check Root Directory:** Must be `DOC_Validator_Vercel`
2. **Check Build Logs:** Look for Python errors
3. **Verify Model Files:** Ensure they're in `DOC_Validator_Vercel/models/`
4. **Check Requirements:** Ensure `requirements.txt` is correct

### Common Issues:

- **"Module not found"**: Check `requirements.txt`
- **"Model file not found"**: Verify model files are in `models/` directory
- **"Function timeout"**: Increase timeout in `vercel.json` (already set to 30s)

---

**Status:** Ready to deploy! Just change Root Directory to `DOC_Validator_Vercel`

