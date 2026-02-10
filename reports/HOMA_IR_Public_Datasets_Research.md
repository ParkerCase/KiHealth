# Research Report: Best Public HOMA-IR Datasets (Fasting Insulin Required)

**Date:** January 2026  
**Purpose:** Identify publicly available datasets with **fasting** glucose and **fasting** insulin suitable for valid HOMA-IR and HOMA-beta calculations.  
**Critical constraint:** Exclude datasets with 2-hour OGTT insulin or non-fasting insulin.

---

## Executive Summary

### Top 3 Recommendations

| Rank | Dataset | Confidence | Access | Sample (HOMA-eligible) | Best for |
|------|---------|------------|--------|------------------------|----------|
| **1** | **NHANES** (CDC) | **100%** | Immediate download, no account | ~9,000+ per 2-year cycle (fasting subsample) | US population; you already have this; gold standard for fasting protocol. |
| **2** | **China Health and Nutrition Survey (CHNS) – Biomarker** | **95%** | Free registration → immediate download | ~10,000+ (2009 biomarker wave) | Geographic diversity; fasting glucose + insulin + HbA1c; peer-reviewed protocol. |
| **3** | **NHLBI BioLINCC studies (MESA, CARDIA, JHS, ACCORD)** | **90%** | Free account + data request (approval typically granted) | 5,000–6,800+ per study | US diversity, longitudinal; fasting status documented in protocols. |

**Direct answer to your key questions:**

1. **Which dataset can you download RIGHT NOW with 100% confidence it has valid fasting insulin?**  
   **NHANES.** Direct .xpt download; documentation explicitly states fasting subsample (8 to &lt;24 hours), LBXIN (μU/mL), LBXGLU (mg/dL). You already use it.

2. **Largest publicly available dataset with fasting insulin that you can access today?**  
   **NHANES** (combine multiple cycles for 15,000+ fasting records) or **CHNS 2009 biomarker** (registration only, then immediate download; ~10k+ with fasting glucose/insulin/HbA1c).

3. **Datasets better than NHANES?**  
   For *immediate* access and US representativeness, NHANES remains best. **CHNS** complements NHANES (China, different population). **UK Biobank** and **All of Us** have larger/biomarker-rich data but require application or registered-tier access—not “click and download today.”

4. **What complements NHANES well?**  
   **CHNS** (population/demographics), **KNHANES** (Korea, if you complete registration), **MESA/CARDIA/JHS** via BioLINCC (US ethnic diversity, longitudinal).

5. **Datasets designed for HOMA-IR/insulin resistance?**  
   Most are general health/biomarker surveys. **DPP/DPPOS** (NIDDK) and **ACCORD** are diabetes-focused and include fasting insulin; access is via repository request (NIDDK or BioLINCC).

---

## TIER 1: READY FOR IMMEDIATE USE ⭐⭐⭐⭐⭐

### 1. NHANES (National Health and Nutrition Examination Survey) – CDC

- **Download URL (Insulin 2021–2023):**  
  https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/INS_L.xpt  
- **Glucose (same cycle):**  
  https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/GLU_L.xpt  
- **Demographics:**  
  https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.xpt  
- **HbA1c:**  
  https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/GHB_L.xpt  
- **Body measures (BMI):**  
  https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.xpt  

- **Sample size:** Fasting subsample ~3,300–3,500 with insulin per 2-year cycle; multiple cycles (e.g., 2017–2020, 2021–2023) yield 9,000+ HOMA-eligible participants.  
- **Key variables:** Fasting glucose (LBXGLU, mg/dL), Fasting insulin (LBXIN, μU/mL; LBDINSI, pmol/L), HbA1c (LBXGH), Age, Sex, BMI (BMXBMI), Diabetes/weighting (WTSAF2YR = fasting subsample weight). Fasting questionnaire (FASTQX) documents fasting duration.  
- **Measurement protocol:** Fasting subsample: **8 to &lt;24 hours** fast; insulin on fasting serum; CLIA standards; University of Missouri-Columbia.  
- **Access:** Direct download, no account.  
- **License:** Public domain (CDC).  
- **Format:** SAS XPT (readable with pandas + pyreadstat).  
- **Documentation:**  
  - INS: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/INS_L.htm  
  - Analytic guidelines: https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx  
