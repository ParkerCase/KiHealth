# Data Preparation - 100% Validation Report

**Date:** Generated automatically  
**Status:** ✅ COMPLETE (with 4-year outcome recommendation)

---

## Executive Summary

Data preparation completed with 100% verification. All datasets merged successfully. **4-year knee replacement outcome recommended for modeling** (EPV=17.10 ≥15). 2-year outcome has insufficient events (EPV=6.80 <15).

---

## Validation Checklist

### ✅ 1. Dataset Structure

- **Rows:** 4,796 (100% match with expected)
- **Columns:** 13 total (10 predictors + 2 outcomes + ID)
- **Duplicate IDs:** 0 ✅
- **All patients included:** ✅

### ✅ 2. Outcome Variables

#### 2-Year Knee Replacement

- **Events:** 68 (1.42% event rate)
- **EPV Ratio:** 6.80
- **Status:** ❌ FAIL (need ≥15)
- **Recommendation:** Do not use for modeling

#### 4-Year Knee Replacement

- **Events:** 171 (3.57% event rate)
- **EPV Ratio:** 17.10
- **Status:** ✅ PASS (≥15)
- **Recommendation:** ✅ **USE FOR MODELING**

### ✅ 3. Predictor Variables (10 total)

| Variable  | Source            | Missing % | Status |
| --------- | ----------------- | --------- | ------ |
| P02SEX    | Enrollees.txt     | 0.00%     | ✅     |
| P02RACE   | Enrollees.txt     | 0.00%     | ✅     |
| V00COHORT | Enrollees.txt     | 0.00%     | ✅     |
| V00WOMTSR | AllClinical00.txt | 0.44%     | ✅     |
| V00WOMTSL | AllClinical00.txt | 0.58%     | ✅     |
| V00AGE    | AllClinical00.txt | 0.00%     | ✅     |
| P01BMI    | AllClinical00.txt | 0.08%     | ✅     |
| V00XRKLR  | MeasInventory.csv | 6.82%     | ✅     |
| V00XRKLL  | MeasInventory.csv | 6.53%     | ✅     |
| P01FAMKR  | SubjectChar00.txt | 0.00%     | ✅     |

**All variables have <20% missing data** ✅

### ✅ 4. EPV Ratio Calculation

**Formula:** EPV = Events / Number of Predictors

- **2-Year Outcome:** 68 events / 10 predictors = **6.80** ❌
- **4-Year Outcome:** 171 events / 10 predictors = **17.10** ✅

**PROBAST Compliance:** ✅ PASS (using 4-year outcome)

### ✅ 5. Data Quality Checks

#### Age

- **Range:** 45-79 years
- **Expected:** 45-85 years
- **Status:** ✅ All values within range

#### BMI

- **Range:** 16.9-48.7 kg/m²
- **Expected:** 15-60 kg/m²
- **Status:** ✅ All values within range

#### WOMAC Scores

- **V00WOMTSR (Right):** 0-94 (expected 0-100) ✅
- **V00WOMTSL (Left):** 0-96 (expected 0-100) ✅
- **Status:** ✅ All values within range

#### KL Grades

- **V00XRKLR (Right):** 0-4 ✅
- **V00XRKLL (Left):** 0-4 ✅
- **Status:** ✅ All values within range

### ✅ 6. Baseline Variables Only

**Check:** All predictor variables start with V00, P01, or P02 (baseline prefixes)

- **Non-baseline variables found:** 0 ✅
- **Status:** ✅ No data leakage

### ✅ 7. Missing Data Analysis

- **Variables with >20% missing:** 0 ✅
- **Variables with >10% missing:** 0 ✅
- **Variables with >5% missing:** 2 (KL grades at 6.5-6.8%, acceptable)
- **Status:** ✅ Acceptable missingness patterns

---

## Output Files Generated

1. ✅ `data/baseline_merged.csv` - Merged dataset without outcomes (4,796 rows × 11 columns)
2. ✅ `data/baseline_modeling.csv` - Complete dataset with outcomes (4,796 rows × 13 columns)
3. ✅ `data_dictionary.csv` - Complete variable documentation (13 variables)
4. ✅ `EPV_calculation.txt` - EPV ratio report
5. ✅ `missing_data_report.png` - Missingness heatmap visualization
6. ✅ `notebooks/3_data_preparation.ipynb` - Complete code notebook

---

## Outcome Variable Definition

### Knee Replacement (4-year outcome)

**Source:** Outcomes99.txt  
**Variables used:**

- `V99ERKRPCF`: Right knee replacement confirmed status
- `V99ELKRPCF`: Left knee replacement confirmed status
- `V99ERKDAYS`: Days from baseline to right knee replacement
- `V99ELKDAYS`: Days from baseline to left knee replacement

**Definition:**

- Total knee replacement (either right or left knee) occurring within 48 months (1,460 days) of baseline visit
- Replacement confirmed by adjudication (`V99ERKRPCF` or `V99ELKRPCF` = "3: Replacement adjudicated, confirmed")
- Patient-level outcome: If either knee was replaced within 4 years, outcome = 1

**Coding:** Binary (0 = no replacement, 1 = replacement occurred)

**Rationale:**

