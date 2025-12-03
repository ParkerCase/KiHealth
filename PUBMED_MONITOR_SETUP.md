# ✅ PubMed Monitoring System - Setup Complete

## 📋 What Was Created

### 1. **Node.js Script** (`scripts/pubmed-monitor.js`)

- ✅ PubMed API integration (E-utilities)
- ✅ Searches for 4 target genes + 20 cancer types
- ✅ Extracts article metadata (title, abstract, authors, etc.)
- ✅ Rate limiting (3 requests/second)
- ✅ Retry logic (3 attempts)
- ✅ Duplicate detection
- ✅ Comprehensive logging

### 2. **Dependencies** (`scripts/package.json`)

- ✅ `@xata.io/client` - Xata database client
- ✅ `axios` - HTTP requests
- ✅ `dotenv` - Environment variables
- ✅ `xml2js` - XML parsing

### 3. **Documentation**

- ✅ `XATA_TABLES_SCHEMA.md` - Table schema definitions
- ✅ `scripts/README.md` - Usage instructions

---

## 🚀 Next Steps (Before Running)

### Step 1: Create Xata Tables

**You need to create the `papers` table in Xata first!**

1. Go to your Xata dashboard
2. Select your database
3. Click **"Add Table"**
4. Name it: `papers`
5. Add these columns:

| Column Name        | Type     | Options                |
| ------------------ | -------- | ---------------------- |
| `pubmed_id`        | string   | **Unique**             |
| `title`            | text     |                        |
| `abstract`         | text     |                        |
| `authors`          | text     |                        |
| `journal`          | string   |                        |
| `publication_date` | datetime |                        |
| `cancer_types`     | multiple |                        |
| `target_genes`     | multiple |                        |
| `relevance_score`  | float    |                        |
| `citation_count`   | int      |                        |
| `last_updated`     | datetime |                        |
| `ai_insights`      | text     | (optional, for future) |
| `key_findings`     | text     | (optional, for future) |

**See `XATA_TABLES_SCHEMA.md` for detailed schema.**

### Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env` in the `scripts/` directory:

   ```bash
   cd scripts
   cp .env.example .env
   ```

2. Edit `.env` and add your Xata credentials:
   ```env
   XATA_API_KEY=your_xata_api_key_here
   XATA_DB_URL=https://your-workspace.region.xata.sh/db/your-db-name:main
   ```

### Step 3: Test Run

```bash
cd scripts
npm run monitor
```

This will:

- Search PubMed for articles from the last 30 days
- Extract metadata
- Store in Xata `papers` table
- Log everything to `../logs/pubmed-YYYY-MM-DD.log`

---

## What It Searches

### Target Genes (4):

- STK17A
- MYLK4
- TBK1
- CLK4

### Cancer Types (20):

- Acute Myeloid Leukemia
- Diffuse Glioma
- Extra Gonadal Germ Cell Tumor
- Melanoma
- Esophagogastric Adenocarcinoma
- Non-Small Cell Lung Cancer
- Mature T and NK Neoplasms
- Colorectal Adenocarcinoma
- Endometrial Carcinoma
- Head and Neck Squamous Cell Carcinoma
- Leiomyosarcoma
- Bladder Urothelial Carcinoma
- Ovarian Epithelial Tumor
- Pancreatic Adenocarcinoma
- Ocular Melanoma
- B-Cell Acute Lymphoblastic Leukemia
- Mature B-Cell Neoplasms
- Myeloproliferative Neoplasms
- Lung Neuroendocrine Tumor
- Osteosarcoma

### Combination Queries:

- Each target gene × Top 5 cancer types = 20 additional queries

**Total: ~44 queries per run**

---

## 🔍 Features

### ✅ Rate Limiting

- Max 3 requests/second (PubMed requirement)
- Automatic delays between requests

### ✅ Error Handling

- Retries failed requests (3 attempts)
- Continues on individual article failures
- Comprehensive error logging

### ✅ Duplicate Prevention

- Checks for existing articles by `pubmed_id`
- Updates existing records instead of creating duplicates

### ✅ Data Extraction

- Automatically extracts mentioned cancer types
- Automatically extracts mentioned target genes
- Parses publication dates
- Extracts author lists

### ✅ Logging

- All operations logged to `logs/pubmed-YYYY-MM-DD.log`
- Console output for real-time monitoring

---

## 📈 Expected Output

After running, you'll have:

1. **Xata `papers` table** populated with:

   - New articles from last 30 days
   - Metadata (title, abstract, authors, etc.)
   - Extracted cancer types and target genes
   - Ready for AI analysis (relevance_score = 0.0 initially)

2. **Log file** (`logs/pubmed-YYYY-MM-DD.log`) with:
   - All search queries executed
   - Number of articles found per query
   - New vs. updated articles
   - Any errors encountered

---

## Next Steps (Future Prompts)

- **PROMPT 2**: Add LINCS integration
- **PROMPT 3**: Add Claude AI for relevance scoring
- **PROMPT 4**: Set up GitHub Actions for daily automation

---

## ⚠️ Important Notes

1. **Xata tables must be created first** - The script will fail if the `papers` table doesn't exist
2. **Environment variables required** - Make sure `.env` is configured
3. **Rate limits** - PubMed allows 3 requests/second (script handles this automatically)
4. **Date range** - Currently set to last 30 days (configurable in script)

---

## 🐛 Troubleshooting

### Error: "Table papers not found"

→ Create the `papers` table in Xata first (see Step 1)

### Error: "XATA_API_KEY is not set"

→ Check your `.env` file in the `scripts/` directory

### Error: "Rate limit exceeded"

→ The script should handle this automatically, but if it persists, increase delays in the script

### No articles found

→ This is normal if there are no new articles in the last 30 days. Check the log file for details.

---

## ✅ Ready to Run!

Once you've:

1. ✅ Created the `papers` table in Xata
2. ✅ Configured `.env` with your Xata credentials
3. ✅ Installed dependencies (`npm install`)

You can run:

```bash
cd scripts
npm run monitor
```

The script will search PubMed and populate your Xata database! 🚀
