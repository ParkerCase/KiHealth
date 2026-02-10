# M1 Data Quality Report — KiHealth Unified Dataset

**Generated:** Milestone 1 (Data Preparation)  
**File:** `data/processed/kihealth_unified.csv`  
**Schema:** TIER 1 + TIER 2 standardized variables.

---

## 1. Total Samples by Dataset

| dataset_source      | N     | % of total | Population |
|---------------------|-------|------------|------------|
| chns_2009           | 9,549 | 33.8%      | China      |
| nhanes_2017_2020    | 5,090 | 18.0%      | USA        |
| nhanes_2021_2023    | 3,996 | 14.2%      | USA        |
| nhanes_2013_2014    | 3,329 | 11.8%      | USA        |
| nhanes_2015_2016    | 3,191 | 11.3%      | USA        |
| frankfurt           | 2,000 | 7.1%       | USA (Pima) |
| diabd               | 1,065 | 3.8%       | South Asia |
| **Total**           | **38,509** | 100%   | Multi-national |

### Diabetes Cases (diabetes_status=1: fasting glucose ≥126 mg/dL or HbA1c ≥6.5%)

| dataset_source      | Diabetes N | % of dataset |
|---------------------|------------|--------------|
| chns_2009           | 882        | 9.2%         |
| diabd               | 840        | 78.9%        |
| nhanes_2017_2020    | 780        | 15.3%        |
| frankfurt           | 684        | 34.2%        |
| nhanes_2021_2023    | 532        | 13.3%        |
| nhanes_2015_2016    | 461        | 14.5%        |
| nhanes_2013_2014    | 385        | 11.6%        |
| **Total diabetes**  | **5,240**  | **13.6%**    |

**HOMA-eligible (invalid_homa_flag=False):** 35,444 samples; 33,078 used for training; 5,240 total diabetes cases.

---

## 2. Missing Data Summary (% missing per variable)

| Variable                    | % missing | Notes                                      |
|-----------------------------|-----------|--------------------------------------------|
| patient_id                  | 0.0       | —                                          |
| age_years                   | 0.0       | —                                          |
| sex                         | 8.8       | DiaBD has no sex; NHANES complete          |
| bmi_kg_m2                   | 1.3       | NHANES: from BMX (BMXBMI); 158 with no BMX/match |
| glucose_mg_dl               | 5.5       | NHANES fasting subsample missing           |
| insulin_uU_ml               | 7.8       | —                                          |
| homa_ir                     | 22.6      | Frankfurt 2-hour OGTT + DiaBD zeros → NaN |
| homa_beta                   | 22.6      | Same                                      |
| diabetes_status             | 0.0       | —                                          |
| invalid_homa_flag           | 0.0       | —                                          |
| homa_analysis_eligible      | 0.0       | — (NHANES=True, Frankfurt/DiaBD=False)     |
| race_ethnicity              | 25.2      | NHANES only; Frankfurt/DiaBD NaN           |
| education_level             | 36.8      | NHANES only; refusals/don’t know           |
| pir                         | 35.4      | NHANES only                                |
| hba1c_percent               | 29.9      | NHANES only; Frankfurt/DiaBD NaN           |
| bp_systolic_mmHg            | 91.2      | Frankfurt has diastolic only              |
| bp_diastolic_mmHg           | 74.8      | NHANES no BP in DEMO/GLU/INS               |
| pregnancies_count           | 74.8      | NHANES no pregnancies                      |
| diabetes_pedigree_function   | 74.8      | NHANES no pedigree                         |
| survey_weight               | 25.2      | NHANES only                                |
| survey_year                 | 25.2      | NHANES only                                |
| dataset_source              | 0.0       | —                                          |
| diq_diabetes                | *         | NHANES only (Diabetes Questionnaire); NA elsewhere |
| diq_prediabetes             | *         | NHANES only                                |
| insulin_use                 | *         | NHANES only                                |
| diabetes_pills              | *         | NHANES only                                |

