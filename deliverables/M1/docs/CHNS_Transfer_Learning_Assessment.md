# CHNS Biomarker File: Transfer Learning Assessment

**File:** `Diabetes-KiHealth/TL-KiHealth/CHNS/biomarker_09.sas7bdat`  
**Wave:** 2009  
**Assessed:** January 2026

---

## 1. File Summary

| Metric | Value |
|--------|--------|
| **Rows** | 9,549 |
| **Columns** | 49 (biomarkers + ID + wave) |
| **Unique individuals (IDind)** | 9,549 |
| **Key HOMA variables** | INS, GLUCOSE, GLUCOSE_MG, HbA1c |

---

## 2. HOMA-Relevant Variables (Verified in File)

| Variable | Non-null | Missing % | Mean | Min–Max | Interpretation |
|----------|----------|-----------|------|---------|----------------|
| **INS** | 9,480 | 0.7% | 14.55 | 0.06–639.87 | Fasting insulin (μU/mL / mIU/L per CHNS codebook) |
| **GLUCOSE** | 9,498 | 0.5% | 5.36 | 2.76–23.24 | Fasting glucose (mmol/L) |
| **GLUCOSE_MG** | 9,498 | 0.5% | 96.45 | 49.68–418.32 | Fasting glucose (mg/dL) — **use for HOMA** |
| **HbA1c** | 9,452 | 1.0% | 5.60 | 2.70–30.00 | HbA1c (%) |
| **Glu_field** | 9,490 | 0.6% | 5.32 | — | Field glucose (mmol/L); alternate to GLUCOSE |

**HOMA-valid rows (INS > 0 and GLUCOSE > 0):** 9,479 (99.3%). No epidemic of zeros like DiaBD; values are physiologically plausible (fasting insulin mean ~14.5 μU/mL).

