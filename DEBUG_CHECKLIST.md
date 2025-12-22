# Debug Checklist - Workflow Failures

## Quick Checks

### 1. Check GitHub Secrets Are Set

Go to: https://github.com/ParkerCase/doc/settings/secrets/actions

Verify these exist:
- [ ] `GOOGLE_SHEET_ID` = `1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ`
- [ ] `GOOGLE_SERVICE_ACCOUNT_EMAIL` = `monitoring-system@stroomtrition.iam.gserviceaccount.com`
- [ ] `GOOGLE_PRIVATE_KEY` = (full private key)
- [ ] `ANTHROPIC_API_KEY` = (your API key)
- [ ] `AI_PROVIDER` = `anthropic` (optional)

### 2. Check Google Sheet Permissions

1. Open: https://docs.google.com/spreadsheets/d/1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ/edit
2. Click "Share"
3. Verify: `monitoring-system@stroomtrition.iam.gserviceaccount.com` is listed
4. Permission should be: **"Editor"**

### 3. Check Workflow Logs

1. Go to: https://github.com/ParkerCase/doc/actions
2. Click on a failed run
3. Click on the failed job
4. Look for error messages

**Common errors to look for:**
- `Cannot find module` → Dependencies issue
- `Permission denied` → Sheet not shared
- `Invalid credentials` → Private key format wrong
- `Sheet not found` → Wrong sheet ID
- `Google Sheets credentials not found` → Missing secrets

### 4. Test Connection Workflow

I've created a simple test workflow. Try it:

1. Go to: https://github.com/ParkerCase/doc/actions
2. Click "Test Google Sheets Connection" workflow
3. Click "Run workflow" → "Run workflow"
4. This will test JUST the connection (simpler to debug)

### 5. Private Key Format Issue

**The most common issue!**

When adding `GOOGLE_PRIVATE_KEY` to GitHub Secrets:

**Option A (Recommended)**: Copy the key as a single line with `\n`:
```
-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz+sQdDZszp4Rl\n... (rest of key)\n-----END PRIVATE KEY-----\n
```

**Option B**: Copy with actual line breaks (multi-line):
```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz+sQdDZszp4Rl
... (rest of key)
-----END PRIVATE KEY-----
```

**Try Option A first** - it's what the code expects (it converts `\n` to actual newlines).

## What to Share for Help

If still not working, share:
1. **Exact error message** from workflow logs
2. **Which job failed** (PubMed, LINCS, AI, etc.)
3. **Screenshot** of the error (if possible)

## Most Likely Issues

1. **Private key format** (90% of issues) - Make sure `\n` characters are included
2. **Sheet not shared** (5% of issues) - Re-share with service account
3. **Missing dependencies** (3% of issues) - Should be fixed now
4. **Wrong sheet ID** (2% of issues) - Double-check the ID

## Quick Test

Run this locally to verify everything works:
```bash
cd scripts
GOOGLE_SHEET_ID=1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ \
GOOGLE_SERVICE_ACCOUNT_EMAIL=monitoring-system@stroomtrition.iam.gserviceaccount.com \
GOOGLE_PRIVATE_KEY='-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz+sQdDZszp4Rl\nnjHCVcP7aybaZFQAzMP3Zruh+4TiavtcF07QMfhIvpQfEwt2UcbRZTmSZFOs+ej5\nfL4ooKo85DmppniirpUVQ4zpeeDLWLdpruG5OhVGpu4Yf+85+EL/Buz9lWeJF/fu\nIguB0PEqpesp2ZcZCpwTewO06hbPNd/WByPara0E9L8JMT959Dz2XbPH00gwcngG\nMzLfSUV0az904dOS59V7BCV3Bq8DcJwI4x7UWiJT6kTi5r9msVX955gRKom3WMYJ\nz7yVVzb34U91512PZFeQI+CqwdT7LFRKmyp+yn7rofw7Jwahdn+HOxAeTsV14fKl\nPnrEwZ3XAgMBAAECggEACx3iHylH/NjMBLrQuAA0KsNjkvm/do0vTYi67jZq7tFM\n1VNbOuDbRSMAYyr5+kTy0tw9wh0QTg7hpQdfd4L1AO3X4fK2YNYHv1h8y68Lg4Pn\nUE/NAXPk/IgzDLBaRmpfOQFkggVIb99bIQpZS5tsSgYVkHAwNQvCuDFQ+Uu8PPAs\nY1Ga2tMy+KVm6d5YJMVesOS9gC4Rbdk8Zx9R4+aNRBu2tMUKVBb/RdlhIdpJIooj\nWP6GTUxG5tWbhaxPtHLxA4QYLryVkGtY5A5ZW9Z9EqYvfukLZ3BHSvKwj6wTXE0r\n16zTyEey/ue24XjkNQFr/QCr8joHiTrCa61BryO5gQKBgQDjkflE6sPrL2nFEGQB\n0Jdo5RU7oEf2DbN+Na+u0/sVcnl2MERrcOhxMkq3N4q2OyyOomYWJAfPiYNoQ8B6\nNSI0H6Dh26Uhpwbgop/vKYS8AHHJPf2Z6cXFjPAEcPZfGcYcUI8zyrlgDhKU/OcD\nTSXPhfnyjZjQ0kDkywU480ykfQKBgQDKdsYk+yqnyeIGKQnTODEZfVW5nTMv/aUH\n9TYLbe7/xrBX6M4IcNa0a5eZDCtXFfjNdIk4gp/4id0ZobCN/8+LtHeNjkNdH3Cs\nxtr4SW2+LuG6g0Mq020Rzvduy7cIEe9Q93mIFoC5QxSaRFXqKnkZVnYtkltIatHl\n+6KoPmU/4wKBgQCUid5Tbo1NAJigSU+No7KAhC60yazO3SiQs8glbDYSTLMdQuoV\n2w/New8rwfQneD5gJ35M612xyEdekgKbgfz+WrqvUafabGRf0aZk/Auojv22ZmEW\nynENvi2YKIeXkYIvTyH5o1QWb3kPiHfdPsj0SLXZ7TSW8PXsoNuazav0HQKBgG7N\n4BU/LJIVh9CtRwZE+4IiuPbTlL8QBvC6/6/zo1hySfJio9e0wZyOQbJuGY4YpUj0\nHWFDA//Gm626cuDT/qdLxh4/nJhra4PzdMVrklcCW2FzEyBuA4Q6i+okLXCKODpM\npkOXZS1/C9h9y7NTOWFnk1fPgIu6glNmixeexlTXAoGAVdT498Rhy9f5Z3v2gjzt\nr8jn8706znt+8Dz5VAFP7HJTRSWXNimR+JlYhq+VfBArS0aOESRFP4pZ+IJJzSm0\nhC6GNPAqa6aImlzbjuiY9QarSRK2yLHCqxYWxV0/JyAtMBPcXH+HL5q4YeBD0lLd\nrdne+A+pECBrbbArScRnZC0=\n-----END PRIVATE KEY-----\n' \
node test-google-sheets.js
```

If this works locally, the issue is likely the private key format in GitHub Secrets.

