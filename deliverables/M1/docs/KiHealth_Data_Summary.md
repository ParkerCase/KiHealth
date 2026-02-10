# KiHealth Diabetes Data Summary

**Generated:** Milestone 1 – Data Preparation  
**Purpose:** Comprehensive inventory and usability assessment for HOMA-IR / HOMA-beta prediction from clinical and (future) methylation data.

---

## CRITICAL: HOMA Analysis Dataset Restrictions

**For HOMA-IR/beta modeling, use HOMA-eligible data (N=35,444; 33,078 used for training).**

**HOMA-eligible datasets:**
1. **NHANES (USA):** 15,606 samples — 2013-14, 2015-16, 2017-20, 2021-23 cycles; gold standard fasting protocol.
2. **CHNS 2009 (China):** 9,479 samples — documented fasting protocol, cross-population validation.

**Excluded datasets:**
1. **Frankfurt (Pima Indians):** 2-hour OGTT insulin — HOMA formulas invalid.
2. **DiaBD:** Data quality concerns — 69.6% invalid, impossible skin thickness values.

**All datasets valid for diabetes outcome prediction (N=38,509). Total diabetes cases: 5,240 (13.6%).**

Use **`homa_analysis_eligible == True`** to select the HOMA modeling sample. See Section 3.1 in `reports/M1_Data_Quality_Report.md` for detailed rationale.

---

## Multi-Population Transfer Learning Dataset

**M1 delivers a cross-population dataset for transfer learning:**

### HOMA-Eligible Datasets (N=35,444; 33,078 used for training)

**1. NHANES (USA) — Source Domain**
- Samples: 15,606 (2013-14, 2015-16, 2017-20, 2021-23 cycles)
- Population: USA multi-ethnic
- Protocol: CDC gold standard fasting protocol
- Use: Primary training dataset for base HOMA-IR/beta model

**2. CHNS (China) — Target Domain**
- Samples: 9,479 (2009 wave)
- Population: Chinese adults and children (age 7+)
- Protocol: UNC/NIH fasting protocol (26 fasting blood measures)
- Use: Cross-population validation and domain adaptation

### Transfer Learning Strategy

**Phase 1 (M2):** Train base model on NHANES (USA population)  
**Phase 2 (M2):** Validate on CHNS (China population) to test generalization  
**Phase 3 (M2):** Optional fine-tuning on CHNS if needed  
**Phase 4 (M3):** Fine-tune on KiHealth methylation data (target application)

**Benefits:**
- Robust to population differences
- Validated across genetic backgrounds
- Tested on different dietary patterns
- Strong foundation for methylation integration

### Datasets Excluded from HOMA Analysis (Still Valid for Other Tasks)

**Frankfurt (Pima Indians):** 2-hour OGTT insulin (N=2,000)  
**DiaBD:** Data quality issues (N=1,065)

Both can be used for diabetes outcome prediction, model generalization testing, and population comparison studies.

---

## 1. Total Files Analyzed

| Location | File count (approx.) | Formats |
|----------|----------------------|---------|
| Diabetes-KiHealth/ (root) | 6 | .docx, .xlsx, .pptx |
| Diabetes-KiHealth/TL-KiHealth/ | 1 | .txt |
| Diabetes-KiHealth/TL-KiHealth/2013-14-NHANES/ | 6+ | .xpt (SAS transport) |
| Diabetes-KiHealth/TL-KiHealth/2015-16-NHANES/ | 6+ | .xpt (SAS transport) |
| Diabetes-KiHealth/TL-KiHealth/NIHANES/ | 8+ | .xpt (SAS transport) |
| Diabetes-KiHealth/TL-KiHealth/NHANES-Diabetes/ | 4 | .xpt (DIQ) |
| Diabetes-KiHealth/TL-KiHealth/Frankfurt/ | 1 | .csv |
| Diabetes-KiHealth/TL-KiHealth/DiaBD/ | 1 | .csv |
| Diabetes-KiHealth/TL-KiHealth/sharpic-Manchester.../ | 2000+ | .csv, .md, .cff |
| Diabetes-KiHealth/TL-KiHealth/HUPA-UCM-Diabetes-Dataset/ | 2000+ | .csv (FreeStyle sensor, Fitbit sleep/steps) |