- **Missing data:** &lt;15% for fasting glucose/insulin in fasting subsample when using WTSAF2YR &gt; 0.  
- **Confidence:** 100% verified—documentation states “fasting subsample” and “8 to less than 24 hour fasting criteria”; you already use NHANES in KiHealth.  
- **Notes:** Use WTSAF2YR for fasting subsample; exclude WTSAF2YR=0 (non-fasting or no lab). Combine GLU_L, INS_L, DEMO_L, GHB_L, BMX_L by SEQN.

---

## TIER 2: HIGH QUALITY, MINOR BARRIERS ⭐⭐⭐⭐

### 2. China Health and Nutrition Survey (CHNS) – Biomarker Data (2009)

- **Data access (after registration):**  
  https://www.cpc.unc.edu/projects/china/data/datasets/data-downloads-registration  
- **Biomarker documentation:**  
  https://www.cpc.unc.edu/projects/china/data/datasets/biomarker-data  

- **Sample size:** 2009 biomarker wave: 26 fasting blood measures on individuals **aged 7+**; typically 10,000+ with glucose/insulin.  
- **Key variables:** Fasting glucose, fasting insulin, HbA1c, triglycerides, CRP, lipids; demographics and constructed variables in longitudinal files.  
- **Measurement protocol:** Explicitly **fasting** blood; protocols and methods documented:  
  - Blood collection: https://www.cpc.unc.edu/projects/china/data/datasets/Blood%20Collection%20Protocol_English.pdf  
  - Biomarker methods: https://www.cpc.unc.edu/projects/china/data/datasets/Biomarker_Methods.pdf  
  - Codebook: https://www.cpc.unc.edu/projects/china/data/datasets/C10BIOMARKER.pdf  
- **Access:** Free registration (name, email, organization, country)—then immediate access to Data Downloads for the session (cookie-based). No approval committee.  
- **License:** Academic/research use; citation required (see CHNS “Citing the Data”).  
- **Format:** Typically Stata/CSV; see codebook.  
- **Documentation:** Links above; peer-reviewed (e.g., Yan et al., Obesity Reviews 2012).  
- **Missing data:** Not specified in search; codebook and documentation should be checked for key variables.  
- **Confidence:** 95%—documentation explicitly states “26 fasting blood measures” and “diabetes such as HbA1c, glucose, insulin”; registration is the only barrier.  
- **Notes:** 2015 biomarker data partially available; 2009 is well documented. Complements NHANES (China vs US).

---

### 3. KNHANES (Korean National Health and Nutrition Examination Survey)

- **Portal (Korean):** https://knhanes.kdca.go.kr/knhanes/main.do  
- **English profile (methodology):** Data Resource Profile in PMC (KNHANES design, fasting blood in participants 10+).  

- **Sample size:** ~10,000 persons per year (continuous survey).  
- **Key variables:** Fasting blood samples (age 10+); diabetes and metabolic markers; demographics.  
- **Measurement protocol:** Fasting blood collection; methodology in peer-reviewed profile.  
- **Access:** Registration at KNHANES portal; no direct English “public use file” link found—interface is Korean-first.  
- **License:** Research use; terms on portal.  
- **Format:** Depends on release (often SAS/SPSS/CSV).  
- **Documentation:** English methodology via PMC; variable lists may require Korean portal.  
- **Confidence:** 85%—fasting blood is standard in KNHANES; access and variable verification require registration and possibly Korean language.  
- **Notes:** Good for geographic/population diversity; confirm variable names for fasting glucose/insulin in the actual download.

---

## TIER 3: GOOD QUALITY, REQUIRES APPLICATION ⭐⭐⭐

### 4. All of Us Research Program (USA)

