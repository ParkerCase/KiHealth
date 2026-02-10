# PubMed + LINCS Monitoring System

Automated system to monitor PubMed and LINCS for new research relevant to StarX Therapeutics targets.

## Setup

### 1. Install Dependencies

```bash
cd scripts
npm install
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Xata credentials:

```bash
cp .env.example .env
# Edit .env with your Xata API key and database URL
```

### 3. Create Xata Tables

Before running, create the `papers` table in Xata:

1. Go to Xata dashboard
2. Select your database
3. Click "Add Table"
4. Name it `papers`
5. Add columns as specified in `../XATA_TABLES_SCHEMA.md`

## Usage

### Run Manually

```bash
npm run monitor
```

### Schedule with GitHub Actions

See `.github/workflows/pubmed-monitor.yml` (to be created in next step)

## What It Does

1. **Searches PubMed** for:

   - Target genes: STK17A, MYLK4, TBK1, CLK4
   - Top 20 cancer types
   - Combination queries (gene + cancer)

2. **Extracts Data**:

   - PubMed ID, title, abstract
   - Authors, journal, publication date
   - Mentioned cancer types and target genes

3. **Stores in Xata**:

   - Creates new records for new articles
   - Updates existing records
   - Avoids duplicates

4. **Logs Everything**:
   - Saves logs to `../logs/pubmed-YYYY-MM-DD.log`

## Output

- **Logs**: `../logs/pubmed-YYYY-MM-DD.log`
- **Xata Table**: `papers` (with all article data)

## Next Steps

- PROMPT 2: Add LINCS integration
- PROMPT 3: Add Claude AI analysis for relevance scoring
- PROMPT 4: Set up GitHub Actions for daily automation
