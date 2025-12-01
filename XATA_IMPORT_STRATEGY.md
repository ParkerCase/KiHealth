# Xata.io Import Strategy: Best Approach

## ✅ Recommended: Hybrid Approach (Import First, Refine After)

**Best practice**: Import CSVs directly, then refine column types and add indexes.

---

## Why Import CSVs First?

### Advantages:

1. ✅ **Fast** - Xata auto-detects column types (usually correct)
2. ✅ **Less error-prone** - No manual typing of column names
3. ✅ **See data immediately** - Verify everything looks right
4. ✅ **Easy to adjust** - Change types/indexes after import
5. ✅ **Bulk import** - All rows imported at once

### Disadvantages:

1. ⚠️ May need to adjust some data types after import
2. ⚠️ Need to add indexes manually after import

---

## Why NOT Manual Column Creation First?

### Disadvantages:

1. ❌ **Time-consuming** - Need to define 20-40 columns per table manually
2. ❌ **Error-prone** - Easy to misspell column names
3. ❌ **No data preview** - Can't see if structure is right until you import
4. ❌ **More steps** - Create columns → Import data → Verify

### Advantages:

1. ✅ Full control over types from the start
2. ✅ Can set up relationships/indexes before import

---

## Recommended Workflow

### Step 1: Import CSVs Directly (5 minutes per table)

For each table:

1. Go to Xata.io dashboard
2. Create new table (e.g., `cancer_rankings`)
3. Click "Import from CSV"
4. Upload the CSV file
5. Review auto-detected column types
6. Click "Import"

**Xata will:**

- Auto-detect column names
- Auto-detect data types (usually correct)
- Import all rows

### Step 2: Verify and Refine (5 minutes per table)

After import, check:

1. **Data Types** - Verify these are correct:

   - Numbers → Integer or Float
   - True/False → Boolean
   - Text → String
   - Dates → DateTime (if applicable)

2. **Primary Key** - Set or verify:

   - `cancer_rankings`: Use `Rank` or auto-generated ID
   - `target_rankings`: Use composite or auto-generated ID
   - `synthetic_lethality`: Use composite `(mutation, target)` or auto-generated ID
   - `cell_lines`: Use `cell_line` or auto-generated ID

3. **Indexes** - Add these for faster queries:

   - `cancer_rankings`: Index on `cancer_type`
   - `target_rankings`: Index on `target`, `Cancer`
   - `synthetic_lethality`: Index on `target`, `mutation`, `is_synthetic_lethal`
   - `cell_lines`: Index on `cell_line`, `cancer_type`, `most_dependent_target`

4. **Column Names** - Adjust if needed (usually fine as-is)

### Step 3: Test Queries (2 minutes)

Run a few test queries to verify everything works:

```sql
-- Test cancer_rankings
SELECT * FROM cancer_rankings ORDER BY overall_score DESC LIMIT 5;

-- Test target_rankings
SELECT * FROM target_rankings WHERE target = 'STK17A' LIMIT 5;

-- Test synthetic_lethality
SELECT * FROM synthetic_lethality WHERE is_synthetic_lethal = true LIMIT 5;

-- Test cell_lines
SELECT * FROM cell_lines WHERE cancer_type = 'Acute Myeloid Leukemia' LIMIT 5;
```

---

## Expected Data Type Mappings

### cancer_rankings

| Column                   | Expected Type | Notes                 |
| ------------------------ | ------------- | --------------------- |
| `Rank`                   | Integer       | Primary key candidate |
| `cancer_type`            | String        | Add index             |
| `n_cell_lines`           | Integer       |                       |
| `overall_score`          | Float         |                       |
| `confidence_tier`        | String        |                       |
| `*_score_normalized`     | Float         | All score columns     |
| `n_validated_cell_lines` | Integer       |                       |
| `total_sl_hits`          | Integer       |                       |
| `has_sl_evidence`        | Boolean       |                       |
| `*_mean`                 | Float         | Target means          |
| `Cell_Lines`             | String        | Large text field      |

### target_rankings

