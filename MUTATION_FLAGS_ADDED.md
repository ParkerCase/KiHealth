# ✅ Mutation Flags Added to Cancer Rankings

**Date**: December 2024  
**Status**: Complete

---

## What Was Added

Added **21 mutation flags** to the `cancer_rankings` table to enable complex queries like:

- "Show me cancers with NRAS mutations and high TBK1 dependency"
- "Which cancers have KRAS mutations?"
- "Find TP53-mutant cancers with high CLK4 dependency"

---

## 🧬 Mutations Tracked

| Mutation   | Cancers with Mutation | Percentage |
| ---------- | --------------------- | ---------- |
| **NRAS**   | 28                    | 36.4%      |
| **KRAS**   | 29                    | 37.7%      |
| **BRAF**   | 26                    | 33.8%      |
| **TP53**   | 61                    | 79.2%      |
| **PIK3CA** | 32                    | 41.6%      |
| **PTEN**   | 23                    | 29.9%      |
| **EGFR**   | 7                     | 9.1%       |
| **APC**    | 10                    | 13.0%      |
| **SMAD4**  | 17                    | 22.1%      |
| **CDKN2A** | 34                    | 44.2%      |
| **RB1**    | 17                    | 22.1%      |
| **NF1**    | 13                    | 16.9%      |
| **ARID1A** | 7                     | 9.1%       |
| **CTNNB1** | 15                    | 19.5%      |
| **IDH1**   | 8                     | 10.4%      |
| **IDH2**   | 0                     | 0.0%       |
| **FLT3**   | 1                     | 1.3%       |
| **NPM1**   | 0                     | 0.0%       |
| **DNMT3A** | 1                     | 1.3%       |
| **TET2**   | 1                     | 1.3%       |
| **ASXL1**  | 0                     | 0.0%       |

---

## 📁 Files Created

### New CSV File

- **`data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED_WITH_MUTATIONS.csv`**
  - Original 77 cancer rankings
  - **+ 21 mutation flag columns** (has_NRAS, has_KRAS, etc.)
  - Ready for Xata import

### Script

- **`add_mutation_flags_to_rankings.py`**
  - Processes DepMap mutation data
  - Maps mutations to cancer types
  - Adds boolean flags to rankings

---

## 🔄 Next Steps for Xata

### Option 1: Update Existing Table (Recommended)

1. Export current `cancer_rankings` table from Xata (backup)
2. Import new CSV: `FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED_WITH_MUTATIONS.csv`
3. Xata will add the new columns automatically
4. Verify all 21 mutation columns are boolean type

### Option 2: Manual Column Addition

1. Add 21 boolean columns to `cancer_rankings` table:
   - `has_NRAS`, `has_KRAS`, `has_BRAF`, etc.
2. Import CSV (will populate the columns)

---

## ✅ Dashboard Updates

The dashboard has been updated to:

- ✅ Accept mutation flags in the `CancerRanking` interface
- ✅ Filter cancer rankings by mutation
- ✅ Handle complex queries: "NRAS mutations + high TBK1 dependency"
- ✅ Update semantic search to extract mutations from queries
- ✅ Display mutation filter status in overview cards

---

## Example Queries Now Supported

1. **"Show me cancers with NRAS mutations and high TBK1 dependency"**

   - Filters to 28 cancers with NRAS mutations
   - Sorts by TBK1_mean (most negative first)

2. **"Which cancers have KRAS mutations?"**

   - Shows all 29 cancers with KRAS mutations

3. **"Find TP53-mutant cancers with high CLK4 dependency"**

   - Filters to 61 cancers with TP53 mutations
   - Sorts by CLK4_mean

4. **"Show me BRAF mutations"**
   - Shows all 26 cancers with BRAF mutations

---

## 📝 Data Source

- **Mutation Data**: `OmicsSomaticMutationsMatrixHotspot.csv` (DepMap 25Q3)
- **Mapping**: `Model.csv` (ModelID → OncotreePrimaryDisease)
- **Method**: Aggregated by cancer type (if any cell line in that cancer type has the mutation, flag = True)

---

## ⚠️ Important Notes

1. **Mutation flags are cancer-type level**: If ANY cell line in a cancer type has the mutation, the flag is `True`
2. **Hotspot mutations only**: Based on hotspot mutation matrix (not all mutations)
3. **Boolean flags**: Simple True/False (not mutation frequency or percentage)
4. **21 common mutations**: Focused on mutations relevant to synthetic lethality analysis

---

## 🚀 Ready for Import

The new CSV is ready to import into Xata. After import, the dashboard will automatically support mutation-based queries!