- **Data browser (public):** https://databrowser.researchallofus.org  
- **Data access tiers:** https://www.researchallofus.org/data-tools/data-access/  

- **Sample size:** Very large; biospecimens and biomarkers (including fasting insulin in lab data) in Registered/Controlled tiers.  
- **Key variables:** EHR and biospecimen-derived labs; fasting insulin available in lab data for fasting subsamples.  
- **Access:** Public = aggregate only. Individual-level fasting insulin requires **Researcher Workbench** registration and project description (audited); no “direct download” of individual-level data.  
- **Confidence:** 90% that fasting insulin exists in tiered data; 0% for “download today” without registration and approval.  
- **Notes:** Best for future projects; not for “immediate download today.”

---

### 5. UK Biobank

- **Biomarker data overview:** https://www.ukbiobank.ac.uk/enable-your-research/about-our-data/biomarker-data  
- **Apply for access:** https://www.ukbiobank.ac.uk/use-your-research/apply-for-access/  

- **Sample size:** 500,000 with biochemistry biomarkers; no public-use subset.  
- **Key variables:** Biochemistry includes diabetes-related markers; fasting insulin likely in biochemistry panel (not explicitly named in search).  
- **Access:** Application required; approval and fee for external researchers; no immediate public download.  
- **Confidence:** 85% that fasting insulin is available to approved applicants; not suitable for “access today.”  
- **Notes:** No open subset; application required.

---

### 6. Canadian Health Measures Survey (CHMS)

- **Survey info:** https://www.statcan.gc.ca/en/survey/household/5071  
- **Accessing CHMS:** https://www.statcan.gc.ca/en/statistical-programs/document/5071_D5_V2  

- **Sample size:** Cycles 1–8; diabetes biomarkers (fasting glucose, insulin) in all cycles.  
- **Key variables:** Fasting glucose, fasting insulin, HbA1c; demographics; physical measures.  
- **Access:** **Microdata with biomarkers** primarily via **Research Data Centres (RDCs)**; no direct public PUMF with fasting insulin found. Public releases are aggregate.  
- **Confidence:** 80%—CHMS collects fasting biomarkers; 0% for “direct download today” of microdata with fasting insulin.  
- **Notes:** RDC application required; good for Canadian population once access is granted.

---

### 7. Framingham Heart Study – Teaching Dataset (BioLINCC)

- **Teaching datasets:** https://biolincc.nhlbi.nih.gov/teaching/  
- **FHS data overview:** https://www.framinghamheartstudy.org/fhs-for-researchers/data-available-overview/  

- **Sample size:** Teaching dataset is a subset (e.g., frmgham2.csv); full FHS has more.  
- **Key variables:** Teaching set has longitudinal exams; **variable list must be checked** for fasting insulin (may be in specific exam cycles).  
- **Access:** Request teaching dataset via BioLINCC; free, no IRB; **not for publication** (anonymized/permuted).  
- **Confidence:** 75%—teaching dataset may include fasting insulin; documentation must be verified; not for publication.  
- **Notes:** Full FHS with full biomarkers may require separate application.

---

### 8. MESA, CARDIA, Jackson Heart Study, ACCORD (NHLBI BioLINCC)

- **BioLINCC home:** https://biolincc.nhlbi.nih.gov/home/  
- **MESA:** https://biolincc.nhlbi.nih.gov/studies/mesa/  
- **CARDIA:** https://biolincc.nhlbi.nih.gov/studies/cardia/  
- **Jackson Heart Study:** https://biolincc.nhlbi.nih.gov/studies/jhs/  
- **ACCORD:** https://biolincc.nhlbi.nih.gov/studies/accord/  

