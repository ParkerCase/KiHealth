# How to Get Your Xata API Key

## Quick Steps:

1. **Go to Xata Dashboard:**

   - Open https://app.xata.io in your browser
   - Log in to your account

2. **Navigate to API Keys:**

   - Click on your workspace (top left)
   - Go to **Settings** (gear icon or sidebar)
   - Click on **API Keys** in the settings menu

3. **Create or Copy an API Key:**

   - If you don't have one: Click **"Create API Key"**
   - Give it a name (e.g., "Dashboard")
   - Copy the key immediately (you won't see it again!)
   - If you have one: Just copy it

4. **Update `.env.local`:**

   - Open `dashboard/.env.local` in your editor
   - Replace `your_xata_api_key_here` with your actual key
   - It should look like: `XATA_API_KEY=xata_abc123xyz789...`
   - Save the file

5. **The dev server will automatically reload** (you should see "Reload env: .env.local" in the terminal)

## Example `.env.local`:

```env
XATA_API_KEY=xata_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
XATA_DB_URL=https://Parker-Case-s-workspace-s4h25u.us-east-1.xata.sh/db/starx-therapeutics:main
```

**Important**:

- API keys start with `xata_`
- Never share your API key publicly
- The `.env.local` file is already in `.gitignore` so it won't be committed

After updating the API key, refresh your browser and the dashboard should work! 🎉
