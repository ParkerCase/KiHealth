# Expression Correlation Analysis - Created ✅

**Date**: October 29, 2025  
**Notebook**: `notebooks/05_expression_correlation.ipynb`  
**Status**: Ready to run

---

## 📋 What This Analysis Does

Tests the **"oncogene addiction" hypothesis**: Do cancers with high target gene expression show higher dependency?

### Key Questions:

1. Does expression correlate with dependency globally?
2. Which cancer types show high expression + high dependency?
3. Is this a classical oncogene addiction mechanism?

---

## Data Used

| Data File                                              | Size     | Purpose               |
| ------------------------------------------------------ | -------- | --------------------- |
| **OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv** | 518 MB   | Gene expression (TPM) |
| **CRISPRGeneEffect.csv**                               | 412 MB   | Dependency scores     |
| **Model.csv**                                          | 683 KB   | Cell line metadata    |
| **cancer_type_rankings.csv**                           | Existing | Previous rankings     |

**Common Cell Lines**: 1,112 with both expression AND dependency data ✅

---

## Target Genes (Verified Present)

| Gene       | Entrez ID | Expression Column | Dependency Column |
| ---------- | --------- | ----------------- | ----------------- |
| **STK17A** | 9263      | STK17A (9263)     | STK17A (9263)     |
| **MYLK4**  | 340156    | MYLK4 (340156)    | MYLK4 (340156)    |
| **TBK1**   | 29110     | TBK1 (29110)      | TBK1 (29110)      |
| **CLK4**   | 57396     | CLK4 (57396)      | CLK4 (57396)      |

---

## Analysis Steps

### 1. Global Correlation

- **Method**: Pearson correlation across all 1,112 cell lines
- **For each gene**: correlation(Expression, Dependency)
- **Interpretation**:
  - **Positive correlation** → Oncogene addiction (HIGH expression = HIGH dependency)
  - **Negative correlation** → Unexpected (investigate)
  - **Near zero** → No relationship

### 2. Per-Cancer-Type Correlation

- Calculate correlations within each cancer type (≥5 cell lines)
- Identify cancers with strong expression-dependency links
- Calculate `expression_dependency_correlation` score

### 3. Identify Oncogene Addiction Candidates

- Find cancers with:
  - Expression > 75th percentile
  - Dependency < 25th percentile (more negative = more dependent)
- **These are PRIME candidates** if both criteria met

### 4. Visualizations

- Scatter plots: Expression vs Dependency for each gene
- Heatmap: Correlation by cancer type

### 5. Merge with Existing Rankings

- Add expression scores to `cancer_type_rankings.csv`
- Create `cancer_type_rankings_with_expression.csv`

---

## 📤 Outputs Generated

| File                                          | Description                                    |
| --------------------------------------------- | ---------------------------------------------- |
| `cancer_type_rankings_with_expression.csv`    | **Main output** - rankings + expression scores |
| `expression_correlation_by_cancer.csv`        | Detailed correlations per cancer               |
| `expression_correlation_global.csv`           | Global correlations for each gene              |
| `expression_dependency_scatter_all_genes.png` | Scatter plots (4 genes)                        |

---

## ⚙️ How to Run

### Option 1: Jupyter Lab (Recommended)

```bash
cd /Users/parkercase/starx-therapeutics-analysis
source venv/bin/activate
jupyter lab notebooks/05_expression_correlation.ipynb
```

Then: **Run All Cells** (Kernel → Restart & Run All)

### Option 2: Command Line

```bash
cd /Users/parkercase/starx-therapeutics-analysis
source venv/bin/activate
jupyter nbconvert --to notebook --execute notebooks/05_expression_correlation.ipynb
```

**Expected Runtime**: 5-10 minutes (large expression file)

---

## 🔍 Key Metrics to Watch

### Global Correlations

- **r > 0.3 and p < 0.05** → Strong oncogene addiction evidence
- **r > 0.1 and p < 0.05** → Weak but significant
- **r < 0.1 or p > 0.05** → No oncogene addiction (look at other mechanisms)