**Total structured data files analyzed for M1:** 18+ (excluding Manchester and HUPA-UCM CGM/sensor CSVs for HOMA outcome definition).

---

## 2. Patient/Sample Counts by Source

| Source | Unique patients/samples | With fasting glucose | With fasting insulin | With both (HOMA-ready) |
|--------|-------------------------|-----------------------|------------------------|--------------------------|
| **NHANES 2013–2014** | 3,329 | 3,329 | 3,329 | **3,329** |
| **NHANES 2015–2016** | 3,191 | 3,191 | 3,191 | **3,191** |
| **NHANES 2017–March 2020** | 5,090 | 5,090 | 5,090 | **5,090** |
| **NHANES 2021–2023** | 3,996 | 3,996 | 3,996 | **3,996** |
| **CHNS 2009** | 9,549 | 9,549 | 9,549 | **9,479** |
| **Frankfurt (diabetes.csv)** | 2,000 | 2,000 | 2,000 | **0** (2-hour OGTT insulin; excluded from HOMA) |
| **DiaBD (DiaBD.csv)** | 1,065 | 1,065 | 1,065 | **324** (69.6% invalid) |

**Total:** 38,509 samples. **HOMA-ready:** 35,444 (33,078 used for training). **Diabetes cases (glucose≥126 or HbA1c≥6.5):** 5,240 (13.6%).

---

## 3. File-by-File Summary

### 3.1 Diabetes-KiHealth/ (root)

| File | Size (approx.) | Format | Purpose |
|------|----------------|--------|---------|
| Combine Beta Score Writeup.docx | — | Word | Documentation |
| Draft_Methods_Results.docx | ~74 KB | Word | Methods/results draft |
| Ext Dataset for Use 20OCT2025.xlsx | ~508 KB | Excel | Sheets: V1 Validation, BioIVT, Cardinal, Cliff Modified (notes row; structure TBD for methylation/biomarkers) |
| Kihealth Data Workflow Model 15OCT2025.pptx | — | PowerPoint | Workflow/model overview |
| October 2025 Blood Drive.xlsx | — | Excel | **Results** sheet: UIN, DIA#, C-peptide, Insulin, A1c, % Unmethylated, Age, BMI, diabetes Qs. **Current state:** 33 rows; A1c present; C-peptide, Insulin, % Unmethylated all missing. |
| Score Calcualtions.docx | ~17 KB | Word | Score calculations documentation |

**Usability for M1:**  
- **October 2025 Blood Drive:** Not yet usable for HOMA (no fasting glucose/insulin; methylation column empty).  
- **Ext Dataset for Use 20OCT2025.xlsx:** Requires parsing past notes row; may contain methylation + biomarkers for future use.

### 3.2 TL-KiHealth/NIHANES/

NHANES uses **SEQN** as the participant ID. Fasting subsample weights: **WTSAFPRP** (2017–20), **WTSAF2YR** (2021–23).