**Fasting status:** CHNS 2009 biomarker data are explicitly **fasting blood measures** (26 fasting blood measures, individuals aged 7+). Documentation: [CHNS Biomarker Data](https://www.cpc.unc.edu/projects/china/data/datasets/biomarker-data). **Suitable for HOMA-IR and HOMA-beta.**

---

## 3. What’s Missing for Your Pipeline

Your unified schema (`load_kihealth.py`) expects at minimum:

- **patient_id** → ✅ **IDind** (map as string or int)
- **glucose_mg_dl** → ✅ **GLUCOSE_MG**
- **insulin_uU_ml** → ✅ **INS**
- **homa_ir / homa_beta** → ✅ Compute from GLUCOSE_MG and INS
- **hba1c_percent** → ✅ **HbA1c**
- **age_years** → ❌ **Not in this file**
- **sex** → ❌ **Not in this file**
- **bmi_kg_m2** → ❌ **Not in this file**
- **diabetes_status** → ❌ **Not in this file** (can be derived from HbA1c/glucose cutoffs if needed)

**Conclusion:** `biomarker_09.sas7bdat` is **biomarker-only**. It has no demographics or anthropometry. For transfer learning with the same feature set as NHANES (age, sex, BMI, glucose, insulin, etc.), you must **merge with CHNS demographic and anthropometry files** (e.g., individual roster, exam data) on **IDind** and wave. CHNS provides longitudinal and roster files via the same Data Downloads (after registration).

---

## 4. Is CHNS Usable for Transfer Learning?

**Yes, with one condition.**

### Strengths for transfer learning

1. **Valid HOMA inputs:** Fasting glucose and fasting insulin, documented protocol, same formulas as NHANES. GLUCOSE_MG and INS can be mapped directly to your schema.
2. **Sample size:** ~9.5k individuals with ~9.5k HOMA-valid rows — comparable to your NHANES HOMA-eligible sample (~9k).
3. **Data quality:** &lt;1% missing for INS, GLUCOSE, HbA1c; 99.3% have both INS &gt; 0 and GLUCOSE &gt; 0; no zero-insulin artifact.
4. **Domain shift:** China vs US (NHANES) — different population, diet, and healthcare. Good for testing **generalizability** of a model trained on NHANES (source) and evaluated or fine-tuned on CHNS (target).
5. **Same outcome space:** HOMA-IR, HOMA-beta, HbA1c, and (if you define it) diabetes/by glucose cutoffs — aligned with your current outcomes.

### Condition: merge demographics

- For **feature-aligned** transfer learning (same covariates as NHANES: age, sex, BMI, glucose, insulin, etc.), you need **age, sex, and BMI** for CHNS individuals.
- Obtain them from CHNS **longitudinal** or **individual/roster** files (same Data Downloads), merge on **IDind** (and wave if multi-wave).
- After merge, you can:
  - Train on NHANES (source) and evaluate on CHNS (target), or
  - Fine-tune on CHNS after pre-training on NHANES, or
  - Use CHNS as an additional source domain in multi-source TL.

### Minimal TL without demographics

- You could use CHNS for **outcome-only** transfer (e.g., predict HOMA-IR from glucose + insulin only) or for **calibration/validation** of HOMA in a different population, without age/sex/BMI. That’s a narrower but still valid use.

---

## 5. Recommendation

| Use case | Verdict |
|----------|--------|
| **HOMA-IR / HOMA-beta from fasting glucose + insulin** | ✅ Usable as-is; compute HOMA from GLUCOSE_MG and INS. |
| **Transfer learning with full covariate set (age, sex, BMI, glucose, insulin, …)** | ✅ Usable **after** merging CHNS demographic/anthro data on IDind. |
| **Inclusion in `load_kihealth.py` unified dataset** | ✅ Recommended once demographics are available; set `homa_analysis_eligible=True` for CHNS (fasting protocol verified). |

**Next steps:**

1. Download CHNS demographic/anthro file(s) that contain **IDind**, **age**, **sex**, **BMI** (and optionally diabetes/medication) for the 2009 wave.
2. Merge with `biomarker_09` on **IDind** (and wave if needed).
3. Map merged data to `UNIFIED_SCHEMA` (patient_id←IDind, glucose_mg_dl←GLUCOSE_MG, insulin_uU_ml←INS, age_years, sex, bmi_kg_m2 from merged file, dataset_source="chns_2009").
4. Add a `load_chns()` (or similar) in `load_kihealth.py` and include CHNS in the unified build with `homa_analysis_eligible=True`.

---

## 7. UNC Dataverse “Individual-Level Data” — Which Files to Download

From **China Health and Nutrition Survey, 2019, Individual-Level Data** (UNC Dataverse, doi: 10.15139/S3/9PQ5KV), these files are **worth downloading** for age, sex, BMI and merge with `biomarker_09`:

### Priority 1: Essential for transfer learning (age, sex, BMI)

| File | Size | Purpose | Why download |
|------|------|---------|----------------|
| **pexam_00.sas7bdat** | 191.8 MB | **Physical exam** | Height, weight, BMI; one row per person per wave. Merge on IDind + wave (filter wave=2009 for biomarker_09). |
| **pexam_00.pdf** | 222 KB | Codebook for pexam | Variable names (e.g. height, weight, BMI), units, wave. |
| **subi_12.sas7bdat** | 2.1 MB | **Subject/individual** | Typically has IDind, **age** (or DOB), **sex (GENDER)**. Merge on IDind. |
| **subi_00.pdf** | 134 KB | Codebook for subi | Confirm IDind, age, sex variable names. |
| **mast_pub_12.sas7bdat** | 2.8 MB | **Master individual ID** | IDind, one observation per respondent (1989–2015); may have gender, DOB. Good for merge key and demographics. |
| **mast_pub_12.pdf** | 134 KB | Codebook for mast | Confirm IDind, wave, gender, DOB. |

**Merge strategy:** Join `biomarker_09` (wave 2009) with **pexam_00** on IDind + wave=2009 for BMI/height/weight; join with **subi_12** or **mast_pub_12** on IDind for age and sex. Confirm variable names in the PDF codebooks (e.g. GENDER vs sex, DOB vs age).

### Priority 2: Optional (health outcomes, diabetes)

| File | Size | Purpose | Why optional |
|------|------|---------|----------------|
| **hlth_12.sas7bdat** | 71.3 MB | Health | Self-reported health, possibly diabetes/medication; useful for diabetes_status if not deriving from HbA1c/glucose. |
| **hlth_12.pdf** | 171 KB | Codebook | Check for diabetes/glucose-related variables. |

### Not needed for your current goal (age, sex, BMI + HOMA)

- **c12diet** — You already have it; diet only, no demographics.
- **birth_12, busi_12, carec_12, educ_12, emw_12, farmg_12, fishi_12, ins_12, jobs_12, livei_12, media_00, pact_12, preg_12, pstress_12, rst_12, timea_12**, etc. — Topic-specific (birth, business, education, employment, etc.). Download only if you need those covariates later.

**Note:** The Dataverse release is “2019” (publication year); files use “_12” (through 2012 or wave 12). Longitudinal files usually include **wave 2009**, so you can filter to wave=2009 to match `biomarker_09`.

---

## 8. Inspection of Downloaded CHNS Files (Post-Download)

All recommended files were inspected. Summary below.

### 8.1 File inventory

| File | Rows | Cols | Key variables |
|------|------|------|----------------|
| **biomarker_09.sas7bdat** | 9,549 | 49 | IDind, wave(2009), INS, GLUCOSE_MG, HbA1c |
| **pexam_00.sas7bdat** | 110,449 | 206 | IDind, **WAVE**, **HEIGHT**, **WEIGHT**, SYSTOL1–3, DIASTOL1–3 |
| **subi_12.sas7bdat** | 14,834 | 18 | IDind, WAVE, I9, I11, I12, I13, I14 (no wave 2009) |
| **mast_pub_12.sas7bdat** | 39,674 | 9 | **Idind** (note: capital I), **GENDER**, **WEST_DOB_Y**, MOON_DOB_Y |
| **hlth_12.sas7bdat** | 127,761 | 77 | IDind, wave, M23–M52 (health questions) |

### 8.2 Overlap with biomarker_09 (wave 2009)

| Source | Filter | Overlap with biomarker_09 | Use for |
|--------|--------|----------------------------|--------|
| **pexam_00** | WAVE = 2009 | **9,516 of 9,549** | HEIGHT (cm), WEIGHT (kg) → **BMI** |
| **mast_pub_12** | — (one row per person) | **9,549 of 9,549** | **GENDER**, **WEST_DOB_Y** → age, sex |
| **subi_12** | WAVE = 2009 | **0** (subi_12 has waves 1989–2006 only; no 2009) | **Do not use** for 2009 cohort |
| **hlth_12** | wave = 2009 | **9,516 of 9,549** | Optional: health/diabetes (M* vars) |

**Conclusion:** Use **pexam_00** (wave=2009) for BMI; use **mast_pub_12** for age and sex. **subi_12** does not contain wave 2009 — ignore for this cohort.

### 8.3 Variable details

**pexam_00 (wave = 2009)**  
- **HEIGHT**: mean 156.5 cm, range 39–188.6 cm (use only plausible, e.g. 100–220 cm, for BMI).  
- **WEIGHT**: mean 56.4 kg, range 2.6–111.6 kg.  
- **Computed BMI** (WEIGHT / (HEIGHT/100)²): mean 22.45, range 11.43–42.72.  
- Merge key: **IDind** + **WAVE** = 2009.

**mast_pub_12**  
- **Idind**: same person ID as biomarker_09 **IDind** (all 9,549 biomarker IDs present; note mast uses **Idind** with lowercase “d”).  
- **GENDER**: 1 = Male, 2 = Female (no NaN in overlap).  
- **WEST_DOB_Y**: birth year; non-null for 39,651; use **age = 2009 − WEST_DOB_Y** for biomarker wave 2009.  
- Merge key: **Idind** (align with biomarker_09 **IDind**).

**hlth_12 (wave = 2009)**  
- 9,516 of 9,549 biomarker IDs have a health record.  
- Variables M23–M52 are health/medication items; check codebook (hlth_12.pdf) for diabetes/glucose if you want **diabetes_status** from self-report.

### 8.4 Merge strategy for transfer learning

1. Start with **biomarker_09** (9,549 rows).  
2. Join **mast_pub_12** on `biomarker_09.IDind == mast_pub_12.Idind` → add **GENDER**, **WEST_DOB_Y**.  
   - Map **sex**: GENDER 1 → Male (1), GENDER 2 → Female (0) per your schema.  
   - Compute **age_years** = 2009 − WEST_DOB_Y.  
3. Join **pexam_00** on `biomarker_09.IDind == pexam_00.IDind` and `pexam_00.WAVE == 2009` → add **HEIGHT**, **WEIGHT**.  
   - Compute **bmi_kg_m2** = WEIGHT / (HEIGHT/100)²; drop or flag implausible HEIGHT/WEIGHT (e.g. HEIGHT &lt; 100 or &gt; 220 cm).  
4. Optional: join **hlth_12** on IDind + wave=2009 for diabetes/health if needed.  
5. Map to unified schema: patient_id←IDind, glucose_mg_dl←GLUCOSE_MG, insulin_uU_ml←INS, hba1c_percent←HbA1c, add homa_ir/homa_beta from GLUCOSE_MG and INS, dataset_source="chns_2009", homa_analysis_eligible=True.

**Expected merged N:** 9,516 (limited by pexam_00 wave=2009 overlap); 33 biomarker individuals without pexam 2009 can be dropped or kept with missing BMI.

---

## 6. Quick Reference: Variable Mapping (Biomarker File Only)

| Unified schema | CHNS biomarker_09 | Notes |
|----------------|--------------------|--------|
| patient_id | IDind | Use as string for consistency |
| glucose_mg_dl | GLUCOSE_MG | Fasting, mg/dL |
| insulin_uU_ml | INS | Fasting, μU/mL (mIU/L) |
| hba1c_percent | HbA1c | % |
| age_years | *(merge from roster/longitudinal)* | — |
| sex | *(merge from roster/longitudinal)* | — |
| bmi_kg_m2 | *(merge from anthropometry)* | — |
| diabetes_status | *(derive from HbA1c ≥6.5% or glucose cutoffs, or merge)* | Optional |