| Column                  | Expected Type | Notes                  |
| ----------------------- | ------------- | ---------------------- |
| `Rank`                  | Integer       |                        |
| `Cancer`                | String        | Add index              |
| `target`                | String        | Add index (key column) |
| `*_mean`                | Float         | Per-target means       |
| `*_n`                   | Integer       | Sample sizes           |
| `*_std`                 | Float         | Standard deviations    |
| `*_min`, `*_max`        | Float         | Ranges                 |
| `*_range`               | String        | Text description       |
| `*_most_dependent_cell` | String        |                        |
| `Cell_Lines`            | String        | Large text field       |
| `Individual_Scores`     | String        | Large text field       |

### synthetic_lethality

| Column                                | Expected Type | Notes             |
| ------------------------------------- | ------------- | ----------------- |
| `mutation`                            | String        | Add index         |
| `target`                              | String        | Add index         |
| `n_mutant`, `n_wt`                    | Integer       |                   |
| `mutant_mean`, `wt_mean`, `mean_diff` | Float         |                   |
| `p_value`                             | Float         |                   |
| `is_synthetic_lethal`                 | Boolean       | Add index         |
| `Rank`                                | Integer       |                   |
| `*_cell_lines`                        | String        | Large text fields |
| `*_individual_scores`                 | String        | Large text fields |

### cell_lines

| Column                  | Expected Type | Notes                            |
| ----------------------- | ------------- | -------------------------------- |
| `cell_line`             | String        | Primary key candidate, add index |
| `cancer_type`           | String        | Add index                        |
| `cancer_rank`           | Integer       |                                  |
| `most_dependent_target` | String        | Add index                        |

---

## Common Issues and Fixes

### Issue 1: Column Type Wrong

**Problem**: Xata detects `n_cell_lines` as Float instead of Integer  
**Fix**: Go to column settings → Change type to Integer

### Issue 2: Boolean Detected as String

**Problem**: `has_sl_evidence` shows as "True"/"False" strings  
**Fix**: Change column type to Boolean, or use data transformation

### Issue 3: Large Text Fields

**Problem**: `Cell_Lines` column is very long  
**Fix**: Keep as String/Text type - Xata handles large text fields fine

### Issue 4: Missing Indexes

**Problem**: Queries are slow  
**Fix**: Add indexes on frequently queried columns (see Step 2)

---

## Time Estimate

| Step          | Time        | Notes                         |
| ------------- | ----------- | ----------------------------- |
| Import 4 CSVs | 20 min      | 5 min per table               |
| Verify types  | 10 min      | Quick check                   |
| Add indexes   | 5 min       | One-time setup                |
| Test queries  | 5 min       | Verify everything works       |
| **Total**     | **~40 min** | Much faster than manual setup |

---

## Alternative: Manual Setup (Not Recommended)

If you really want full control from the start:

1. Create table structure manually (30 min)
2. Define all columns and types (20 min)
3. Set up indexes (10 min)
4. Import data (10 min)
5. **Total: ~70 min** (vs 40 min with hybrid approach)

**Not worth it** unless you have very specific requirements.

---

## Final Recommendation

✅ **Import CSVs directly, then refine**

This gives you:

- Speed (40 min vs 70 min)
- Flexibility (easy to adjust after)
- Less error-prone (auto-detection handles most cases)
- Immediate feedback (see data right away)

You can always adjust column types, add indexes, and set up relationships after the initial import. Xata makes it easy to modify tables after creation.

---

## Quick Checklist

- [ ] Import `FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv` → `cancer_rankings`
- [ ] Import `target_rankings_combined.csv` → `target_rankings`
- [ ] Import `true_synthetic_lethality_WITH_CELL_LINES.csv` → `synthetic_lethality`
- [ ] Import `cell_lines_normalized.csv` → `cell_lines`
- [ ] Verify data types for each table
- [ ] Add indexes on key columns
- [ ] Test queries on each table
- [ ] Set up relationships (optional)

---

**Bottom line**: Import first, refine after. It's faster, easier, and you can always adjust things later!
