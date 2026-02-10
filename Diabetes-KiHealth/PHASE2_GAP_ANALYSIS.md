# Phase 2 vs Current Implementation — Gap Analysis

**Purpose:** Clarify what is already in place (often from M1 + the current prediction pipeline) vs what remains for Phase 2 scope.

---

## Task 2.0: Transfer Learning Foundation

### 2.0.1 NHANES Data Preparation — **Largely done (M1)**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Merge glucose, insulin, HbA1c, demographics on patient ID (SEQN) | Done. `load_kihealth.py` merges DEMO, GLU, INS, GHB, BMX on SEQN per NHANES cycle. |
| HOMA-IR = (Fasting Insulin × Fasting Glucose) / 405 | Done. `src/features/homa_calculations.py` (Matthews formula). |
| HOMA-beta = 360 × Fasting Insulin / (Fasting Glucose − 63) | Done. Same module (Phase 2 doc uses 20/(glucose−3.5) in mmol/L; 63 mg/dL is equivalent). |
| Filter valid fasting samples (weights) | Done. `homa_analysis_eligible`, `invalid_homa_flag`; WTSAF2YR/survey weights in unified schema where available. |
| Handle missing values and outliers | Done. Invalid HOMA flagged; missing imputed with medians at prediction time. |
| Analysis-ready dataset 5,000–10,000 patients | Exceeded. **38,509** total; **33,078** HOMA-eligible used for training (NHANES + CHNS + C-Pep, etc.). |

**Deliverable:** Preprocessed NHANES dataset — **Done** (`data/processed/unified_kihealth.csv`).

---

### 2.0.2 Pre-train Foundation Model — **Partially done**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Train on public data (Random Forest / XGBoost) | **Done.** `kihealth_diabetes_prediction.py` trains **XGBoost** on 33,078 HOMA-eligible samples (RF fallback if no XGBoost). |
| Features: HbA1c, glucose, insulin, HOMA-IR, HOMA-beta, age, BMI, gender, race | **Done.** Plus HBP, C-peptide, Ins/C-peptide ratio. |
| Target: diabetes diagnosis or progression | **Done.** Target = `diabetes_status` (glucose ≥126 or HbA1c ≥6.5). |
| Feature importance rankings | **Not done.** No importance exported or documented in script. |
| HOMA-IR threshold (e.g. >2.5) | **Not done.** No formal threshold doc or threshold-based rule in pipeline. |
| Document baseline performance metrics | **Not done.** No AUC, sensitivity/specificity, or hold-out validation in the script. |

**Deliverable:** Pre-trained model — **Done.** Performance documentation — **Not done.**

---

### 2.0.3 Fine-tune on Beta Score Data — **Not done**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Add Beta Score as novel feature | **Not done.** No Beta Score (or % methylated) as a **model feature**; only in at-risk flags as optional display. |
| Fine-tune weights on 160-patient KiHealth dataset | **Not done.** Model is trained only on public data; applied directly to KiHealth (no second-stage fine-tuning). |
| Interaction terms (Beta Score × HOMA-IR, × HOMA-beta, × HbA1c) | **Not done.** No interaction terms in features. |
| Compare transfer learning vs train-from-scratch on KiHealth only | **Not done.** No comparison. |
| Validate that transfer learning improves predictions | **Not done.** No formal comparison or validation. |

**Deliverable:** Fine-tuned Beta Score model — **Not done.**

---

### 2.0.4 Methodology Documentation — **Partial**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Separate foundation training (public) from clinical validation (KiHealth) | **Partial.** README/M1 docs describe data sources; no single “transfer learning methodology” doc. |
| Transfer learning rationale and methodology | **Partial.** Described in M1/PHASE1 and in script docstring; not a dedicated deliverable. |
| Reproducibility procedures | **Partial.** Scripts and paths documented; no single reproducibility checklist. |
| FDA/CLIA submission discussions | **Not done.** No submission-ready methodology doc. |

**Deliverable:** Transfer learning methodology doc — **Partial** (could be formalized).

---

