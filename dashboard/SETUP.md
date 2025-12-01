# Quick Setup Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### 2. Set Up Environment Variables

Create `.env.local` file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and add your Xata credentials:

```env
XATA_API_KEY=xata_your_api_key_here
XATA_DB_URL=https://your-workspace-id.us-east-1.xata.sh/db/your-database-name:main
```

**Where to find your Xata API key:**

1. Go to https://app.xata.io
2. Click on your workspace
3. Go to **Settings** → **API Keys**
4. Create a new key or copy an existing one
5. Paste it into `.env.local`

### 3. Run the Dashboard

```bash
npm run dev
```

Open [http://localhost:3003](http://localhost:3003) in your browser!

---

## 📋 What You'll See

- **Table of 77 cancer types** sorted by overall score
- **Search bar** to filter by cancer type or confidence tier
- **Key metrics**:
  - Overall score
  - Confidence tier (HIGH/MEDIUM/LOW)
  - Number of cell lines
  - Synthetic lethality hits
  - Top target gene

---

## 🚢 Deploy to Vercel

### Option 1: Vercel CLI

```bash
npm i -g vercel
vercel login
vercel
```

Then add environment variables in Vercel dashboard:

- `XATA_API_KEY`
- `XATA_DB_URL`

### Option 2: GitHub + Vercel

1. Push code to GitHub
2. Import repo in Vercel
3. Add environment variables
4. Deploy!

---

## ❓ Troubleshooting

**"Failed to fetch rankings"**

- Check `.env.local` exists and has correct values
- Verify API key is valid
- Ensure `cancer_rankings` table exists in Xata

**Port 3003 in use?**

- Change port in `package.json`: `"dev": "next dev -p 3004"`

**Need help?**

- Check the full [README.md](./README.md) for detailed documentation