| File | Rows | Columns (key) | Key variables | Missing (key) |
|------|------|----------------|----------------|----------------|
| 2017-20P_DEMO.xpt | 15,560 | SEQN, RIAGENDR, RIDAGEYR, RIDRETH3, DMDEDUC2, INDFMPIR, WTINTPRP, WTMECPRP, SDMVPSU, SDMVSTRA, … | Demographics, survey weights | RIDAGEMN 93.7%, DMDEDUC2 40.7% |
| 2017-20P_GHB.xpt | 10,409 | SEQN, LBXGH | HbA1c (%) | LBXGH 6.5% |
| 2017-20P_GLU.xpt | 5,090 | SEQN, WTSAFPRP, LBXGLU, LBDGLUSI | Fasting glucose (mg/dL; SI: mmol/L) | LBXGLU 6.8% |
| 2017-20P_INS.xpt | 5,090 | SEQN, WTSAFPRP, LBXIN, LBDINSI, LBDINLC | Fasting insulin (μU/mL) | LBXIN 9.1% |
| 2021-23DEMO_L.xpt | 11,933 | SEQN, RIAGENDR, RIDAGEYR, … | Demographics (2021–23) | Various 25–87% for optional vars |
| 2021-23GHB_L.xpt | 7,199 | SEQN, WTPH2YR, LBXGH | HbA1c (%) | LBXGH 6.7% |
| 2021-23GLU_L.xpt | 3,996 | SEQN, WTSAF2YR, LBXGLU, LBDGLUSI | Fasting glucose (mg/dL) | LBXGLU 8.1% |
| 2021-23INS_L (1).xpt | 3,996 | SEQN, WTSAF2YR, LBXIN, LBDINSI, LBDINLC | Fasting insulin (μU/mL) | LBXIN 12.2% |

**Merge key:** SEQN. GLU and INS row counts match per cycle (fasting subsample).  
**Units:** LBXGLU = mg/dL; LBXIN = μU/mL (direct for HOMA formulas).  
**Usability:** ✅ **Usable** for HOMA-IR and HOMA-beta (after merge DEMO + GLU + INS; use survey weights in analysis).

**Diabetes Questionnaire (DIQ):** When DIQ files are present in `NHANES-Diabetes/` or `NIHANES/` (e.g. `17-19DIQ_L.xpt`, `21-23P_DIQ.xpt`), the pipeline merges them by SEQN and adds unified columns: `diq_diabetes` (DIQ010), `diq_prediabetes` (DIQ160), `insulin_use` (DIQ050), `diabetes_pills` (DIQ070). These support self-reported diabetes/prediabetes and treatment for outcome definitions and questionnaire integration.

### 3.3 TL-KiHealth/Frankfurt/diabetes.csv

**Dataset:** Pima Indians Diabetes Dataset (Smith et al., 1988). Source: UCI ML Repository. Downloaded from: https://github.com/ibrahimuhammad/diabetes_prediction

| Attribute | Value |
|-----------|--------|
| Rows | 2,000 |
| Columns | Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome |
| Glucose | mg/dL (fasting) |
| Insulin | **2-hour serum insulin (μU/mL)** from OGTT — **NOT fasting** |
| Missing | 0% all columns |
| Outcome | 0: 1316, 1: 684 (diabetic) |

**CRITICAL LIMITATION:** Insulin is **2-hour post-glucose** (OGTT), not fasting. HOMA-IR and HOMA-beta require **fasting** glucose and insulin; using 2-hour insulin produces invalid HOMA. All Frankfurt samples are flagged `invalid_homa_flag = True` and excluded from HOMA-based modeling.

**Valid uses:** Diabetes outcome (Outcome 0/1), glucose-based analysis, demographics, BMI. **Not** HOMA-IR, HOMA-beta, or insulin resistance modeling.

### 3.4 TL-KiHealth/DiaBD/DiaBD.csv

| Attribute | Value |
|-----------|--------|
| Rows | 1,065 |
| Columns | No. of Pregnancy, Age, BMI, BP(Systolic), BP(Diastolic), DiabetesPedigreeFunction, Insulin, Skin Thickness(mm), Type-2 Diabetic, Glucose |
| Glucose | (min 50, max 450, mean 138.4) — units assumed mg/dL |
| Insulin | (min 0, max 44, mean 5.4) — units assumed μU/mL |
| Missing | BP(Diastolic) 0.4%, Skin Thickness(mm) 0.7% |
| Type-2 Diabetic | 1: 840, 0: 225 |

**Data quality issue:** “Skin Thickness(mm)” values ~259–381 suggest wrong unit or coding (triceps skinfold typically 10–40 mm); do not use for skinfold without verification.  
**Usability:** ✅ **Usable** for HOMA-IR/HOMA-beta (Glucose and Insulin present; exclude or handle Insulin=0 for HOMA-beta). No methylation; no direct identifiers.

