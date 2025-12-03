# 🚀 Quick Start Guide - Xata Database Setup

## Current Status: ✅ AHEAD OF SCHEDULE

### What's Already Done:

- ✅ DepMap data downloaded (7 files including Phase 2 mutation data!)
- ✅ Enhanced Xata schema created (includes copy number + mutations)
- ✅ Project structure set up
- ✅ Requirements installed

### What You Need: Xata Database Setup (15 minutes)

---

## Step 1: Run Validation (2 minutes)

This checks that everything is ready:

```bash
cd /Users/parkercase/starx-therapeutics-analysis/src/database
python migrate_v2.py --validate
```

**Expected Output:**

```
✅ CRISPRGeneEffect.csv (500 MB)
✅ CRISPRGeneDependency.csv (500 MB)
✅ Model.csv (5 MB)
✅ OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv (400 MB)
✅ OmicsCNGeneWGS.csv (100 MB)
✅ OmicsSomaticMutationsMatrixDamaging.csv (50 MB)
✅ OmicsSomaticMutationsMatrixHotspot.csv (20 MB)

Found 7/7 expected files
Schema includes 6 target genes: STK17A, MYLK4, TBK1, CLK4, XPO1, BTK
```

---

## Step 2: Setup Xata (10 minutes)

Run the interactive setup wizard:

```bash
python migrate_v2.py --setup
```

The wizard will guide you through:

1. Creating Xata account (if needed)
2. Creating database named `starx-therapeutics`
3. Getting your API key
4. Getting your database URL
5. Saving to `.env` file

**Pro Tip:** Have https://app.xata.io open in your browser

---

## Step 3: Create Tables (3 minutes)

Once setup is complete:

```bash
python migrate_v2.py --create
```

This creates 6 tables:

- `papers` (literature mining)
- `cancer_indications` (cancer rankings)
- `multi_target_dependencies` (cell line analysis)
- `combination_predictions` (drug combinations)
- `genetic_vulnerabilities` (mutation analysis)
- `depmap_cell_lines` (cell line metadata)

---

## Step 4: Verify (1 minute)

Check everything is working:

```bash
python migrate_v2.py --status
```

You should see all 6 tables listed.

---

## 🎉 You're Done!

### Your Database is Ready For:

1. **Phase 1 Analysis** (Days 1-3):

   - ✅ Multi-target dependency scoring
   - ✅ Expression correlation analysis
   - ✅ Copy number integration
   - ✅ Literature mining

2. **Phase 2 Analysis** (Days 4-7):
   - ✅ Genetic context (mutations already downloaded!)
   - ✅ Synthetic lethality predictions
   - ✅ Combination therapy recommendations

### You're Ahead Because:

1. **Downloaded mutation data early** (was planned for Phase 2)
2. **Schema includes mutation fields** (is_hotspot, is_damaging)
3. **Schema includes copy number** (copy_number_score fields)
4. **Extended to 6 targets** (original roadmap had only 4)

---

## Next Steps (Day 1 Afternoon)

### Task 1.3: Explore DepMap Data

Create `notebooks/01_explore_depmap.ipynb`:

```python
import pandas as pd
import numpy as np

# Load samples to understand structure
print("Loading DepMap data...")

# 1. Cell line metadata
model_df = pd.read_csv('../data/raw/depmap/Model.csv')
print(f"\n Model Data: {model_df.shape}")
print(f"Columns: {list(model_df.columns)}")
print(f"\nCancer Types: {model_df['OncotreeLineage'].value_counts().head(10)}")

# 2. Gene dependency (first 1000 rows to check structure)
dep_df = pd.read_csv('../data/raw/depmap/CRISPRGeneEffect.csv', nrows=1000)
print(f"\n Dependency Data: {dep_df.shape}")
print(f"Sample columns: {list(dep_df.columns[:10])}")

# 3. Expression data (first 1000 rows)
expr_df = pd.read_csv('../data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv', nrows=1000)
print(f"\n Expression Data: {expr_df.shape}")

# 4. Check for target genes
target_genes = ['STK17A', 'MYLK4', 'TBK1', 'CLK4', 'XPO1', 'BTK']
gene_columns = [col for col in dep_df.columns if any(gene in col for gene in target_genes)]
print(f"\n Target genes found: {len(gene_columns)}")
for col in gene_columns:
    print(f"   • {col}")
```

### Task 1.4: Load Initial Data to Xata

Create `src/database/load_cell_lines.py`:

```python
from xata.client import XataClient
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

client = XataClient(
    api_key=os.getenv('XATA_API_KEY'),
    db_url=os.getenv('XATA_DB_URL')
)

# Load Model.csv
print("Loading cell line metadata...")
model_df = pd.read_csv('../../data/raw/depmap/Model.csv')

# Prepare records for Xata
records = []
for _, row in model_df.iterrows():
    record = {
        'model_id': row['ModelID'],
        'cell_line_name': row['CellLineName'],
        'stripped_cell_line_name': row.get('StrippedCellLineName', ''),
        'oncotree_lineage': row.get('OncotreeLineage', ''),
        'oncotree_primary_disease': row.get('OncotreePrimaryDisease', ''),
        'oncotree_subtype': row.get('OncotreeSubtype', ''),
        'oncotree_code': row.get('OncotreeCode', ''),
        'age_category': row.get('AgeCategory', ''),
        'sex': row.get('Sex', ''),
        'primary_or_metastasis': row.get('PrimaryOrMetastasis', ''),
        'model_metadata': row.to_dict()
    }
    records.append(record)

# Batch insert to Xata
print(f"Inserting {len(records)} cell lines...")
client.records().bulk_insert('depmap_cell_lines', records)
print("✅ Done!")
```

---

## Troubleshooting

### "Connection failed" during setup

- Check your API key is correct
- Ensure database URL format: `https://WORKSPACE.xata.sh/db/starx-therapeutics`
- Try visiting https://app.xata.io to verify database exists

### "Table already exists"

- This is OK! The script will skip existing tables
- Use `--status` to see what's already created

### "DepMap files not found"

- Check they're in `/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/`
- Run `ls data/raw/depmap/` to verify

---

## Timeline Check

### Original Roadmap (Day 1):

- [x] Email responses (DONE)
- [x] Repo setup (DONE)
- [x] DepMap download (DONE + bonus files!)
- [ ] Xata setup (15 min remaining)
- [ ] Explore DepMap (1 hour)

### You're Ahead Because:

1. Downloaded Phase 2 mutation data already
2. Schema is more comprehensive than roadmap
3. Have copy number data for immediate use

**Estimated Time to Complete Day 1:** 2-3 hours remaining

---

## Contact

If you have issues:

1. Check `.env` file has correct values
2. Try `python migrate_v2.py --status` to diagnose
3. Visit https://xata.io/docs for Xata documentation
