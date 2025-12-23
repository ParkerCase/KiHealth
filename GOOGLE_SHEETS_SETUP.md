# Google Sheets Setup Guide

## Overview

The monitoring system now uses **Google Sheets** for data storage, making it easy to view and monitor all data in one place!

## Benefits

✅ **Easy Monitoring** - View all data in Google Sheets
✅ **Free** - Google Sheets is free
✅ **Filterable** - Easy to filter and sort data
✅ **Shareable** - Share with team members
✅ **Automatic** - Data updates automatically

## Setup Steps

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable **Google Sheets API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

### Step 2: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name it: `monitoring-system` (or any name)
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

### Step 3: Create Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Download the JSON file

### Step 4: Create Google Sheet

1. Go to https://sheets.google.com
2. Create a new spreadsheet
3. Name it: "Monitoring Data" (or any name)
4. **Share with service account**:
   - Click "Share" button
   - Add the service account email (from JSON file, field: `client_email`)
   - Give it "Editor" permission
   - Click "Send"

### Step 5: Get Sheet ID

1. Open your Google Sheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ/edit`
3. Copy the `1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ` part

### Step 6: Extract Credentials from JSON

Open the downloaded JSON file and find:
- `client_email` → This is `GOOGLE_SERVICE_ACCOUNT_EMAIL`
- `private_key` → This is `GOOGLE_PRIVATE_KEY`
- Sheet ID from URL → This is `GOOGLE_SHEET_ID`

### Step 7: Add to GitHub Secrets

1. Go to: https://github.com/ParkerCase/doc/settings/secrets/actions
2. Add these secrets:

**GOOGLE_SHEET_ID**
- Value: The sheet ID from the URL

**GOOGLE_SERVICE_ACCOUNT_EMAIL**
- Value: The `client_email` from JSON file

**GOOGLE_PRIVATE_KEY**
- Value: The `private_key` from JSON file (include the full key with `\n` characters)

**ANTHROPIC_API_KEY**
- Value: Your Anthropic API key (from .env.local)

**AI_PROVIDER** (optional)
- Value: `anthropic`

## How It Works

1. **Sheets Created Automatically**:
   - `papers` sheet - PubMed articles
   - `lincs_data` sheet - LINCS data

2. **Data Updates**:
   - New records added as rows
   - Existing records updated in place
   - All data visible in Google Sheets

3. **Fallback**:
   - If Google Sheets credentials not found, falls back to file storage
   - System still works without Google Sheets

## Schedule

- **Runs**: Weekly on Mondays at 2 AM EST (7 AM UTC)
- **First Run**: Can trigger manually anytime
- **Saves Credits**: Weekly schedule reduces AI API usage

## Monitoring

View your data:
1. Open your Google Sheet
2. See `papers` tab for PubMed articles
3. See `lincs_data` tab for LINCS data
4. Filter, sort, and analyze as needed!

## Troubleshooting

**"Permission denied"**:
- Make sure service account email has "Editor" access to sheet

**"Sheet not found"**:
- Check GOOGLE_SHEET_ID is correct (from URL)

**"Invalid credentials"**:
- Check GOOGLE_PRIVATE_KEY includes `\n` characters
- Make sure JSON was copied correctly

## Cost

✅ **Google Sheets**: Free (up to 10 million cells)
✅ **Google API**: Free (generous quotas)
✅ **Total**: $0/month for storage

Plus AI costs if using:
- Anthropic: ~$5-20/month (weekly schedule reduces this)
- OpenAI: ~$10-30/month

