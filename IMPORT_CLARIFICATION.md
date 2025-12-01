# Import Clarification: Separate Tables vs Combined

## ✅ YES - Import Them ALL SEPARATELY

These are **4 DIFFERENT tables** serving **DIFFERENT purposes**. They won't get jumbled because they're in separate tables!

---

## Table Structure Comparison

### 1. **cancer_rankings** (FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv)

- **Rows**: 77 (1 per cancer type)
- **Purpose**: Overall integrated composite scores
- **Key Columns**:
  - `overall_score` (composite ranking)
  - `depmap_score_normalized`, `expression_score_normalized`, etc. (component scores)
  - `STK17A_mean`, `STK17B_mean`, etc. (simple means for all 5 targets)
  - `confidence_tier`, `has_sl_evidence`
- **Use Case**: "What's the overall ranking of cancer types?"

### 2. **target_rankings** (target_rankings_combined.csv)

- **Rows**: 385 (77 cancers × 5 targets = 385 rows)
- **Purpose**: Detailed per-target statistics
- **Key Columns**:
  - `target` (STK17A, STK17B, MYLK4, TBK1, or CLK4)
  - `STK17A_mean`, `STK17A_n`, `STK17A_std`, `STK17A_min`, `STK17A_max`, `STK17A_range`
  - `STK17A_most_dependent_cell`, `Individual_Scores`
  - (Same pattern for all 5 targets, but only relevant columns populated per row)
- **Use Case**: "What are the detailed stats for STK17A in AML?"

### 3. **synthetic_lethality** (true_synthetic_lethality_WITH_CELL_LINES.csv)

- **Rows**: 106 (significant hits only)
- **Purpose**: Mutation × target combinations
- **Key Columns**: `mutation`, `target`, `mean_diff`, `p_value`, `is_synthetic_lethal`
- **Use Case**: "What mutations create synthetic lethality with CLK4?"

### 4. **cell_lines** (cell_lines_normalized.csv)

- **Rows**: 1,186 (one per cell line)
- **Purpose**: Individual cell line data
- **Key Columns**: `cell_line`, `cancer_type`, `most_dependent_target`
- **Use Case**: "Which cell lines are in AML and what's their most dependent target?"

---

## Why They're Different

### cancer_rankings vs target_rankings

**cancer_rankings** has:

- ✅ `overall_score` (composite ranking)
- ✅ Component scores (depmap, expression, mutation, etc.)
- ✅ Simple target means (just the mean, no details)
- ✅ 1 row per cancer

**target_rankings** has:

- ✅ Detailed target statistics (min, max, std, range)
- ✅ Most dependent cell line per target
- ✅ Individual cell line scores
- ✅ 5 rows per cancer (one per target)

**They complement each other:**

- Use `cancer_rankings` for overall rankings
- Use `target_rankings` for detailed per-target analysis

---

## Column Overlap (Won't Cause Issues)

There IS some overlap in column names:

- Both have: `Rank`, `STK17A_mean`, `STK17B_mean`, etc., `Cell_Lines`

**But this is FINE because:**

1. They're in **separate tables** - no conflict
2. The overlap is minimal (just basic means)
3. `cancer_rankings` has `cancer_type` while `target_rankings` has `Cancer` (different names)
4. `target_rankings` has the `target` column to distinguish which target each row is for

---

## ✅ All Files Ready to Import

| Table                   | File                                                                    | Status   | Rows  |
| ----------------------- | ----------------------------------------------------------------------- | -------- | ----- |
| **cancer_rankings**     | `data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv` | ✅ Ready | 77    |
| **target_rankings**     | `target_rankings_combined.csv`                                          | ✅ Ready | 385   |
| **synthetic_lethality** | `data/processed/true_synthetic_lethality_WITH_CELL_LINES.csv`           | ✅ Ready | 106   |
| **cell_lines**          | `cell_lines_normalized.csv`                                             | ✅ Ready | 1,186 |

---

## Recommended Import Order

1. **cancer_rankings** - Main table, import first
2. **target_rankings** - Detailed stats, import second
3. **synthetic_lethality** - SL interactions, import third
4. **cell_lines** - Individual lines, import fourth

---

## Example Queries After Import

### Query 1: "What's the overall ranking?"

```sql
SELECT * FROM cancer_rankings
ORDER BY overall_score DESC
LIMIT 10;
```

### Query 2: "What are STK17A stats for AML?"

```sql
SELECT * FROM target_rankings
WHERE Cancer = 'Acute Myeloid Leukemia'
AND target = 'STK17A';
```

### Query 3: "What mutations create SL with CLK4?"

```sql
SELECT * FROM synthetic_lethality
WHERE target = 'CLK4'
AND is_synthetic_lethal = true;
```

### Query 4: "What cell lines are in AML?"

```sql
SELECT * FROM cell_lines
WHERE cancer_type = 'Acute Myeloid Leukemia';
```

---

## Summary

✅ **Import all 4 tables separately** - they serve different purposes  
✅ **No column jumbling** - they're in separate tables  
✅ **All files ready** - pre-processed and ready to import  
✅ **Complementary data** - use together for comprehensive analysis

The `target_rankings_combined.csv` does NOT replace `cancer_rankings` - they work together!
