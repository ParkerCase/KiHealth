# 🧬 COMPREHENSIVE SYNTHETIC LETHALITY ANALYSIS - COMPLETE RESULTS

**Date**: November 7, 2025  
**Analysis**: All mutations × 4 targets (STK17A, MYLK4, TBK1, CLK4)  
**Status**: ✅ COMPLETE

---

## 📊 EXECUTIVE SUMMARY

### What Changed

**Previous Analysis:**

- Tested: 11 mutations × 4 targets = **44 combinations**
- Found: **1 synthetic lethality hit** (NRAS × CLK4)

**Comprehensive Analysis:**

- Tested: **165 mutations** × 4 targets = **660 combinations**
- Found: **243 synthetic lethality hits** (uncorrected)
- Found: **190 synthetic lethality hits** (FDR corrected)
- Found: **75 synthetic lethality hits** (Bonferroni corrected)

### Key Findings

1. **Massive expansion**: Found 243 potential synthetic lethality relationships (vs 1 previously)
2. **All targets have hits**: Each of the 4 targets shows multiple synthetic lethality patterns
3. **Sample size considerations**: Many hits have small mutant sample sizes (n=3-4), requiring validation

---

## RESULTS BY TARGET GENE

### STK17A: 53 Synthetic Lethality Hits

**Top 5 Hits:**

1. **CDC25A × STK17A**: Δ = -0.0443, p = 6.5e-209, n_mutant = 3
2. **SDHA × STK17A**: Δ = -0.0420, p = 8.6e-186, n_mutant = 4
3. **IL37 × STK17A**: Δ = -0.0408, p = 6.4e-04, n_mutant = 3
4. **RIT1 × STK17A**: Δ = -0.0393, p = 4.2e-172, n_mutant = 3
5. **TSC2 × STK17A**: Δ = -0.0368, p = 4.1e-04, n_mutant = 4

**Notable patterns:**

- Strongest effect sizes observed
- Many hits with very small sample sizes (n=3-4)
- Includes known cancer genes (RIT1, TSC2, BLM, BRCA1)

### MYLK4: 72 Synthetic Lethality Hits

**Top 5 Hits:**

1. **RIT1 × MYLK4**: Δ = -0.0153, p = 5.4e-171, n_mutant = 3
2. **NSD2 × MYLK4**: Δ = -0.0147, p = 2.9e-04, n_mutant = 3
3. **DST × MYLK4**: Δ = -0.0143, p = 1.2e-02, n_mutant = 3
4. **STIL × MYLK4**: Δ = -0.0130, p = 4.4e-06, n_mutant = 6
5. **RAB40C × MYLK4**: Δ = -0.0128, p = 1.8e-06, n_mutant = 3

**Notable patterns:**

- Most hits of any target (72)
- Generally smaller effect sizes than STK17A
- STIL has larger sample size (n=6)

### TBK1: 46 Synthetic Lethality Hits

**Top 5 Hits:**

1. **ARID5B × TBK1**: Δ = -0.0371, p = 8.2e-04, n_mutant = 3
2. **PPP2R2B × TBK1**: Δ = -0.0366, p = 1.3e-27, n_mutant = 3
3. **SPOP × TBK1**: Δ = -0.0362, p = 1.4e-127, n_mutant = 3
4. **AP3B1 × TBK1**: Δ = -0.0353, p = 2.4e-122, n_mutant = 3
5. **ZFAND1 × TBK1**: Δ = -0.0352, p = 6.5e-05, n_mutant = 4

**Notable patterns:**

- Strong effect sizes (similar to STK17A)
- Includes known cancer genes (SPOP, ARID5B)
- Many hits with small sample sizes

### CLK4: 72 Synthetic Lethality Hits

**Top 5 Hits:**

1. **ZNF14 × CLK4**: Δ = -0.0392, p = 2.2e-03, n_mutant = 3
2. **ACTR10 × CLK4**: Δ = -0.0392, p = 2.2e-03, n_mutant = 3
3. **GIGYF2 × CLK4**: Δ = -0.0388, p = 4.3e-04, n_mutant = 4
4. **DNAJA4 × CLK4**: Δ = -0.0382, p = 1.6e-02, n_mutant = 3
5. **MYBPC3 × CLK4**: Δ = -0.0382, p = 1.5e-02, n_mutant = 3

**Notable patterns:**

