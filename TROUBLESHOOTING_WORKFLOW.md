# Troubleshooting Workflow Failures

## Common Issues and Fixes

### Issue 1: Missing Dependencies

**Symptom**: `Cannot find module 'google-spreadsheet'` or similar

**Fix**: Make sure `package.json` is committed with all dependencies.

**Check**:
```bash
cd scripts
cat package.json | grep google-spreadsheet
```

Should show: `"google-spreadsheet": "^4.1.5"`

**Solution**: If missing, run:
```bash
cd scripts
npm install google-spreadsheet google-auth-library
git add package.json package-lock.json
git commit -m "Add Google Sheets dependencies"
git push
```

### Issue 2: Private Key Format in GitHub Secrets

**Symptom**: `Invalid credentials` or `401 Unauthorized`

**Problem**: GitHub Secrets might need actual newlines, not `\n` characters.

**Fix**: When adding `GOOGLE_PRIVATE_KEY` to GitHub Secrets:
1. Copy the private key from JSON file
2. **Replace all `\n` with actual line breaks** (press Enter)
3. Or keep `\n` but make sure it's the full key

**Test**: The key should look like this in GitHub Secrets:
```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz+sQdDZszp4Rl
... (rest of key)
-----END PRIVATE KEY-----
```

### Issue 3: Sheet Not Shared

**Symptom**: `Permission denied` or `403 Forbidden`

**Fix**: 
1. Open your Google Sheet
2. Click "Share"
3. Add: `monitoring-system@stroomtrition.iam.gserviceaccount.com`
4. Give it **"Editor"** permission
5. Click "Send"

### Issue 4: Wrong Sheet ID

**Symptom**: `Sheet not found` or `404 Not Found`

**Fix**: 
- Check `GOOGLE_SHEET_ID` in GitHub Secrets
- Should be: `1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ`
- Get it from URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

### Issue 5: Missing Environment Variables

**Symptom**: Scripts fail with "not found" errors

**Check**: All these secrets should be in GitHub:
- ✅ GOOGLE_SHEET_ID
- ✅ GOOGLE_SERVICE_ACCOUNT_EMAIL  
- ✅ GOOGLE_PRIVATE_KEY
- ✅ ANTHROPIC_API_KEY
- ✅ AI_PROVIDER (optional)

## How to Debug

### Step 1: Check Workflow Logs

1. Go to: https://github.com/ParkerCase/doc/actions
2. Click on a failed workflow run
3. Click on the failed job (e.g., "PubMed Monitoring")
4. Expand the failed step
5. Look for error messages

### Step 2: Common Error Messages

**"Cannot find module 'google-spreadsheet'"**
→ Dependencies not installed. Fix: Commit package.json with dependencies.

**"Google Sheets credentials not found"**
→ Missing secrets. Fix: Add all Google Sheets secrets to GitHub.

**"Permission denied"**
→ Sheet not shared. Fix: Share sheet with service account email.

**"Invalid credentials"**
→ Private key format wrong. Fix: Check private key format in secrets.

**"Sheet not found"**
→ Wrong sheet ID. Fix: Verify GOOGLE_SHEET_ID is correct.

### Step 3: Test Locally

Run this to test your setup:
```bash
cd scripts
GOOGLE_SHEET_ID=1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ \
GOOGLE_SERVICE_ACCOUNT_EMAIL=monitoring-system@stroomtrition.iam.gserviceaccount.com \
GOOGLE_PRIVATE_KEY='-----BEGIN PRIVATE KEY-----\n...' \
node test-google-sheets.js
```

## Quick Fixes

### Fix 1: Ensure package.json is Committed

```bash
cd /Users/parkercase/DOC
git add scripts/package.json scripts/package-lock.json
git commit -m "Ensure Google Sheets dependencies are committed"
git push
```

### Fix 2: Verify Secrets Format

In GitHub Secrets, the private key should be:
- Option A: Full key with `\n` characters (as single line)
- Option B: Full key with actual line breaks (multi-line)

Both should work, but if one doesn't, try the other.

### Fix 3: Re-share Google Sheet

1. Open: https://docs.google.com/spreadsheets/d/1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ/edit
2. Click "Share"
3. Verify: `monitoring-system@stroomtrition.iam.gserviceaccount.com` has "Editor" access
4. If not, add it with "Editor" permission

## Still Not Working?

1. **Check the exact error** in GitHub Actions logs
2. **Copy the error message** 
3. **Share it** and I can help debug further

Most common issue: **Private key format** - make sure it's copied correctly from JSON file!