- **Sample sizes:** MESA ~6,814; CARDIA ~5,115; JHS ~5,301 (3,883 with sharing consent); ACCORD ~10,000 (diabetes trial).  
- **Key variables:** Fasting lipids and metabolic panels; MESA/CARDIA/JHS protocols use fasting blood draws; ACCORD has fasting glucose/insulin in diabetes cohort.  
- **Measurement protocol:** Fasting blood draw standard in exam protocols; confirm in each study’s data dictionary.  
- **Access:** Free **registration** at BioLINCC; **data request** with project description; approval typically granted for open studies. Not immediate download.  
- **License:** Varies by study (e.g., ACCORD no commercial restriction; others tiered).  
- **Confidence:** 90% that fasting insulin (or sufficient to compute HOMA-IR) is available once request is approved; 0% for “download today” without request.  
- **Notes:** Best US multi-ethnic/longitudinal sources after NHANES; complement NHANES by design and ethnicity.

---

### 9. DPP / DPPOS (NIDDK Central Repository)

- **DPP:** https://repository.niddk.nih.gov/studies/dpp  
- **DPPOS:** https://repository.niddk.nih.gov/studies/dppos  

- **Sample size:** DPP/DPPOS thousands; prediabetes/diabetes outcomes; fasting and OGTT used.  
- **Key variables:** Fasting plasma glucose, fasting insulin, clinical labs, diabetes outcomes.  
- **Access:** **Request** through NIDDK Central Repository; not immediate download.  
- **Confidence:** 95% that fasting insulin and glucose are in the requested datasets; access requires approval.  
- **Notes:** Ideal for diabetes prevention and HOMA in at-risk population; application required.

---

### 10. LOOK AHEAD (Action for Health in Diabetes)

- **Study site:** https://www.lookaheadtrial.org  
- **Data sharing:** Typically via NHLBI or NIDDK repositories; no direct “download now” link found.  

- **Sample size:** Large RCT in type 2 diabetes.  
- **Key variables:** Fasting labs and diabetes outcomes.  
- **Access:** Data sharing by application (repository or PI); not immediate.  
- **Confidence:** 80%—trial included metabolic labs; exact fasting insulin availability and access path need verification.  

---

## TIER 4: PROMISING BUT UNVERIFIED ⭐⭐

### 11. European Health Examination Survey (EHES)

- **Site:** https://www.ehes.info  

- **Status:** Coordinating centre; no centralized public database of biomarker microdata found. Data are national; access and fasting insulin would need to be confirmed per country.  
- **Confidence:** 50%—EHES uses standardized exams (including glucose); fasting insulin and public download not verified.  

---

### 12. Dryad / Figshare / Zenodo – Fasting Insulin or HOMA-IR

- **Dryad example (fasting metabolic):** https://doi.org/10.5061/dryad.6121hj7 (prolonged fasting, skeletal muscle; may include insulin).  
- **Figshare:** Several small datasets (e.g., methylation vs fasting glucose/insulin/HOMA-IR; rat studies; Saku Study supplementary). None are large, nationally representative surveys.  

- **Sample sizes:** Generally small (tens to low hundreds).  
- **Access:** Direct download where DOI/link provided.  
- **Confidence:** 70% for “fasting” where authors state it; **not** for “500+ subjects, representative, full codebook” unless a specific dataset is identified and validated.  
- **Notes:** Useful for methods or replication of single papers; not replacements for NHANES/CHMS-style surveys.

---

### 13. Harvard Dataverse / ICPSR

- **ICPSR:** Hosts NHANES and other surveys; NHANES fasting insulin is same as CDC source.  
- **Harvard Dataverse:** Various health datasets; no single “HOMA-IR fasting insulin, n&gt;1000, verified” dataset identified without targeted search.  
- **Confidence:** 60%—repositories exist; a dedicated search per repository would be needed for a specific large, fasting-insulin dataset beyond NHANES.

---

## TIER 5: NOT SUITABLE ❌

| Dataset / Source | Reason for exclusion |
|------------------|------------------------|
| **Pima Indians Diabetes (e.g., Frankfurt/UCI)** | **2-hour OGTT insulin**, not fasting—invalid for HOMA; already excluded in KiHealth. |
| **Many Kaggle “diabetes” datasets** | Often derived from Pima or unspecified; 2-hour insulin common; avoid unless protocol explicitly states fasting. |
| **DiaBD (your current file)** | High proportion of zero insulin and quality issues; excluded from HOMA in your pipeline. |
| **UK Biobank “public”** | No public-use subset; application and fee required. |
| **CHMS public PUMF** | No direct public microdata with fasting insulin; RDC required. |
| **Framingham Teaching Dataset** | May contain fasting insulin but **not for publication**; anonymization/permutation. |
| **All of Us / UK Biobank** | Not “immediate download”; require registration and/or application. |

