# Environment Variables Setup

## Quick Fix

You need to create a `.env.local` file in the `dashboard` directory with your Xata credentials.

### Steps:

1. **Create the file:**

   ```bash
   cd dashboard
   cp .env.local.example .env.local
   ```

2. **Edit `.env.local` and add your actual values:**

   ```env
   XATA_API_KEY=your_actual_api_key_here
   XATA_DB_URL=https://your-workspace-id.us-east-1.xata.sh/db/your-database-name:main
   ```

3. **Where to find these values:**

   - **XATA_API_KEY**: Go to https://app.xata.io → Settings → API Keys → Create or copy a key
   - **XATA_DB_URL**: Go to your database in Xata → Copy the database URL from the connection info

4. **Restart the dev server:**
   ```bash
   # Stop the current server (Ctrl+C)
   npm run dev
   ```

### Example `.env.local`:

```env
XATA_API_KEY=xata_abc123xyz789...
XATA_DB_URL=https://Parker-Case-s-workspace-s4h25u.us-east-1.xata.sh/db/starx-therapeutics:main
```

**Important**: Never commit `.env.local` to git (it's already in `.gitignore`)