\* When NHANES DIQ files are present (`NHANES-Diabetes/` or `NIHANES/`), these columns are populated for NHANES rows; otherwise NA.

---

## 3. Invalid HOMA Flag (Within-Sample Issues)

Samples with **invalid_homa_flag = True** have HOMA-IR and HOMA-beta set to NaN (invalid for HOMA-based analysis). This is **separate from** dataset-level HOMA analysis eligibility (Section 3.1).

| dataset_source      | N total | Invalid HOMA (count) | Invalid % | Reason |
|---------------------|---------|----------------------|-----------|--------|
| chns_2009           | 9,549   | ~70                  | ~0.7%     | glucose≤0 or insulin≤0 (minor) |
| nhanes_2017_2020    | 5,090   | 0                    | 0%        | All valid (fasting) |
| nhanes_2021_2023    | 3,996   | 0                    | 0%        | All valid (fasting) |
| nhanes_2013_2014    | 3,329   | 0                    | 0%        | All valid (fasting) |
| nhanes_2015_2016    | 3,191   | 0                    | 0%        | All valid (fasting) |
| frankfurt           | 2,000   | 2,000                | 100%      | 2-hour OGTT insulin (not fasting) |
| diabd               | 1,065   | 741                  | 69.6%     | glucose≤0 or insulin≤0 |
| **Total**           | **38,509** | **~2,811**       | **~7.3%** | — |

HOMA-based modeling in this project uses only rows where **`homa_analysis_eligible == True`** (35,444 samples; 33,078 used for training). See Section 3.1 for eligibility details.

### 3.1 HOMA Analysis Eligibility — Frankfurt & DiaBD Exclusion

**CRITICAL DATA QUALITY DECISION:** Frankfurt and DiaBD datasets are **EXCLUDED** from HOMA-IR/beta analysis due to measurement validity and data quality issues. Use **`homa_analysis_eligible`** to select the HOMA modeling sample.

#### Frankfurt (Pima Indians) — 2-Hour OGTT Insulin

**Issue:** Dataset contains 2-hour post-glucose insulin from Oral Glucose Tolerance Tests (OGTT), **NOT** fasting insulin.

**Evidence:**
- Original UCI ML Repository description: "Insulin: 2-hour serum insulin (mu U/ml)"
- Reference: Smith et al. (1988) "Using the ADAP Learning Algorithm..."
- Mean insulin: ~80 μU/mL (typical for 2-hour post-glucose; 5–10× higher than fasting)
- HOMA-IR mean ~51.5 (pathologically high, indicates formula misapplication)

**Why this matters:**
- HOMA-IR/beta formulas are for **fasting** steady-state conditions only.
- Using post-glucose insulin produces meaningless HOMA values.
- Normal fasting insulin: 5–15 μU/mL; 2-hour post-glucose: 50–150 μU/mL.

**Action:** All 2,000 Frankfurt samples flagged **`homa_analysis_eligible = False`**.

#### DiaBD — Data Quality Concerns

**Issues:**
- 741/1,065 samples (69.6%) have insulin = 0 (invalid for HOMA).
- Only 324 valid HOMA samples.
- Skin thickness values impossible: 259–381 mm (normal triceps: 10–50 mm).
- Unknown measurement protocols; questionable data provenance (Mendeley repository).

**Action:** All 1,065 DiaBD samples flagged **`homa_analysis_eligible = False`**.

#### NHANES — Gold Standard (HOMA Analysis Dataset)

**Quality indicators:** CDC NHANES; standardized fasting protocols (8–12 hours); certified laboratories; quality-controlled measurements; population-representative sampling; published methodology.

**Valid HOMA samples:** 9,086 (5,090 from 2017–2020 + 3,996 from 2021–2023).

**Action:** All NHANES samples flagged **`homa_analysis_eligible = True`**.

