# Cancer Rankings Dashboard

A Next.js dashboard that displays cancer type rankings from your Xata database, sorted by overall score with search functionality.

## Features

- ✅ Connects to Xata database
- ✅ Displays cancer rankings sorted by overall score
- ✅ Real-time search by cancer type or confidence tier
- ✅ Beautiful Tailwind CSS styling
- ✅ Responsive design
- ✅ Ready for Vercel deployment

## Prerequisites

- Node.js 18+ installed
- A Xata account with your database set up
- Xata API key and branch name

## Setup Instructions

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the `dashboard` directory:

```bash
cp .env.local.example .env.local
```

Then edit `.env.local` and add your Xata credentials:

```env
XATA_API_KEY=your_xata_api_key_here
XATA_DB_URL=https://your-workspace-id.us-east-1.xata.sh/db/your-database-name:main
```

**Note**: Use `XATA_DB_URL` (full database URL) instead of `XATA_BRANCH`. You can find your database URL in the Xata dashboard.

**How to get your Xata API key:**

1. Go to [Xata Dashboard](https://app.xata.io)
2. Navigate to your workspace
3. Go to Settings → API Keys
4. Create a new API key or copy an existing one
5. Your branch name is usually `main` (check in your Xata dashboard)

### 3. Run the Development Server

```bash
npm run dev
```

The dashboard will be available at [http://localhost:3003](http://localhost:3003)

## Project Structure

```
dashboard/
├── app/
│   ├── api/
│   │   └── rankings/
│   │       └── route.ts          # API route to fetch rankings from Xata
│   ├── page.tsx                  # Main dashboard page
│   ├── layout.tsx                # Root layout
│   └── globals.css               # Global styles
├── lib/
│   └── xata.ts                   # Xata client configuration
├── .env.local                    # Environment variables (create this)
├── .env.local.example            # Example environment file
├── package.json
└── vercel.json                   # Vercel deployment config
```

## Deployment to Vercel

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:

```bash
npm i -g vercel
```

2. Login to Vercel:

```bash
vercel login
```

3. Deploy:

```bash
cd dashboard
vercel
```

4. Add environment variables in Vercel dashboard:
   - Go to your project settings
   - Navigate to Environment Variables
   - Add `XATA_API_KEY` and `XATA_DB_URL`

### Option 2: Deploy via GitHub

1. Push your code to GitHub
2. Import your repository in [Vercel](https://vercel.com)
3. Add environment variables:
   - `XATA_API_KEY`
   - `XATA_DB_URL`
4. Deploy!

## Environment Variables

| Variable       | Description                       | Required |
| -------------- | --------------------------------- | -------- |
| `XATA_API_KEY` | Your Xata API key                 | Yes      |
| `XATA_DB_URL`  | Your Xata database URL (full URL) | Yes      |

**Example `XATA_DB_URL`**: `https://workspace-id.us-east-1.xata.sh/db/database-name:main`

## Features Explained

### Search Functionality

- Search by cancer type name (e.g., "Leukemia", "Glioma")
- Search by confidence tier (e.g., "HIGH", "MEDIUM", "LOW")
- Real-time filtering as you type

### Table Columns

- **Rank**: Overall ranking position
- **Cancer Type**: Name of the cancer type
- **Overall Score**: Composite score (sorted descending)
- **Confidence**: Confidence tier badge (HIGH/MEDIUM/LOW)
- **Cell Lines**: Preview of cell lines (hover for full list)
- **SL Hits**: Number of synthetic lethality hits
- **Top Target**: Most dependent target gene for this cancer type

## Troubleshooting

### "Failed to fetch rankings" Error

1. Check that your `.env.local` file exists and has correct values
2. Verify your Xata API key is valid
3. Ensure your branch name is correct
4. Check that the `cancer_rankings` table exists in your Xata database

### Port 3003 Already in Use

If port 3003 is already in use, you can change it in `package.json`:

```json
"dev": "next dev -p 3004"
```

### Xata Connection Issues

Make sure:

- Your Xata database is accessible
- Your API key has the correct permissions
- The table name matches exactly: `cancer_rankings`

## Development

### Available Scripts

- `npm run dev` - Start development server on port 3003
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## License

Private project for StarX Therapeutics analysis.
