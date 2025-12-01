# EXTERNAL VALIDATION STUDY PROTOCOL
## DOC Model - Bergman Clinics Prospective Cohort

**Protocol Version:** 1.0  
**Date:** 2025-12-01  
**Status:** DRAFT - Awaiting review by Dr. Moen

---

### Study Title
Prospective External Validation of a Machine Learning Model for Predicting 
4-Year Knee Replacement Risk in Dutch Patients with Osteoarthritis

### Principal Investigator
Dr. Maarten Moen, Chief Medical Officer, NOC*NSF / Bergman Clinics

### Study Design
Prospective observational cohort study

---

## BACKGROUND

### Model to be Validated
- **Name:** Digital Osteoarthritis Counseling (DOC) Model
- **Development Dataset:** Osteoarthritis Initiative (OAI), USA, N=4,796
- **Outcome:** Total knee replacement within 4 years
- **Performance:** AUC=0.862, Brier score=0.092
- **PROBAST Assessment:** LOW RISK OF BIAS

### Rationale for External Validation
- OAI is US-based; generalizability to European population unknown
- Different healthcare systems (US vs Netherlands)
- Temporal validation (model trained on 2004-2014 data, validation in 2025+)
- Geographic validation (US vs Netherlands)

---

## OBJECTIVES

### Primary Objective
Assess external validity of the DOC model in a Dutch orthopedic clinic population by:
1. Evaluating discrimination (AUC)
2. Assessing calibration (Brier score, calibration plots)

### Secondary Objectives
1. Compare performance across age groups (<60 vs ≥60 years)
2. Compare performance by sex (male vs female)
3. Compare performance by KL grade severity (grades 2-3 vs grade 4)
4. Assess clinical utility via decision curve analysis

---

## METHODS

### Study Population

**Inclusion Criteria:**
- Age 45-79 years
- Diagnosis of knee osteoarthritis (clinical or radiographic)
- New patient or existing patient presenting for OA evaluation
- Able to provide informed consent

**Exclusion Criteria:**
- Prior knee replacement (bilateral or unilateral)
- Inflammatory arthritis (RA, psoriatic arthritis, ankylosing spondylitis)
- Recent knee trauma (<6 months)
- Unable to complete Dutch-language questionnaires

### Sample Size Calculation

**Target Sample Size:** N = 500 patients minimum

**Justification:**
- Assuming 4% event rate (similar to OAI)
- Expected 20 events over 4 years
- EPV = 20 / 10 predictors = 2.0 (adequate for validation, not development)
- Precision for AUC ±0.05 at 95% CI

**Recruitment Timeline:** 12 months (enrollment)  
**Follow-up Duration:** 48 months (outcomes)  
**Total Study Duration:** 60 months (5 years)

### Data Collection

**Baseline (Enrollment):**
1. Demographics: Age, sex, race/ethnicity
2. Anthropometrics: Height, weight (BMI calculated)
3. Clinical: WOMAC questionnaire (Dutch translation)
4. Imaging: Bilateral knee X-rays (KL grade scored by radiologist)
5. History: Family history of knee OA

**Follow-up (Every 12 months):**
1. Phone or clinic visit to assess outcome
2. Query surgical registry for knee replacement procedures
3. Update contact information

**Outcome Ascertainment:**
- Total knee replacement (TKR) surgery
- Date of surgery
- Laterality (right, left, or bilateral)
- Partial vs total replacement

### Data Quality Assurance

1. **X-ray Scoring:** Blinded assessment by two radiologists, adjudication if discordant
2. **WOMAC Completion:** Research assistant reviews for missing items
3. **Outcome Verification:** Cross-check with national surgical registry (if available)
4. **Missing Data:** Document reasons, attempt to retrieve

### Statistical Analysis

**Primary Analysis:**
1. Calculate predicted probabilities using DOC model
2. Assess discrimination: AUC with 95% CI (DeLong method)
3. Assess calibration: 
   - Calibration plot (10 quantile bins)
   - Calibration slope and intercept
   - Brier score
4. Compare observed vs predicted event rates

**Secondary Analysis:**
1. Subgroup analyses (age, sex, KL grade)
2. Decision curve analysis
3. Net reclassification improvement (NRI) vs existing tools (if any)

**Statistical Software:** R or Python  
**Significance Level:** α = 0.05 (two-sided)

### Ethical Considerations

**Ethics Approval:** Required from Bergman Clinics IRB/Ethics Committee

**Informed Consent:** Written consent obtained from all participants

**Data Protection:** 
- GDPR-compliant data storage
- De-identified dataset for analysis
- Secure encrypted database

**Patient Safety:**
- Model predictions NOT used for clinical decision-making during validation
- Standard of care maintained for all patients
- Adverse events monitored and reported

---

## EXPECTED OUTCOMES

### Success Criteria
- External AUC ≥0.75 (clinically useful)
- Calibration slope 0.80-1.20 (good calibration)
- Brier score improvement over baseline

### Interpretation
- If AUC <0.75: Model needs recalibration or redevelopment
- If poor calibration: Apply calibration correction factors
- If good performance: Ready for clinical implementation

---

## BUDGET & RESOURCES

**Personnel:**
- Study coordinator (0.5 FTE × 5 years)
- Research assistant (0.25 FTE × 5 years)
- Radiologist time (KL grading)
- Data analyst (for final analysis)

**Materials:**
- X-ray imaging (covered by clinical care)
- WOMAC questionnaires (Dutch translation)
- Database software (REDCap or similar)

**Estimated Cost:** €150,000 - €200,000

---

## DISSEMINATION

**Target Journals:**
1. Journal of Orthopaedic Research
2. Osteoarthritis and Cartilage
3. BMC Musculoskeletal Disorders

**Conferences:**
1. Osteoarthritis Research Society International (OARSI)
2. European Society of Sports Traumatology, Knee Surgery & Arthroscopy (ESSKA)

**Authorship:** Per ICMJE guidelines

---

## STUDY TIMELINE

| Month | Milestone |
|-------|-----------|
| 0-3 | Ethics approval, protocol finalization |
| 3-4 | Staff training, database setup |
| 4-16 | Patient recruitment (N=500) |
| 16-64 | Follow-up (4 years) |
| 64-66 | Data analysis |
| 66-68 | Manuscript preparation |
| 68 | Submission for publication |

**Total Duration:** 68 months (~5.5 years)

---

## REFERENCES

1. OAI dataset documentation
2. Zhang et al. (2025) systematic review of ML models in OA/TKA/THA
3. PROBAST guidelines
4. TRIPOD statement

---

**Protocol Version:** 1.0  
**Date:** 2025-12-01  
**Status:** DRAFT - Awaiting review by Dr. Moen