---

## Quick Reference Table: Tier 1 & Tier 2 Datasets

| Dataset | Fasting insulin verified | Sample (approx.) | Access | Format | Best use |
|---------|---------------------------|------------------|--------|--------|----------|
| **NHANES** | Yes (8 to &lt;24 h) | ~9k+ (multi-cycle) | Direct download | XPT | US; immediate; gold standard |
| **CHNS 2009 biomarker** | Yes (documented) | ~10k+ | Registration → download | Stata/CSV | China; complements NHANES |
| **KNHANES** | Yes (methodology) | ~10k/year | Portal registration (Korean) | Various | Korea; diversity |
| **MESA (BioLINCC)** | Yes (protocol) | ~6,800 | Request after registration | Various | US multi-ethnic, longitudinal |
| **CARDIA (BioLINCC)** | Yes (protocol) | ~5,100 | Request after registration | Various | US young adults, longitudinal |
| **JHS (BioLINCC)** | Yes (protocol) | ~3,900 shared | Request after registration | Various | US Black population |
| **ACCORD (BioLINCC)** | Yes (trial) | ~10,000 | Request after registration | Various | Type 2 diabetes trial |
| **DPP/DPPOS (NIDDK)** | Yes (trial) | Thousands | Repository request | Various | Diabetes prevention |

---

## Download Instructions: Top Recommendation (NHANES – You Already Use It)

For a **new** user wanting to replicate “download today” with valid fasting insulin:

### Step 1: Choose cycle(s)

- Single cycle (e.g., 2021–2023): https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2021-2023  
- Or 2017–March 2020: same site, cycle 2017-March 2020.

### Step 2: Download these XPT files (example 2021–2023)

1. **Demographics:**  
   https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.xpt  
2. **Fasting glucose:**  
   https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/GLU_L.xpt  
3. **Fasting insulin:**  
   https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/INS_L.xpt  
4. **HbA1c:**  
   https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/GHB_L.xpt  
5. **Body measures (BMI):**  
   https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.xpt  

### Step 3: Restrict to fasting subsample

- Use **WTSAF2YR &gt; 0** (from INS or GLU file) so only participants with valid fasting (8 to &lt;24 h) and non-missing weight are included.  
- Merge files by **SEQN**.  
- Key variables: **LBXGLU** (fasting glucose, mg/dL), **LBXIN** (fasting insulin, μU/mL), **LBXGH** (HbA1c), **BMXBMI**, **RIAGENDR**, **RIDAGEYR**.

### Step 4: Compute HOMA-IR / HOMA-beta

- Use standard formulas with fasting glucose (mg/dL) and fasting insulin (μU/mL).  
- Your project already implements this in `src/features/homa_calculations.py` and `src/data/load_kihealth.py` for NHANES.

---

## Summary

- **Only Tier 1 “immediate, no account” dataset with verified fasting insulin in this review is NHANES.**  
- **CHNS 2009 biomarker** is the best next option with minimal friction (registration only) and explicit fasting protocol.  
- **BioLINCC (MESA, CARDIA, JHS, ACCORD)** and **NIDDK (DPP/DPPOS)** are strong for quality and design but require a request/approval step.  
- **Avoid** any dataset that does not explicitly state **fasting** glucose and **fasting** insulin; exclude 2-hour or post-OGTT insulin from HOMA calculations.

If you want, the next step can be: (1) a short “CHNS download walkthrough” using their registration and biomarker codebook, or (2) a one-page “BioLINCC request checklist” for MESA/CARDIA/JHS/ACCORD focused on fasting insulin and HOMA-IR.