### 3.5 TL-KiHealth/sharpic-ManchesterCSCoordinatedDiabetesStudy-a9e8025/

**Content:** T1D longitudinal CGM, insulin (basal/bolus), nutrition, sleep, activity (16 participants).  
**Glucose:** CGM values in **mmol/L** (not fasting lab); **Insulin:** doses (U), not fasting serum insulin.  
**Usability for HOMA:** ❌ **Not usable** for fasting HOMA-IR/HOMA-beta. Useful for T1D management / CGM modeling only.

### 3.6 TL-KiHealth/HUPA-UCM-Diabetes-Dataset/

**Content:** UCM (Universidad Complutense de Madrid) / HUPA diabetes dataset. **~27 FreeStyle LibreLink sensor CSV files** across ~20 participants (HUPA0001P–HUPA0028P). Each file has:
- **Historial de glucosa mg/dL** — CGM glucose (mg/dL), time-stamped (not fasting lab).
- **Insulina de acción rápida (unidades)** / **Insulina de acción larga (unidades)** — rapid- and long-acting **insulin doses** in units (bolus/basal), **not** fasting serum insulin (μU/mL).
- **Tira reactiva para glucosa mg/dL** — fingerstick glucose (mg/dL) in some rows; spot checks, not paired with fasting serum insulin.
- Fitbit sleep/steps CSVs in Raw_Data per participant.

**Usability for HOMA:** ❌ **Not usable** for HOMA-IR or HOMA-beta. HOMA requires **fasting plasma glucose** and **fasting serum insulin** (μU/mL) from a single lab draw. Here we have CGM/fingerstick glucose and **insulin doses** (units), not serum insulin concentration. Useful for CGM/time-in-range or dose-response modeling only.

### 3.7 TL-KiHealth/GitHub Search for International Health Datasets.txt

Reference document describing international diabetes datasets (KNHANES, Frankfurt, DiaBD, etc.) and HOMA-IR requirements. No structured data.

---

## 4. Usability for This Project

### 4.1 Usable for M1 (HOMA outcomes)

- **NIHANES 2017–20:** DEMO + GLU + INS (+ BMX) → 5,090 with fasting glucose + insulin. *Merge on SEQN:* SEQN is the NHANES respondent sequence number (unique ID per person per cycle). We join the demographics (DEMO), glucose (GLU), insulin (INS), and body measures (BMX) files by SEQN so each row is one person with all variables.  
- **NIHANES 2021–23:** DEMO + GLU + INS (+ BMX) → 3,996 (same: merge on SEQN per cycle).  
- **Frankfurt/diabetes.csv:** **Excluded from HOMA** — 2-hour OGTT insulin, not fasting. Use for diabetes outcome/glucose only.  
- **DiaBD/DiaBD.csv:** 1,065 rows; handle Insulin=0 for HOMA-beta; 324 valid HOMA rows.

**Valid HOMA sample count for M1:** 9,410 (NHANES 9,086 + DiaBD 324).

### 4.2 Not usable (or not yet) for M1

- **October 2025 Blood Drive.xlsx:** Insulin and % Unmethylated empty; A1c only → not for HOMA or methylation modeling yet.  
- **Ext Dataset for Use 20OCT2025.xlsx:** Structure and methylation/biomarker content to be confirmed.  
- **Manchester T1D-UOM:** No fasting glucose/insulin → not for HOMA.  
- **HUPA-UCM-Diabetes-Dataset:** CGM/fingerstick glucose + insulin **doses** (units), not fasting serum insulin → not for HOMA.  
- **.docx / .pptx:** Documentation only.

### 4.3 Variables for HOMA

- **HOMA-IR:** fasting glucose (mg/dL) × fasting insulin (μU/mL) / 405.  
- **HOMA-beta:** 360 × fasting insulin (μU/mL) / (fasting glucose (mg/dL) − 63).

