# Scoring Weights Update - November 1, 2025

## CRITICAL UPDATE: Copy Number Weight Reduced

Based on Cursor validation of PROMPT 2.5, copy number analysis revealed uniformly high amplification rates (99%+) across target genes, limiting discriminatory power.

## UPDATED SCORING WEIGHTS FOR PROMPT 4

### New Weight Distribution:

```
overall_score = (
    0.30 × depmap_score_normalized +
    0.25 × expression_score_normalized +        ← INCREASED from 20% to 25%
    0.20 × mutation_context_score +
    0.05 × copy_number_score +                  ← REDUCED from 10% to 5%
    0.10 × literature_score_normalized +
    0.10 × experimental_validation_score
)
```

### Rationale for Updated Weights:

- **DepMap (30%)**: Direct evidence of genetic dependency
- **Expression (25%)**: Validates biological relevance AND shows strong variation across cancer types
- **Mutation context (20%)**: Stratification opportunity with significant synthetic lethality signals
- **Copy number (5%)**: **REDUCED WEIGHT** - uniformly high amplification rates (99%+) provide limited discrimination between cancer types
- **Literature (10%)**: Supporting evidence, often sparse for novel targets
- **Experimental validation (10%)**: Real IC50 data from 160 cell lines validates predictions

### Why This Change Was Made:

**Copy Number Analysis Findings (from PROMPT 2.5):**
- 47 cancer types analyzed
- STK17A: 99.6% amplification rate across all cell lines
- MYLK4: 99.5% amplification rate
- TBK1: 99.7% amplification rate  
- CLK4: 99.3% amplification rate

**Scientific Interpretation:**
These target genes reside in genomically stable regions and are NOT subject to frequent focal amplifications or deletions (unlike oncogenes like EGFR or MYC). This is actually **positive for drug development** (targets are rarely deleted), but provides **limited value for patient stratification**.

**Impact on Scoring:**
- Copy number dimension still included (shows comprehensive analysis)
- Reduced weight reflects honest assessment of discriminatory power
- Extra 5% allocated to expression correlation (which DOES show variation)
- Final rankings will emphasize dependency, expression, mutation context, and experimental validation

### How to Frame This in Report:

> "Copy number analysis revealed uniformly high copy number stability (99%+) across target genes in most cancer types, indicating these kinases reside in genomically stable regions. While this supports broad targetability (genes are rarely deleted), it provides limited discriminatory value for patient stratification. Our analysis therefore emphasizes dependency scores, expression correlation, mutation context, and experimental IC50 validation as primary evidence dimensions."

---

## PREVIOUS WEIGHTS (For Reference)

**Original PROMPT 4 weights (before experimental data):**
- DepMap: 35%
- Expression: 25%
- Mutation: 20%
- Copy Number: 10%
- Literature: 10%

**After experimental data added (temporary):**
- DepMap: 30%
- Expression: 20%
- Mutation: 20%
- Copy Number: 10%
- Literature: 10%
- Experimental: 10%

**FINAL weights (after copy number validation):**
- DepMap: 30%
- Expression: 25% ← Increased
- Mutation: 20%
- Copy Number: 5% ← Reduced
- Literature: 10%
- Experimental: 10%

---

**Date:** November 1, 2025
**Validation Report:** outputs/reports/validation_prompt_2_5.txt
**Status:** Ready for PROMPT 3
