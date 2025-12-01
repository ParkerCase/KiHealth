# 📋 Xata Update Required

## ✅ What's Already in Xata (Complete)

You currently have **4 tables** imported:

1. **`cancer_rankings`** - 77 cancer types with all scores
2. **`target_rankings`** - 385 rows (77 cancers × 5 targets)
3. **`synthetic_lethality`** - 106 true SL hits
4. **`cell_lines`** - 1,186 cell lines

---

## 🔄 What Needs to Be Added to Xata

### **NEW FILE TO IMPORT:**

**`FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED_WITH_MUTATIONS.csv`**

This is the **updated version** of your `cancer_rankings` table with **21 new mutation flag columns**:

- `has_NRAS`, `has_KRAS`, `has_BRAF`, `has_TP53`, `has_PIK3CA`, `has_PTEN`
- `has_EGFR`, `has_APC`, `has_SMAD4`, `has_CDKN2A`, `has_RB1`, `has_NF1`
- `has_ARID1A`, `has_CTNNB1`, `has_IDH1`, `has_IDH2`, `has_FLT3`
- `has_NPM1`, `has_DNMT3A`, `has_TET2`, `has_ASXL1`

---

## 📝 How to Update Xata

### Option 1: Replace Existing Table (Easiest)

1. **Backup current data** (optional but recommended)

   - Export current `cancer_rankings` table from Xata

2. **Delete old table** (or rename it to `cancer_rankings_old`)

3. **Import new CSV**

   - File: `data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED_WITH_MUTATIONS.csv`
   - Table name: `cancer_rankings`
   - Xata will auto-detect column types (mutation flags will be boolean)

4. **Verify**
   - Check that all 41 columns are present (20 original + 21 mutation flags)
   - Verify mutation columns are boolean type

### Option 2: Add Columns Manually (Safer)

1. **Add 21 boolean columns** to existing `cancer_rankings` table:

   - Go to Schema Editor in Xata
   - Add each column: `has_NRAS` (boolean), `has_KRAS` (boolean), etc.

2. **Import CSV** (will populate the new columns)

---

## ✅ What This Enables

After updating Xata, the dashboard will support:

✅ **"Show me cancers with NRAS mutations and high TBK1 dependency"**  
✅ **"Which cancers have KRAS mutations?"**  
✅ **"Find TP53-mutant cancers with high CLK4 dependency"**  
✅ **"Show me BRAF mutations"**

---

## 📊 Summary

- **Current Xata tables**: 4 tables ✅
- **New data needed**: 1 updated CSV file (with mutation flags)
- **Dashboard code**: Already updated to handle mutations ✅
- **Ready to use**: Yes, after Xata import ✅

---

## 🎯 No External Data Sources Needed

All mutation data comes from **DepMap** (already in your project):

- `OmicsSomaticMutationsMatrixHotspot.csv` - mutation data
- `Model.csv` - cancer type mapping

**No external APIs or additional data sources required!**