#### CHNS 2009 — China Population (HOMA Analysis Dataset)

**Dataset:** China Health and Nutrition Survey, 2009 wave  
**Source:** UNC/NIH collaborative study  
**URL:** https://www.cpc.unc.edu/projects/china

**Quality indicators:**
- Documented fasting protocol (8–12 hours, 26 fasting blood measures)
- Standardized laboratory measurements
- Certified laboratories
- Population-representative sampling (Chinese adults & children age 7+)
- Published methodology and peer-reviewed studies
- National-level health survey

**Valid HOMA samples:** 9,479 out of 9,549 (99.3%)

**Transfer Learning Value:**
- **Different population:** Chinese vs USA (NHANES)
- **Different dietary patterns:** Traditional Chinese + Western transition
- **Different metabolic profiles:** Lower average BMI, different diabetes rates
- **Validates cross-population generalization:** Tests if HOMA model trained on USA data works for Chinese population
- **Domain shift testing:** Suitable for evaluating model robustness

**Data quality:**
- Fasting insulin mean: 14.55 μU/mL (physiologically normal, similar to NHANES)
- Missing data: <1% for glucose, insulin, HbA1c
- No zero-insulin artifact (unlike DiaBD)
- BMI available for 99.6% (9,516/9,549)
- Age and sex available for 100%

**Action:** All CHNS samples flagged **`homa_analysis_eligible = True`**.

---

#### Summary: HOMA Analysis Eligibility by Dataset

| Dataset           | Total N | homa_analysis_eligible=True | % Eligible | Reason |
|-------------------|---------|------------------------------|------------|--------|
| **CHNS 2009**     | **9,549** | **9,549**                  | **100%**   | **Fasting data, gold standard** |
| NHANES 2017–2020  | 5,090   | 5,090                        | 100%       | Gold standard fasting data |
| NHANES 2021–2023  | 3,996   | 3,996                        | 100%       | Gold standard fasting data |
| Frankfurt         | 2,000   | 0                            | 0%         | 2-hour OGTT insulin (not fasting) |
| DiaBD             | 1,065   | 0                            | 0%         | Data quality concerns |
| **TOTAL**         | **21,700** | **18,635**                | **85.9%**  | — |

**For HOMA-IR/beta modeling:** Use **only** samples where **`homa_analysis_eligible == True`** (N=18,635).

**Cross-population composition:**
- USA (NHANES): 9,086 samples (48.8%)
- China (CHNS): 9,549 samples (51.2%). Of these, 9,479 have valid glucose and insulin for HOMA (99.3%).

**For diabetes outcome prediction:** All datasets valid (N=21,700).

---

## 4. Distribution Statistics (Continuous Variables)

| Variable              | count   | mean   | std    | min   | 25%   | 50%   | 75%   | max    |
|-----------------------|---------|--------|--------|-------|-------|-------|-------|--------|
| age_years             | 12,151  | 44.24  | 19.69  | 12    | 27    | 43    | 61    | 86     |
| bmi_kg_m2             | 11,993  | 29.25  | 7.70   | 0     | 24.00 | 28.00 | 33.30 | 92.30  |
| glucose_mg_dl         | 11,481  | 114.40 | 39.12  | 0     | 94    | 103   | 120   | 561    |
| insulin_uU_ml         | 11,200  | 25.64  | 57.44  | 0     | 4.63  | 9.52  | 18.40 | 744    |
| homa_ir               | 8,432   | 4.58   | 9.78   | 0.07  | 1.56  | 2.65  | 4.73  | 240.00 |
| homa_beta             | 8,408   | 125.47 | 201.47 | 1.02  | 55.97 | 87.75 | 143.13| 10,015 |

*Note:* HOMA stats are for **homa_analysis_eligible & ~invalid_homa_flag** (NHANES only, N=9,086). Frankfurt and DiaBD excluded from HOMA analysis. BMI from all datasets; 158 rows missing BMI.