## Task 2.1: Model Training — **Partially done**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Combine pre-trained foundation with Beta Score | **No.** Foundation only; no Beta Score in model. |
| KiHealth “high 80s” AUC as benchmark | **Not measured.** No AUC reported. |
| Cross-validation to prevent overfitting | **Not done.** Single fit on full training set. |
| Multiple algorithms (RF, XGBoost, etc.) | **Partial.** XGBoost primary; RF only as fallback if XGBoost missing. No comparison. |

**Deliverable:** Trained model — **Done.** Documented performance vs benchmark — **Not done.**

---

## Task 2.2: Feature Engineering — **Partial**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| HOMA-IR, HOMA-beta (learned from NHANES) | **Done.** In features and pipeline. |
| Interaction terms (Beta×HOMA-IR, Beta×HOMA-beta, Beta×HbA1c, Age×HOMA-IR, BMI×HOMA-IR) | **Not done.** No interaction terms. |
| Differential weighting (e.g. Beta 30–35%, HOMA-IR 20–25%, …) | **Not done.** Model learns weights implicitly; no fixed clinical weighting. |
| Questionnaire-derived scores (mood, metabolic, lifestyle) | **Not done.** No questionnaire risk scores in pipeline. |

**Deliverable:** Feature engineering pipeline — **Partial** (core biomarkers + HOMA; no interactions or questionnaire scores).

---

## Task 2.3: Model Optimization — **Not done**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Hyperparameter tuning | **Not done.** Fixed XGBoost params (n_estimators=200, max_depth=6, etc.). |
| Feature selection from importance | **Not done.** |
| Threshold optimization (sensitivity vs specificity) | **Not done.** Fixed 0.5 and tier rules (e.g. ≥0.25 for “Elevated”). |
| Target AUC > 0.85 | **Not measured.** No AUC reported. |

**Deliverable:** Optimized model meeting AUC target — **Not done.**

---

## Task 2.4: Interpretable Output Format — **Partially done**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Risk categories (Low / Medium / High) with percentiles | **Done.** `risk_tier`: High / Moderate / Low / Elevated (model). |
| Risk % (0–100 scale) | **Done.** `predicted_diabetes_risk_pct` (Diabetic=99.9, Prediabetic=blank, Non-diabetic=model %). |
| Feature importance breakdown (“Beta 35%, HbA1c 25%…”) | **Not done.** No importance in output. |
| Confidence intervals for predictions | **Not done.** |
| Trend visualization for longitudinal tracking | **Not done.** |

**Deliverable:** Interpretable output spec — **Partial** (categories and risk %; no importance or CI).

---

## Task 2.5: Hold-out Validation — **Not done**

| Phase 2 requirement | Current state |
|---------------------|----------------|
| Split KiHealth: 70% train / 15% val / 15% test | **Not done.** No KiHealth split; model trained only on public data. |
| Performance on held-out test set | **Not done.** No hold-out. |
| Compare to KiHealth baseline | **Not done.** |
| Statistical significance testing | **Not done.** |
| Population-specific calibration | **Not done.** |

**Deliverable:** Validation report — **Not done.**

---

## Summary

- **Already in place (M1 + current pipeline):**  
  - Task 2.0.1 (data prep, merge on SEQN, HOMA, 33k+ training samples).  
  - Most of 2.0.2 (pre-train XGBoost on public data, correct features and target).  
  - Parts of 2.1 (single trained model), 2.2 (HOMA + core features), 2.4 (risk tiers and risk %).

- **Partially done:**  
  - 2.0.2 (no feature importance or baseline metrics doc).  
  - 2.0.4 (methodology in M1/docs but not a single TL methodology deliverable).  
  - 2.2 (no interactions, no questionnaire scores).  
  - 2.4 (no importance breakdown, no CI, no trend viz).

- **Not done:**  
  - 2.0.3 (Beta Score as feature, fine-tuning on 160 patients, interaction terms, TL vs from-scratch comparison).  
  - 2.3 (tuning, feature selection, threshold optimization, AUC target).  
  - 2.5 (hold-out split, test-set metrics, baseline comparison, significance, calibration).

So: **we have already done a lot of the data and “foundation model” side of Phase 2 (2.0.1 and much of 2.0.2/2.1), but not the Beta Score integration, fine-tuning, formal optimization, or validation (2.0.3, 2.3, 2.5).**