| Source | Glucose variable | Insulin variable | Units | Notes |
|--------|-------------------|-------------------|--------|--------|
| NIHANES | LBXGLU | LBXIN | mg/dL, μU/mL | Use after merge |
| Frankfurt | Glucose | Insulin | mg/dL, μU/mL | Exclude 0/0 |
| DiaBD | Glucose | Insulin | mg/dL, μU/mL | Handle Insulin=0 |

**Fasting glucose in mmol/L:** convert to mg/dL: `glucose_mg_dL = glucose_mmol_L * 18.0182` before using the formulas above.

---

## 5. Train/Validation/Test and Sample Size

- **Total HOMA-ready:** ~12k+ rows across NHANES (two cycles), Frankfurt, and DiaBD.  
- **Minimum 100:** ✅ Met. **Ideal 500+:** ✅ Met per source.  
- **Split:** By source (e.g., hold out one NHANES cycle or Frankfurt/DiaBD) or random 70/15/15 with stratification by outcome/diabetes status; document in M1.

---

## 6. DNA Methylation and Outcome Labels

- **Methylation (CpG):** Not present in the analyzed tabular files. KiHealth’s own methylation is expected from **October 2025 Blood Drive** (“% Unmethylated”) and/or **Ext Dataset for Use 20OCT2025.xlsx** once populated and parsed.  
- **Clinical biomarkers:** Fasting glucose and insulin (and HbA1c in NHANES/Blood Drive) as above.  
- **Demographics:** NHANES DEMO (age, sex, race, education, PIR, weights); Frankfurt/DiaBD (age, BMI, etc.).  
- **Outcome labels:**  
  - Frankfurt: **Outcome** (0/1).  
  - DiaBD: **Type-2 Diabetic** (0/1).  
  - NHANES: derived (e.g., diabetes by medication/DIQ or by glucose/HbA1c cutoffs); no single “diabetes” column in DEMO/GLU/INS.

---

## 7. Missing Data Summary (Key Files)

| File | Key columns | Missing % |
|------|-------------|-----------|
| 2017-20P_GLU.xpt | LBXGLU | 6.8 |
| 2017-20P_INS.xpt | LBXIN | 9.1 |
| 2021-23GLU_L.xpt | LBXGLU | 8.1 |
| 2021-23INS_L (1).xpt | LBXIN | 12.2 |
| Frankfurt diabetes.csv | All | 0 |
| DiaBD.csv | BP(Diastolic), Skin Thickness(mm) | 0.4, 0.7 |

---

## 8. Data Quality Issues and What We Did

1. **Frankfurt:** Glucose=0 or Insulin=0 in some rows → invalid for HOMA. **What we did:** Frankfurt is excluded from HOMA modeling (`homa_analysis_eligible=False`). Rows are kept in the unified dataset for diabetes outcome and glucose-only use; `invalid_homa_flag=True` and HOMA-IR/HOMA-beta set to NaN for all Frankfurt rows (2-hour OGTT insulin, not fasting).  
2. **DiaBD:** “Skin Thickness(mm)” values 259–381 mm → likely unit/coding error. **What we did:** DiaBD is excluded from HOMA modeling (`homa_analysis_eligible=False`). Rows with Glucose ≤ 0 or Insulin ≤ 0 are flagged (`invalid_homa_flag=True`); valid rows remain for diabetes outcome. Skin thickness is not used in the unified schema; no change to that column.  
3. **NHANES:** LBDINLC has anomalous tiny values (e.g. 5.4e-79). **What we did:** The pipeline uses **LBXIN** (μU/mL) for insulin in HOMA calculations only; LBDINLC is not used. All NHANES cycles are loaded with LBXIN and merged on SEQN; add_homa_columns() and invalid_homa_flag logic use the correct variable.  
4. **October 2025 Blood Drive:** Many biomarker/methylation columns empty. **What we did:** Blood Drive / KiHealth patient files are not part of the M1 unified training dataset. When KiHealth patient TSV/CSV is used for predictions, missing A1c/Insulin/Glucose are handled by the prediction script (exclusion or imputation as documented); methylation columns are carried through in flags where present.

---

*End of KiHealth Data Summary.*
