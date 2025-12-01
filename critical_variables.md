# Critical Variables for OAI Model

This document lists all variables needed for building the predictive model.

## 1. Demographics (Enrollees.txt)
- **ID**: Patient identifier
- **V00AGE**: Age at baseline
- **P02SEX**: Sex
- **P02RACE**: Race
- **V00COHORT**: Cohort (Progression vs Incidence)

## 2. Baseline Characteristics (SubjectChar00.txt)
- **ID**: Patient identifier
- **P01BMI**: BMI
- **P01FAMKR**: Family history of knee OA
- **V00PASE**: Physical activity scale
- **V00WORK7**: Work status

## 3. Clinical Scores (AllClinical00.txt)

### WOMAC Scores
- **V00WOMKPR**: WOMAC Pain (Right knee)
- **V00WOMKPL**: WOMAC Pain (Left knee)
- **V00WOMSTFR**: WOMAC Stiffness (Right knee)
- **V00WOMSTFL**: WOMAC Stiffness (Left knee)
- **V00WOMADLR**: WOMAC Function/ADL (Right knee)
- **V00WOMADLL**: WOMAC Function/ADL (Left knee)
- **V00WOMTSR**: WOMAC Total Score (Right knee)
- **V00WOMTSL**: WOMAC Total Score (Left knee)

### Pain VAS
- **V00KPPNRT**: Pain VAS Right knee (if exists)
- **V00KPPNLT**: Pain VAS Left knee (if exists)

### Physical Function
- **V00WTMWK**: 20m walk time
- **V00CSTIME**: Chair stand time

## 4. X-Ray Assessments

### KL Grades (kxr_sq_bu00.txt)
- **V00XRKL**: Kellgren-Lawrence grade (per knee, per side)
- **ID**: Patient identifier
- **SIDE**: 1=Right, 2=Left

### Alignment (flxr_kneealign_cooke01.txt)
- **V01HKANGLE**: Hip-knee-ankle angle

## 5. Outcomes (Outcomes99.txt)
- **id**: Patient identifier (lowercase)
- **V99ERKBLRP**: Right knee replacement at baseline
- **V99ELKBLRP**: Left knee replacement at baseline
- **V99ERKRPCF**: Right knee replacement confirmed
- **V99ELKRPCF**: Left knee replacement confirmed

## 6. Biomarkers (Biomarkers00.txt)
- **ID**: Patient identifier
- [Biomarker value columns to be determined]

## Data Linkage Notes
- Most datasets use **ID** (uppercase) as patient identifier
- Outcomes99 uses **id** (lowercase) - needs standardization
- X-ray files have **SIDE** column (1=Right, 2=Left)
- Visit codes: V00=baseline, V01=12mo, V02=24mo, etc.