---

## 5. Categorical Variable Frequencies

### diabetes_status (0 = No, 1 = Yes)

| Value | Count  | %     |
|-------|--------|-------|
| 0     | 9,315  | 76.6% |
| 1     | 2,836  | 23.4% |

### dataset_source

See Section 1.

### sex (0 = Female, 1 = Male) — where present

- Frankfurt: all 0 (female).
- DiaBD: all missing (sex not collected).
- NHANES: mix of 0 and 1.

### race_ethnicity (NHANES only)

Present for ~75% of NHANES rows; categories include Mexican American, Other Hispanic, Non-Hispanic White, Non-Hispanic Black, Non-Hispanic Asian, Other/Multi-Racial.

### education_level (NHANES only)

Present for ~63% of NHANES rows; categories include Less than 9th grade, 9-11th grade, High school grad/GED, Some college or AA, College graduate or above, Refused, Don’t know.

---

## 6. Known Issues and Fixes

### 6.1 DiaBD Skin Thickness

- **Issue:** “Skin Thickness(mm)” has values ~259–381 (implausible for triceps skinfold in mm).
- **Status:** Variable omitted from unified schema for M1 (per “SKIP FOR NOW”).
- **Investigation:** Check if unit is 0.1 mm (e.g. 259 → 25.9 mm) or a coding error; validate against source documentation before reintroducing.

### 6.2 Frankfurt / DiaBD: glucose = 0 or insulin = 0

- **Issue:** 958 (Frankfurt) and 741 (DiaBD) rows have glucose ≤ 0 or insulin ≤ 0 → invalid for HOMA.
- **Handling:** `invalid_homa_flag` set True; `homa_ir` and `homa_beta` set to NaN. These rows are excluded from HOMA modeling but retained for diabetes_status and other outcomes.

### 6.3 NHANES diabetes_status

- **Derivation:** Binary flag = 1 if **fasting glucose ≥ 126 mg/dL** OR **HbA1c ≥ 6.5%**; else 0.
- **Note:** DIQ010 (doctor-diagnosed) and diabetes medication not in current DEMO/GLU/INS/GHB load; add DIQ/medication files if needed for a stricter definition.

### 6.4 NHANES BMI

- **Status (resolved):** BMI is now merged from BMX (2017-20P_BMX.xpt, 2021-23BMX_L.xpt) on SEQN; BMXBMI mapped to `bmi_kg_m2`. Left join used so fasting subsample is retained; 158 rows (1.3%) have missing BMI where BMX was not measured or BMXBMI is missing.

### 6.5 Duplicate checks

- **NHANES 2017–20 vs 2021–23:** No duplicate SEQNs. Each cycle has distinct SEQN ranges (2017–20: 109,264–124,822; 2021–23: 130,378–142,309). Different participants per cycle.
- **Cross-dataset (fingerprint):** No same-person duplicates across sources. Fingerprint (age, sex, BMI, glucose, insulin) matches across *different* datasets: 0 for Frankfurt↔DiaBD; 11 matches are NHANES↔NHANES (different cycles, same demographics = different people, coincidental).

---

## 7. Recommended Train / Validation / Test Split

- **Split:** 70% train, 15% validation, 15% test.
- **Stratification:** By **diabetes_status** (0/1) to preserve outcome prevalence.
- **Random seed:** Fixed (e.g. 42) for reproducibility.
- **Optional:** Stratify by **dataset_source** to ensure each split has all sources, or split by source (e.g. hold out one NHANES cycle or DiaBD) for external validation.

**Approximate sizes (12,151 total):**

- Train: ~8,506  
- Validation: ~1,823  
- Test: ~1,822  

For HOMA-outcome models, apply the same split to the subset with **homa_analysis_eligible == True** (N = 9,086, NHANES only).

---

*End of M1 Data Quality Report.*
