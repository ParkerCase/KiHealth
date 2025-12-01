# Comprehensive Verification Report - All 6 Issues

**Date:** Generated automatically  
**Purpose:** Verify all 6 issues raised regarding data accuracy and methodology

---

## Issue 1: STK17A AML Mean Discrepancy (-0.062 vs -0.082)

### Status: ✅ **NO DISCREPANCY FOUND**

**Findings:**

- Comprehensive Rankings: **-0.0623**
- Individual STK17A Rankings: **-0.0623**
- Raw Data (calculated directly): **-0.0623** (n=30 cell lines)

**Verification:**
All three sources match exactly. The mean is calculated from 30 AML cell lines:

- Most dependent: HEL9217 (-0.4100)
- Least dependent: SKM1 (0.3152)
- Mean: -0.0623

**Conclusion:** No discrepancy found. If you saw -0.082 elsewhere, it may be:

1. From a different dataset or subset
2. A rounding/display issue
3. From a different calculation method

**Recommendation:** If you can point to the source showing -0.082, we can investigate further.

---

## Issue 2: Synthetic Lethality Hit Count (106 vs 190 vs 75)

### Status: ✅ **CORRECT - 106 HITS**

**Findings:**

- `true_synthetic_lethality_WITH_CELL_LINES.csv`: **106 hits**
- `synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv`: **660 total combinations tested**
- Uncorrected significant (p < 0.10): **106 hits**

**FDR Correction:**

- FDR correction function is correctly implemented (Benjamini-Hochberg)
- Uses `min()` for proper step-up procedure
- Rejection uses `p_adjusted < alpha` (correct)
- **Note:** FDR-adjusted p-values are not in the CSV export, but the logic is correct in the script

**Clarification:**

- **660** = Total combinations tested (165 mutations × 4 targets)
- **106** = True synthetic lethality hits (mean_diff < 0 AND p < 0.10, uncorrected)
- **322** = All combinations with negative mean_diff (regardless of significance)

**Conclusion:**

- ✅ 106 is the correct count for true synthetic lethality hits
- ✅ FDR correction logic is correct (would reduce, not increase, the count)
- ⚠️ If you saw 190 or 75, those may be:
  - 190: Possibly all negative mean_diff combinations (322) filtered somehow
  - 75: Possibly FDR-corrected hits (not exported in current CSV)

**Recommendation:** If you need FDR-corrected counts, we can add them to the export.

---

## Issue 3: Terminology Drift (106 vs 243 total hits)

### Status: ✅ **CLARIFIED**

**Findings:**

- **660** = Total combinations tested (165 mutations × 4 targets)
- **106** = True synthetic lethality hits (mean_diff < 0 AND p < 0.10)
- **322** = All combinations with negative mean_diff
- **243** = This number appears in `total_sl_hits` column in comprehensive rankings

**Clarification:**

- **106** = True positives (synthetic lethality hits)
- **243** = Total synthetic lethality hits across all cancer types (aggregated)
- **660** = Total tested combinations

**Conclusion:**

- ✅ 106 = True synthetic lethality hits (correct)
- ✅ 243 = Total SL hits aggregated by cancer type (different metric)
- ✅ Terminology is consistent within each context

**Recommendation:** The `total_sl_hits` column (243) represents a different aggregation level (cancer-type level) than the 106 mutation-target pairs.

---

## Issue 4: Effect Size Sign Conventions

### Status: ✅ **SIGN PRESERVED CORRECTLY**

**Findings:**

- mean_diff sign distribution:
  - Negative (SL): 322 combinations
  - Positive: 338 combinations
  - Zero: 0 combinations

**Verification:**

- ✅ No absolute value columns found
- ✅ Sign is preserved in all exports
- ✅ mean_diff < 0 = Synthetic lethality (mutants more dependent)
- ✅ mean_diff > 0 = Not synthetic lethality

**Sample values:**

- PIK3CD × STK17A: -0.0064 (NEGATIVE = SL)
- PIK3CD × MYLK4: 0.0830 (POSITIVE = not SL)
- MTOR × TBK1: -0.0818 (NEGATIVE = SL)

**Conclusion:**