- Patient-level outcome (not knee-level) - clinically relevant as patients typically get one knee replaced
- 4-year timeframe balances sufficient events (171) with clinical relevance
- Adjudicated replacements ensure data quality (not self-reported)

### Knee Replacement (2-year outcome)

**Definition:** Same as above but within 24 months (730 days)  
**Status:** ❌ Not recommended (insufficient events, EPV=6.80 <15)

---

## Predictor Selection Rationale

### Included Variables (10 total)

**Selection Criteria:**

1. **Clinical relevance** - Evidence-based OA risk factors
2. **Data availability** - >90% completeness
3. **Routine clinical accessibility** - No specialized tests required
4. **Non-redundancy** - Avoid multicollinearity
5. **EPV compliance** - Sufficient events per variable (≥15)

#### Demographics (4 variables)

1. **Age (V00AGE)** - Established OA risk factor (increases with age)
2. **Sex (P02SEX)** - Female sex is OA risk factor
3. **Race (P02RACE)** - Demographic confounder, important for generalizability
4. **Cohort (V00COHORT)** - Progression vs Incidence (different risk profiles)

#### Clinical Scores (2 variables)

5. **WOMAC Total Right (V00WOMTSR)** - Gold standard OA symptom measure (0-96 scale)
6. **WOMAC Total Left (V00WOMTSL)** - Symptom severity predictor

**Rationale for using Total scores:**

- Composite scores reduce dimensionality (vs. separate pain/stiffness/function)
- Maintains clinical relevance while achieving EPV ≥15
- Total score is standard clinical metric

#### Anthropometric (1 variable)

7. **BMI (P01BMI)** - Well-documented mechanical OA risk factor

#### Imaging (2 variables)

8. **KL Grade Right (V00XRKLR)** - Validated structural OA severity (0-4)
9. **KL Grade Left (V00XRKLL)** - Radiographic severity predictor

**Distribution:** Balanced across grades 0-4 (not heavily skewed)

#### Risk Factors (1 variable)

10. **Family History (P01FAMKR)** - Strong genetic predisposition indicator

### Excluded Variables (with rationale)

**Pain VAS scores:**

- **Rationale:** Redundant with WOMAC pain component (already in total score)
- **Data availability:** Limited availability in AllClinical00

**20m walk time, Chair stand time:**

- **Rationale:** Redundant with WOMAC function component
- **Missing data:** Higher missingness than WOMAC total

**Individual WOMAC components (pain, stiffness, function):**

- **Rationale:** Used total score to reduce predictor count and achieve EPV ≥15
- **Trade-off:** Slight loss of granularity for statistical power

**Biomarkers:**

- **Rationale:** Limited clinical utility, not routinely available in clinical practice
- **Missing data:** Variable availability across patients

**Previous knee injury (P01INJR, P01INJL):**

- **Rationale:** High missingness, less predictive than family history
- **Clinical relevance:** Lower evidence base than other included variables

**Physical activity scale (V00PASE):**

- **Rationale:** Complex categorical variable, less interpretable
- **Redundancy:** Partially captured by BMI and WOMAC function

**Work status (V00WORK7):**

- **Rationale:** Less directly related to OA progression than included variables

---

## Final Recommendations

### ✅ Primary Outcome for Modeling

**Use: `knee_replacement_4yr`**

- EPV ratio: 17.10 (≥15) ✅
- Event rate: 3.57% (171 events)
- Sufficient for robust modeling
- PROBAST compliant

### ❌ Do Not Use

**Avoid: `knee_replacement_2yr`**

- EPV ratio: 6.80 (<15) ❌
- Event rate: 1.42% (68 events)
- Insufficient for reliable modeling
- Would violate PROBAST guidelines

---

## Data Dictionary Summary

| Variable             | Type        | Description                 | Missing % |
| -------------------- | ----------- | --------------------------- | --------- |
| ID                   | Identifier  | Patient ID                  | 0%        |
| P02SEX               | Categorical | Sex                         | 0%        |
| P02RACE              | Categorical | Race                        | 0%        |
| V00COHORT            | Categorical | Cohort type                 | 0%        |
| V00WOMTSR            | Continuous  | WOMAC Total Right           | 0.44%     |
| V00WOMTSL            | Continuous  | WOMAC Total Left            | 0.58%     |
| V00AGE               | Continuous  | Age at baseline             | 0%        |
| P01BMI               | Continuous  | Body Mass Index             | 0.08%     |
| V00XRKLR             | Ordinal     | KL Grade Right (0-4)        | 6.82%     |
| V00XRKLL             | Ordinal     | KL Grade Left (0-4)         | 6.53%     |
| P01FAMKR             | Categorical | Family history knee OA      | 0%        |
| knee_replacement_2yr | Binary      | Outcome: 2-year replacement | 0%        |
| knee_replacement_4yr | Binary      | Outcome: 4-year replacement | 0%        |

---

## Validation Status: ✅ COMPLETE

**All critical checks passed:**

- ✅ 4,796 rows (100% of cohort)
- ✅ No duplicate patients
- ✅ EPV ratio ≥15 (4-year outcome)
- ✅ <20% missing in all critical variables
- ✅ All values within plausible ranges
- ✅ Only baseline variables (no data leakage)

**Ready for modeling with 4-year outcome.**
