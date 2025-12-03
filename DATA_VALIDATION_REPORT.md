### Data Validation Report

Generated: 2025-10-30

## ✅ Passed checks

- p-values in `synthetic_lethality_results.csv` are within [0, 1]
- `mean_diff` equals `mutant_mean - wt_mean` (within tolerance)
- Dependency scores in `top_dependent_cell_lines.csv` are mostly negative; `combined_score` negative for 100% of rows
- Cancer type names consistent across `top_dependent_cell_lines.csv` and `cancer_type_rankings.csv` (58 overlaps)

## ⚠️ Warnings

- `cancer_type_rankings.csv`: Many top-ranked cancer types have n_cell_lines < 3 (min_cell_lines_ok = false). Interpret with caution.
- `MYLK4_dependency_mean` averages slightly positive overall, suggesting weak or absent dependency.

## ❌ Errors

- None detected in processed files.

## File Summaries

### 1) cancer_type_rankings.csv

- Cancer types ranked: 58
- Top 10 (by `combined_score_mean`, more negative = stronger dependency):
  - Extra Gonadal Germ Cell Tumor — -0.2241 (n=1)
  - Non-Seminomatous Germ Cell Tumor — -0.1615 (n=1)
  - Merkel Cell Carcinoma — -0.1320 (n=1)
  - Meningothelial Tumor — -0.1260 (n=1)
  - Endometrial Carcinoma — -0.1241 (n=5)
  - Bladder Squamous Cell Carcinoma — -0.1214 (n=1)
  - Breast Ductal Carcinoma In Situ — -0.1177 (n=1)
  - Ocular Melanoma — -0.1168 (n=2)
  - Gestational Trophoblastic Disease — -0.1166 (n=1)
  - Non-Hodgkin Lymphoma — -0.1123 (n=1)
- Missing values: `combined_score_std` has 28 missing; others 0
- Score ranges:
  - combined_score_mean: min -0.2241, max -0.0501, mean -0.0915
  - STK17A_dependency_mean: min -0.4580, max 0.0806, mean -0.1371
  - MYLK4_dependency_mean: min -0.1710, max 0.2162, mean 0.0044
  - TBK1_dependency_mean: min -0.5276, max 0.3384, mean -0.1046
  - CLK4_dependency_mean: min -0.4591, max 0.0633, mean -0.1287
- At least 3 cell lines per cancer type: NO (min_cell_lines_ok = false)

### 2) multi_target_dependencies.csv

- File not found in `data/processed/` (skipped checks)

### 3) synthetic_lethality_results.csv

- Mutation × target combinations tested: 44
- Significant hits (p < 0.10): 11
- Top 5 by |effect size| (mean_diff):
  - PTEN × CLK4: Δ=+0.1164, p=2.31e-07 (n_mutant=28, n_wt=2002)
  - EGFR × MYLK4: Δ=+0.0649, p=0.0162 (n_mutant=17, n_wt=2062)
  - HRAS × STK17A: Δ=+0.0643, p=0.0402 (n_mutant=17, n_wt=2060)
  - HRAS × TBK1: Δ=+0.0620, p=0.0525 (n_mutant=17, n_wt=2060)
  - STK11 × TBK1: Δ=+0.0587, p=0.2085 (n_mutant=8, n_wt=2054)
- Effect size sanity: mean_diff = mutant_mean - wt_mean (consistent)
- p-values in [0,1]: YES

## 🔍 Critical Validation vs Comprehensive Report

- Top 10 cancer types in report match `cancer_type_rankings.csv` values and order.
- Mutation analysis scope consistent (44 combinations expected and present).
- No discrepancies detected between files and the comprehensive report.

## 🧪 Additional Sanity Checks

- Dependency negativity (fraction negative):
  - STK17A_dependency: 88.6%
  - MYLK4_dependency: 52.7%
  - TBK1_dependency: 81.9%
  - CLK4_dependency: 84.0%
  - combined_score: 100.0%
- Unique cell lines (top_dependent_cell_lines.csv): 237
- Cancer type overlap between files: 58 shared names
