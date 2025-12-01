# Xata.io Import Guide for StarX Analysis Data

## Overview

You have 4 main data tables to import:

1. **Cancer Rankings** - Final integrated rankings by cancer type
2. **Individual Targets** - Per-target scores (STK17A, STK17B, MYLK4, TBK1, CLK4)
3. **Synthetic Lethality** - Mutation × target combinations
4. **Cell Line Data** - Individual cell line results (extracted from rankings)

---

## Recommended Approach: Direct CSV Import with Pre-Processing

**Yes, you can import CSVs directly into Xata.io**, but I recommend some pre-processing first to ensure optimal results.

---

## Table 1: Cancer Rankings

### Source File

- `data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv`

### Pre-Import Considerations

**Issues to Address:**

1. **Column Names**: Some have underscores (Xata prefers lowercase, but underscores are fine)
2. **Large Text Field**: `Cell_Lines` column contains very long comma-separated lists
3. **Data Types**: Mixed types (numbers, strings, booleans)

**Recommended Actions:**

1. ✅ **Column names are fine** - Xata will handle underscores
2. ⚠️ **Cell_Lines field**: Consider if you need this as a single text field or if you want to normalize it into a separate table
3. ✅ **Data types**: Xata will auto-detect, but you may want to verify:
   - `Rank`, `n_cell_lines`, `n_validated_cell_lines` → Integer
   - `overall_score`, `*_mean`, `*_score_normalized` → Float
   - `confidence_tier` → String
   - `has_sl_evidence` → Boolean

### Import Steps

1. In Xata.io, create a new table called `cancer_rankings`
2. Use "Import from CSV" feature
3. Upload `FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv`
4. Review auto-detected column types
5. Set primary key to `Rank` (or let Xata auto-generate an ID)

---

## Table 2: Individual Target Rankings

### Source Files

- `outputs/reports/STK17A_COMPLETE_RANKINGS_WITH_SCORES.csv`
- `outputs/reports/STK17B_COMPLETE_RANKINGS_WITH_SCORES.csv`
- `outputs/reports/MYLK4_COMPLETE_RANKINGS_WITH_SCORES.csv`
- `outputs/reports/TBK1_COMPLETE_RANKINGS_WITH_SCORES.csv`
- `outputs/reports/CLK4_COMPLETE_RANKINGS_WITH_SCORES.csv`

### Recommended Approach: Single Combined Table

**Option A: One Table with Target Column (Recommended)**

1. Combine all 5 CSVs into one file with a `target` column
2. Import as single `target_rankings` table
3. Add index on `target` column for filtering

**Option B: Separate Tables**

1. Import each CSV as separate table:
   - `stk17a_rankings`
   - `stk17b_rankings`
   - `mylk4_rankings`
   - `tbk1_rankings`
   - `clk4_rankings`

**I recommend Option A** for easier querying across targets.

### Pre-Processing Script Needed

Create a combined CSV:

```python
import pandas as pd

targets = ['STK17A', 'STK17B', 'MYLK4', 'TBK1', 'CLK4']
combined = []

for target in targets:
    df = pd.read_csv(f'outputs/reports/{target}_COMPLETE_RANKINGS_WITH_SCORES.csv')
    df['target'] = target
    combined.append(df)

final = pd.concat(combined, ignore_index=True)
final.to_csv('target_rankings_combined.csv', index=False)
```

---

## Table 3: Synthetic Lethality

### Source File

- `data/processed/true_synthetic_lethality_WITH_CELL_LINES.csv` (106 hits)
- OR `data/processed/synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv` (660 total combinations)

### Recommendation

- Use `true_synthetic_lethality_WITH_CELL_LINES.csv` for the main table (only significant hits)
- Optionally import `synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv` as a separate table for reference

### Pre-Import Considerations

**Issues:**

1. **Large text fields**: `mutant_cell_lines`, `wt_cell_lines`, `mutant_individual_scores`, `wt_individual_scores` contain comma-separated lists
2. **Column names**: Some are long but acceptable

**Data Types:**

- `n_mutant`, `n_wt`, `Rank` → Integer
- `mutant_mean`, `wt_mean`, `mean_diff`, `p_value` → Float
- `is_synthetic_lethal` → Boolean
- `mutation`, `target` → String

### Import Steps

1. Create table `synthetic_lethality`
2. Import CSV
3. Set composite index on `(mutation, target)` for unique lookups
4. Consider adding index on `is_synthetic_lethal` for filtering