- Tied with MYLK4 for most hits (72)
- Includes known cancer genes (BRCA1, MAX)
- Previously identified NRAS × CLK4 still present (ranked lower)

---

## ⚠️ IMPORTANT CAVEATS

### 1. Sample Size Limitations

**Many hits have very small mutant sample sizes (n=3-4):**

- Small samples can produce spurious results
- High variance in small groups
- Need experimental validation

**Recommendation**: Prioritize hits with:

- n_mutant ≥ 10 (more reliable)
- Larger effect sizes (|Δ| > 0.02)
- Known cancer relevance

### 2. Multiple Testing

**Statistical corrections applied:**

- **Uncorrected**: 243 hits (p < 0.10)
- **FDR corrected**: 190 hits (q < 0.10) - **Recommended for discovery**
- **Bonferroni corrected**: 75 hits (p < 0.10) - **Most conservative**

**Recommendation**: Use FDR-corrected results for prioritizing candidates

### 3. Biological Interpretation

**Not all hits are equally actionable:**

- Some mutations are very rare (n=3-4 mutants)
- Clinical relevance depends on mutation frequency in patient populations
- Need pathway/mechanism validation

---

## 📈 COMPARISON: OLD vs NEW ANALYSIS

| Metric                    | Previous (11 mutations) | Comprehensive (165 mutations) | Change                |
| ------------------------- | ----------------------- | ----------------------------- | --------------------- |
| **Combinations tested**   | 44                      | 660                           | **15× more**          |
| **SL hits (uncorrected)** | 1                       | 243                           | **243× more**         |
| **SL hits (FDR)**         | 1                       | 190                           | **190× more**         |
| **SL hits (Bonferroni)**  | 0                       | 75                            | **75 new hits**       |
| **Targets with hits**     | 1 (CLK4)                | 4 (all)                       | **Complete coverage** |

---

## PRIORITIZATION RECOMMENDATIONS

### Tier 1: High Confidence (Validate First)

- **Large sample sizes** (n_mutant ≥ 10)
- **FDR-corrected significance** (q < 0.10)
- **Known cancer genes** (e.g., RIT1, TSC2, SPOP, BRCA1)
- **Strong effect sizes** (|Δ| > 0.03)

### Tier 2: Medium Confidence (Follow-up)

- **Moderate sample sizes** (n_mutant = 5-9)
- **FDR-corrected significance**
- **Moderate effect sizes** (|Δ| = 0.02-0.03)

### Tier 3: Low Confidence (Exploratory)

- **Small sample sizes** (n_mutant = 3-4)
- **Uncorrected significance only**
- **Requires experimental validation**

---

## 📁 OUTPUT FILES

1. **`comprehensive_synthetic_lethality_all_mutations.csv`**

   - All 660 combinations tested
   - Includes all statistics and corrections

2. **`true_synthetic_lethality_all_mutations.csv`**

   - 243 true SL hits (uncorrected p < 0.10, mean_diff < 0)
   - Sorted by effect size

3. **`true_synthetic_lethality_fdr_corrected.csv`**
   - 190 true SL hits (FDR corrected, q < 0.10)
   - **Recommended for prioritization**

---

## 🔬 NEXT STEPS

1. **Validate top hits experimentally**

   - Focus on Tier 1 candidates
   - Test in relevant cell lines

2. **Pathway analysis**

   - Group hits by biological pathways
   - Identify common mechanisms

3. **Clinical relevance assessment**

   - Check mutation frequencies in patient populations
   - Prioritize by addressable patient population

4. **Literature review**
   - Search for known relationships
   - Identify novel mechanisms

---

## 📊 STATISTICAL METHODS

### Analysis Parameters

- **Minimum mutants**: 3
- **Minimum wild-type**: 10
- **Significance threshold**: p < 0.10 (uncorrected)
- **Statistical test**: Welch's t-test (unequal variances)
- **Multiple testing correction**: FDR (Benjamini-Hochberg) and Bonferroni

### Synthetic Lethality Definition

- **True SL**: mean_diff < 0 (mutants more dependent) AND p < 0.10
- **Effect size**: mean_diff = mutant_mean - wt_mean
- **Negative values**: Mutants need target more (therapeutic opportunity)

---

_Generated by: `comprehensive_synthetic_lethality_all_mutations.py`_  
_For questions or follow-up analysis, refer to the script and output files._