### Per-Cancer Correlations

- Cancers with positive correlations → Classical oncogene addiction
- Cancers with negative correlations → Investigate (may be tumor suppressors)

### Oncogene Addiction Candidates

- If candidates found → These are TOP PRIORITY for drug development
- If NO candidates → Dependencies driven by other mechanisms (mutations, copy number)

---

## Expected Results

Based on previous synthetic lethality analysis:

- **Likely outcome**: Weak or no global correlation
- **Why**: These genes showed context-specific dependencies (mutations), NOT broad essentiality
- **Implication**: Expression may not be a strong predictor

**If correlation IS strong**:

- ✅ This is GOOD NEWS - classical oncogene addiction
- → High-expressing cancers are excellent targets

**If correlation is weak/absent**:

- ⚠️ Expected based on prior results
- → Look to copy number (Notebook 06) or mutations (already done)
- → Multi-factor model will be needed

---

## 🔗 Next Steps After This Analysis

### Immediate

1. Review global correlation results
2. Identify cancers with high expression + high dependency
3. Compare with synthetic lethality results (Notebook 04)

### Next Notebook: Copy Number Analysis

Create `06_copy_number_impact.ipynb`:

```
GOAL: Test if gene amplifications correlate with dependency

HYPOTHESIS: Amplified genes → Higher dependency (oncogene addiction via copy number)

DATA: OmicsCNGeneWGS.csv (copy number variations)

ANALYSIS:
- Classify: Amplified (>2.5), Normal (1.5-2.5), Deleted (<1.5)
- Test: Amplification → Higher dependency?
- Per cancer: % amplified, mean CN, CN-dependency correlation
```

### Final Notebook: Comprehensive Scoring (07)

Combine ALL analyses:

- Dependency (done)
- Expression (current)
- Copy number (next)
- Mutations (done)

Create final comprehensive cancer rankings.

---

## 🐛 Troubleshooting

### Error: "0 common cell lines"

**Fix**: Expression file must use `ModelID` as index

```python
expression = pd.read_csv('...csv')
expression = expression.set_index('ModelID')  # CRITICAL!
```

### Error: "Column not found"

**Check**: Target gene column names in expression file

```python
expr_cols = [col for col in expression.columns if 'STK17A' in col and '9263' in col]
print(expr_cols)  # Should find 'STK17A (9263)'
```

### Low Memory Warning

**Normal**: Expression file is 518 MB

- Analysis will run but may take 5-10 minutes
- Consider running on a machine with >8GB RAM

---

## 📝 Notes for Interpretation

### Positive Correlation (r > 0)

- **Interpretation**: Higher expression → More dependent
- **Mechanism**: Classic oncogene addiction
- **Clinical Strategy**: Target high-expressing cancers
- **Example**: MYC amplification → MYC dependency

### Negative Correlation (r < 0)

- **Interpretation**: Higher expression → Less dependent
- **Mechanism**: May act as tumor suppressor, or compensatory pathway
- **Clinical Strategy**: Investigate further before targeting

### No Correlation (r ≈ 0)

- **Interpretation**: Expression doesn't predict dependency
- **Mechanism**: Other factors drive dependency (mutations, CN, essential pathways)
- **Clinical Strategy**: Use other biomarkers (mutation status, CN)

---

## ✅ Checklist Before Running

- [x] Expression file exists (518 MB)
- [x] Dependency file exists (412 MB)
- [x] cancer_type_rankings.csv exists from previous analysis
- [x] Virtual environment activated
- [x] Jupyter Lab installed
- [x] All target genes verified present in data

**Status**: ✅ READY TO RUN

---

## 📧 Questions or Issues

If notebook fails:

1. Check data file paths are correct
2. Verify all 4 target genes found in expression data
3. Confirm 1,112+ common cell lines
4. Check memory available (need ~4-8GB for large files)

---

**Created**: October 29, 2025  
**Next**: Run notebook → Review results → Proceed to Copy Number Analysis (06)
