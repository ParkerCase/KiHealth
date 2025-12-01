# 📥 Xata CSV Import Guide - Empty Tables

## Quick Import Instructions

I've created **empty CSV files with headers** that you can import directly into Xata to auto-create the table structure.

### Files Created:

- `scripts/papers.csv` - For the `papers` table
- `scripts/lincs_data.csv` - For the `lincs_data` table

---

## 🚀 How to Import

### Option 1: Import via Xata Dashboard (Recommended)

1. **Go to Xata Dashboard**

   - Navigate to your database
   - Click **"Add Table"** or **"Import Data"**

2. **Import `papers.csv`**

   - Click **"Import CSV"** or **"Upload File"**
   - Select `scripts/papers.csv`
   - Xata will auto-detect:
     - Table name: `papers` (or you can name it)
     - Column types from headers
   - Review the column types:
     - `pubmed_id` → **string** (set as **unique**)
     - `title` → **text**
     - `abstract` → **text**
     - `authors` → **text**
     - `journal` → **string**
     - `publication_date` → **datetime**
     - `cancer_types` → **multiple** (array)
     - `target_genes` → **multiple** (array)
     - `relevance_score` → **float**
     - `citation_count` → **int**
     - `last_updated` → **datetime**
     - `ai_insights` → **text** (optional)
     - `key_findings` → **text** (optional)
   - Click **"Import"**

3. **Import `lincs_data.csv`**

   - Repeat the process for `scripts/lincs_data.csv`
   - Table name: `lincs_data`
   - Column types:
     - `lincs_id` → **string** (set as **unique**)
     - `compound_name` → **string**
     - `target_gene` → **string**
     - `cell_line` → **string**
     - `efficacy_score` → **float**
     - `interaction_type` → **string**
     - `data_source` → **string**
     - `last_updated` → **datetime**

4. **Set Unique Constraints**
   - After import, go to each table's schema
   - Set `pubmed_id` as **unique** in `papers` table
   - Set `lincs_id` as **unique** in `lincs_data` table

---

### Option 2: Import via Xata CLI

```bash
# Install Xata CLI (if not already installed)
npm install -g @xata.io/cli

# Login to Xata
xata auth login

# Import papers table
xata import csv scripts/papers.csv --table papers --database your-db-name

# Import lincs_data table
xata import csv scripts/lincs_data.csv --table lincs_data --database your-db-name
```

---

## 📋 Column Type Mapping

### `papers` Table:

| Column             | Type     | Notes             |
| ------------------ | -------- | ----------------- |
| `pubmed_id`        | string   | **Set as UNIQUE** |
| `title`            | text     |                   |
| `abstract`         | text     |                   |
| `authors`          | text     |                   |
| `journal`          | string   |                   |
| `publication_date` | datetime |                   |
| `cancer_types`     | multiple | Array of strings  |
| `target_genes`     | multiple | Array of strings  |
| `relevance_score`  | float    | Default: 0.0      |
| `citation_count`   | int      | Default: 0        |
| `last_updated`     | datetime |                   |
| `ai_insights`      | text     | Optional          |
| `key_findings`     | text     | Optional          |

### `lincs_data` Table:

| Column             | Type     | Notes             |
| ------------------ | -------- | ----------------- |
| `lincs_id`         | string   | **Set as UNIQUE** |
| `compound_name`    | string   |                   |
| `target_gene`      | string   |                   |
| `cell_line`        | string   |                   |
| `efficacy_score`   | float    |                   |
| `interaction_type` | string   |                   |
| `data_source`      | string   |                   |
| `last_updated`     | datetime |                   |

---

## ✅ After Import

1. **Verify Tables Created**

   - Check that both tables exist in Xata
   - Verify all columns are present

2. **Set Unique Constraints**

   - `papers.pubmed_id` → **unique**
   - `lincs_data.lincs_id` → **unique**

3. **Test the PubMed Monitor**
   ```bash
   cd scripts
   npm run monitor
   ```

---

## 🎯 Why Empty CSVs?

- **Auto-detection**: Xata automatically detects column types from headers
- **No manual work**: No need to create columns one by one
- **Fast setup**: Import takes seconds instead of minutes
- **Error-free**: Headers match exactly what the scripts expect

---

## 📝 Notes

- The CSV files contain **only headers** (no data rows)
- This creates empty tables ready to receive data
- The PubMed monitor script will populate `papers` table
- LINCS integration (future) will populate `lincs_data` table

---

## 🐛 Troubleshooting

### Xata doesn't detect column types correctly

- Manually adjust column types in Xata dashboard after import
- Refer to the column type mapping above

### Import fails

- Make sure CSV files are in the correct format (UTF-8)
- Check that column names match exactly (case-sensitive)

### Unique constraint not set

- Go to table schema in Xata dashboard
- Click on `pubmed_id` or `lincs_id` column
- Enable "Unique" constraint

---

## ✅ Ready to Import!

1. Import `scripts/papers.csv` → Creates `papers` table
2. Import `scripts/lincs_data.csv` → Creates `lincs_data` table
3. Set unique constraints on `pubmed_id` and `lincs_id`
4. Run `npm run monitor` to test!
