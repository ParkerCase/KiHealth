# GitHub Secrets Setup Guide

## ✅ Test Results

Your Google Sheets connection is **working perfectly**! The test successfully:
- ✅ Connected to Google Sheets
- ✅ Created a test record
- ✅ Retrieved the record
- ✅ Updated the record

## Step-by-Step: Add Secrets to GitHub

### Step 1: Go to GitHub Secrets

1. Go to: https://github.com/ParkerCase/doc/settings/secrets/actions
2. Click **"New repository secret"** for each secret below

### Step 2: Add Each Secret

#### Secret 1: GOOGLE_SHEET_ID

- **Name**: `GOOGLE_SHEET_ID`
- **Value**: `1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ`
- Click **"Add secret"**

#### Secret 2: GOOGLE_SERVICE_ACCOUNT_EMAIL

- **Name**: `GOOGLE_SERVICE_ACCOUNT_EMAIL`
- **Value**: `monitoring-system@stroomtrition.iam.gserviceaccount.com`
- Click **"Add secret"**

#### Secret 3: GOOGLE_PRIVATE_KEY

⚠️ **IMPORTANT**: Copy the private key exactly as shown below, including all the `\n` characters.

- **Name**: `GOOGLE_PRIVATE_KEY`
- **Value**: (Copy the entire key below - it's long!)

```
-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz+sQdDZszp4Rl\nnjHCVcP7aybaZFQAzMP3Zruh+4TiavtcF07QMfhIvpQfEwt2UcbRZTmSZFOs+ej5\nfL4ooKo85DmppniirpUVQ4zpeeDLWLdpruG5OhVGpu4Yf+85+EL/Buz9lWeJF/fu\nIguB0PEqpesp2ZcZCpwTewO06hbPNd/WByPara0E9L8JMT959Dz2XbPH00gwcngG\nMzLfSUV0az904dOS59V7BCV3Bq8DcJwI4x7UWiJT6kTi5r9msVX955gRKom3WMYJ\nz7yVVzb34U91512PZFeQI+CqwdT7LFRKmyp+yn7rofw7Jwahdn+HOxAeTsV14fKl\nPnrEwZ3XAgMBAAECggEACx3iHylH/NjMBLrQuAA0KsNjkvm/do0vTYi67jZq7tFM\n1VNbOuDbRSMAYyr5+kTy0tw9wh0QTg7hpQdfd4L1AO3X4fK2YNYHv1h8y68Lg4Pn\nUE/NAXPk/IgzDLBaRmpfOQFkggVIb99bIQpZS5tsSgYVkHAwNQvCuDFQ+Uu8PPAs\nY1Ga2tMy+KVm6d5YJMVesOS9gC4Rbdk8Zx9R4+aNRBu2tMUKVBb/RdlhIdpJIooj\nWP6GTUxG5tWbhaxPtHLxA4QYLryVkGtY5A5ZW9Z9EqYvfukLZ3BHSvKwj6wTXE0r\n16zTyEey/ue24XjkNQFr/QCr8joHiTrCa61BryO5gQKBgQDjkflE6sPrL2nFEGQB\n0Jdo5RU7oEf2DbN+Na+u0/sVcnl2MERrcOhxMkq3N4q2OyyOomYWJAfPiYNoQ8B6\nNSI0H6Dh26Uhpwbgop/vKYS8AHHJPf2Z6cXFjPAEcPZfGcYcUI8zyrlgDhKU/OcD\nTSXPhfnyjZjQ0kDkywU480ykfQKBgQDKdsYk+yqnyeIGKQnTODEZfVW5nTMv/aUH\n9TYLbe7/xrBX6M4IcNa0a5eZDCtXFfjNdIk4gp/4id0ZobCN/8+LtHeNjkNdH3Cs\nxtr4SW2+LuG6g0Mq020Rzvduy7cIEe9Q93mIFoC5QxSaRFXqKnkZVnYtkltIatHl\n+6KoPmU/4wKBgQCUid5Tbo1NAJigSU+No7KAhC60yazO3SiQs8glbDYSTLMdQuoV\n2w/New8rwfQneD5gJ35M612xyEdekgKbgfz+WrqvUafabGRf0aZk/Auojv22ZmEW\nynENvi2YKIeXkYIvTyH5o1QWb3kPiHfdPsj0SLXZ7TSW8PXsoNuazav0HQKBgG7N\n4BU/LJIVh9CtRwZE+4IiuPbTlL8QBvC6/6/zo1hySfJio9e0wZyOQbJuGY4YpUj0\nHWFDA//Gm626cuDT/qdLxh4/nJhra4PzdMVrklcCW2FzEyBuA4Q6i+okLXCKODpM\npkOXZS1/C9h9y7NTOWFnk1fPgIu6glNmixeexlTXAoGAVdT498Rhy9f5Z3v2gjzt\nr8jn8706znt+8Dz5VAFP7HJTRSWXNimR+JlYhq+VfBArS0aOESRFP4pZ+IJJzSm0\nhC6GNPAqa6aImlzbjuiY9QarSRK2yLHCqxYWxV0/JyAtMBPcXH+HL5q4YeBD0lLd\nrdne+A+pECBrbbArScRnZC0=\n-----END PRIVATE KEY-----\n
```

**Important Notes**:
- Copy the ENTIRE key above (from `-----BEGIN` to `-----END`)
- Keep the `\n` characters as-is (they represent newlines)
- Don't add extra spaces or line breaks
- Click **"Add secret"**

#### Secret 4: ANTHROPIC_API_KEY

- **Name**: `ANTHROPIC_API_KEY`
- **Value**: `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`
- Click **"Add secret"**

#### Secret 5: AI_PROVIDER (Optional but Recommended)

- **Name**: `AI_PROVIDER`
- **Value**: `anthropic`
- Click **"Add secret"**

## Step 3: Verify Secrets

After adding all secrets, you should see:
- ✅ GOOGLE_SHEET_ID
- ✅ GOOGLE_SERVICE_ACCOUNT_EMAIL
- ✅ GOOGLE_PRIVATE_KEY
- ✅ ANTHROPIC_API_KEY
- ✅ AI_PROVIDER (optional)

## Step 4: Test the Workflow

1. Go to: https://github.com/ParkerCase/doc/actions
2. Click **"Weekly Monitoring System"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 5-10 minutes
5. Check your Google Sheet - data should appear!

## What to Expect

### In Google Sheets:
- **`papers` sheet** will be created automatically
- **`lincs_data` sheet** will be created automatically
- Data will appear as rows
- You can filter, sort, and analyze!

### In GitHub Actions:
- All jobs should complete with ✅ green checkmarks
- No errors about missing credentials
- Logs will show successful connections

## Troubleshooting

### "Permission denied" error:
- ✅ Make sure sheet is shared with: `monitoring-system@stroomtrition.iam.gserviceaccount.com`
- ✅ Give it "Editor" permission

### "Sheet not found" error:
- ✅ Check GOOGLE_SHEET_ID is correct: `1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ`

### "Invalid credentials" error:
- ✅ Check GOOGLE_PRIVATE_KEY includes the full key
- ✅ Make sure `\n` characters are included (not actual line breaks)

### "ANTHROPIC_API_KEY not found":
- ✅ Check the API key is added correctly
- ✅ Make sure there are no extra spaces

## Summary

✅ **Connection tested and working**
✅ **All credentials verified**
✅ **Ready to add to GitHub Secrets**
✅ **System will work once secrets are added**

After adding secrets, trigger the workflow manually to test! 🚀