---

## Table 4: Cell Line Data

### Challenge

The cell line data is currently embedded in the `Cell_Lines` column of rankings tables as comma-separated strings like:

```
"MV411 (CLK4), SKM1 (MYLK4), HDMYZ (CLK4), ..."
```

### Recommended Approach: Extract and Normalize

**Option A: Extract from Rankings (Recommended)**
Create a normalized cell line table by parsing the `Cell_Lines` column:

```python
import pandas as pd
import re

rankings = pd.read_csv('data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv')
cell_lines = []

for idx, row in rankings.iterrows():
    cancer_type = row['cancer_type']
    cell_line_str = str(row['Cell_Lines'])

    # Parse "CellLine (Target)" format
    matches = re.findall(r'([A-Z0-9_]+)\s*\(([A-Z0-9]+)\)', cell_line_str)

    for cell_line, target in matches:
        cell_lines.append({
            'cell_line': cell_line,
            'cancer_type': cancer_type,
            'most_dependent_target': target,
            'rank': row['Rank']
        })

df = pd.DataFrame(cell_lines)
df.to_csv('cell_lines_normalized.csv', index=False)
```

**Option B: Use Individual Target Files**
Extract from `Individual_Scores` columns in target ranking files (more detailed but more complex parsing).

### Import Steps

1. Create table `cell_lines`
2. Import normalized CSV
3. Add indexes on:
   - `cell_line` (for lookups)
   - `cancer_type` (for filtering)
   - `most_dependent_target` (for target-based queries)

---

## Xata.io Import Best Practices

### 1. Column Naming

- ✅ Current column names are fine (Xata supports underscores)
- ⚠️ Avoid special characters if possible
- ✅ Use lowercase for consistency (optional)

### 2. Data Types

- Xata will auto-detect, but verify:
  - Numbers → Integer or Float
  - True/False → Boolean
  - Dates → DateTime (if applicable)
  - Everything else → String

### 3. Large Text Fields

- Fields like `Cell_Lines`, `mutant_cell_lines` can be stored as text
- Consider if you need to query/search within these fields
- If yes, you may want to normalize into separate tables

### 4. Indexes

Add indexes on frequently queried columns:

- `cancer_type` in cancer_rankings
- `target` in target_rankings
- `(mutation, target)` in synthetic_lethality
- `cell_line` in cell_lines

### 5. Relationships (Optional)

If you want to link tables:

- `cancer_rankings.cancer_type` → `cell_lines.cancer_type`
- `synthetic_lethality.target` → `target_rankings.target`

---

## Quick Import Checklist

### Before Import

- [ ] Review CSV files for any obvious data issues
- [ ] Decide on table structure (combined vs. separate for targets)
- [ ] Create normalized cell_lines CSV if needed
- [ ] Backup original CSVs

### During Import

- [ ] Create tables in Xata.io
- [ ] Use "Import from CSV" for each table
- [ ] Review auto-detected column types
- [ ] Adjust data types if needed
- [ ] Set primary keys
- [ ] Add indexes on key columns

### After Import

- [ ] Verify row counts match CSV files
- [ ] Test queries on each table
- [ ] Set up relationships if needed
- [ ] Create views/queries for common use cases

---

## File Mapping Summary

| Table Name            | Source CSV                                               | Rows   | Notes                         |
| --------------------- | -------------------------------------------------------- | ------ | ----------------------------- |
| `cancer_rankings`     | `FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv` | 77     | Main rankings table           |
| `target_rankings`     | Combined from 5 target CSVs                              | ~385   | One row per target per cancer |
| `synthetic_lethality` | `true_synthetic_lethality_WITH_CELL_LINES.csv`           | 106    | Only significant hits         |
| `cell_lines`          | Extracted from rankings                                  | ~1,186 | Normalized cell line data     |

---

## Alternative: Single Table Approach

If you want to keep it simple, you could:

1. Import `FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv` as main table
2. Import `true_synthetic_lethality_WITH_CELL_LINES.csv` as secondary table
3. Skip individual target tables (data is in main rankings)
4. Parse cell lines on-the-fly when needed

This reduces complexity but may limit query flexibility.

---

## Need Help?

If you want me to:

1. Create the combined target_rankings CSV
2. Extract and normalize the cell_lines data
3. Clean/prepare any CSVs for optimal Xata import

Just let me know!