- ✅ Sign conventions are correct
- ✅ Negative values correctly indicate synthetic lethality
- ✅ No absolute values are taken that would lose direction

---

## Issue 5: Validation Overlap Percentage (12.4%)

### Status: ⚠️ **NEEDS INVESTIGATION**

**Findings:**

- DepMap total cell lines: **2,132**
- IC50 cell lines found: **49** (from Tulasi data)
- Overlap: **12 cell lines**
- Calculated percent: **0.56%** (12/2132)

**Issue:**

- Expected: **12.4%**
- Calculated: **0.56%**

**Possible Explanations:**

1. **Different denominator:** 12.4% might be calculated as 12/97 (if only considering a subset of DepMap lines)
2. **Different cell line matching:** Cell line names might not match exactly (case sensitivity, naming conventions)
3. **Different data source:** The 12.4% might refer to a different experimental dataset

**Investigation Needed:**

- Check if cell line names match exactly (case, formatting)
- Verify which DepMap subset was used for the 12.4% calculation
- Check if other experimental data sources (beyond IC50) were included

**Recommendation:**

- Need to verify the exact cell line matching logic used for the 12.4% calculation
- Check if the denominator should be a subset of DepMap (e.g., only cancer cell lines, not all lines)

---

## Issue 6: Composite Score Normalization

### Status: ✅ **CORRECT - NORMALIZATION BEFORE WEIGHTING**

**Findings:**

**Score Ranges (all normalized 0-1):**

- `overall_score`: [0.1600, 0.4914] ✅
- `depmap_score_normalized`: [0.0000, 1.0000] ✅
- `expression_score_normalized`: [0.5000, 0.5000] ✅
- `mutation_context_score`: [0.3000, 0.7000] ✅
- `copy_number_score`: [0.0000, 1.0000] ✅
- `literature_score_normalized`: [0.0000, 0.0500] ✅
- `experimental_validation_score`: [0.0000, 0.8220] ✅

**Normalization Order:**

- ✅ Normalization happens **BEFORE** weighting (correct)
- ✅ All component scores are normalized to 0-1 range
- ✅ Overall score is calculated as weighted sum of normalized scores

**Sample Calculation (AML, first row):**

```
depmap_score_normalized: 0.3642
expression_score_normalized: 0.5000
mutation_context_score: 0.5000
copy_number_score: 1.0000
literature_score_normalized: 0.0000
experimental_validation_score: 0.8220

overall_score: 0.4914
```

**Weights (from script):**

- Dependency: 0.30
- Expression: 0.20
- Mutation: 0.20
- Copy Number: 0.10
- Literature: 0.10
- Experimental: 0.10

**Conclusion:**

- ✅ Normalization order is correct (normalize → weight)
- ✅ All scores are in 0-1 range
- ✅ Overall score calculation is correct

---

## Summary

| Issue               | Status                 | Notes                                     |
| ------------------- | ---------------------- | ----------------------------------------- |
| 1. STK17A AML Mean  | ✅ No Discrepancy      | All sources show -0.0623                  |
| 2. SL Hit Count     | ✅ Correct             | 106 hits is correct; FDR logic verified   |
| 3. Terminology      | ✅ Clarified           | 106 = hits, 243 = aggregated, 660 = total |
| 4. Sign Conventions | ✅ Correct             | Signs preserved, negative = SL            |
| 5. Overlap %        | ⚠️ Needs Investigation | Got 0.56% vs expected 12.4%               |
| 6. Normalization    | ✅ Correct             | Normalize before weighting                |

---

## Recommendations

1. **Issue 1:** If you have a source showing -0.082, please share it for investigation.

2. **Issue 2:** Consider adding FDR-corrected p-values to CSV exports for transparency.

3. **Issue 3:** Consider renaming `total_sl_hits` to `aggregated_sl_hits_by_cancer` for clarity.

4. **Issue 5:** Need to verify:

   - Exact cell line matching logic
   - Which DepMap subset was used
   - If other experimental data sources were included

5. **Issue 6:** No changes needed - normalization is correct.

---

**Generated by:** `verify_all_issues.py`  
**Date:** Auto-generated
