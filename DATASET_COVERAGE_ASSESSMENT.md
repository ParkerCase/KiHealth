# OAI Dataset Coverage Assessment

## Summary

**Question:** Do we have all relevant OAI datasets, and are there any we should check for missing data?

**Answer:** We have the core datasets. Additional datasets checked but **do not contain**:

- ❌ Compartment-specific KL grades
- ❌ Osteotomy procedures (separate from TKR)
- ❌ VAS pain scores

---

## Datasets We Have ✅

### 1. **GENERAL - ASCII** ✅

- **Files:** `Enrollees.txt`, `AllClinical00.txt`, `Outcomes99.txt`, `SubjectChar00.txt`
- **Status:** ✅ Complete
- **Contains:** Demographics, clinical scores (WOMAC, KOOS), outcomes (TKR)

### 2. **ALL CLINICAL - ASCII** ✅

- **Files:** `AllClinical00.txt` through `ALLCLINICAL14.txt`
- **Status:** ✅ Complete
- **Contains:** WOMAC, KOOS, symptoms, physical exam, biomarkers

### 3. **X-RAY ASSESSMENTS - ASCII** ✅

- **Files Checked:**
  - `kxr_sq_bu00.txt` - Semi-quantitative scoring (KL grades, JSN)
  - `kxr_qjsw_duryea00.txt` - Quantitative Joint Space Width
  - `kxr_fta_duryea00.txt` - Alignment angles
- **Status:** ✅ Complete
- **Contains:** Overall KL grades, compartment-specific JSN, quantitative JSW

### 4. **OUTCOMES - ASCII** ✅

- **Files:** `Outcomes99.txt`
- **Status:** ✅ Complete
- **Contains:** TKR outcomes, partial replacements

---

## Datasets Checked for Missing Data ❌

### 1. **Compartment-Specific KL Grades**

**Searched in:**

- ✅ Baseline clinical data (`AllClinical00.txt`)
- ✅ X-ray semi-quantitative scoring (`kxr_sq_bu00.txt`)
- ✅ X-ray quantitative JSW (`kxr_qjsw_duryea00.txt`)
- ✅ X-ray alignment files (`kxr_fta_duryea00.txt`)

**Finding:** ❌ **NOT FOUND**

- OAI does not track separate KL grades for medial/lateral/patellofemoral compartments
- Has compartment-specific JSN (Joint Space Narrowing) but not KL grades
- Has quantitative JSW (Joint Space Width) measurements but not KL grades

### 2. **Osteotomy Procedures**

**Searched in:**

- ✅ Outcomes file (`Outcomes99.txt`)
- ✅ All surgery-related columns

**Finding:** ❌ **NOT FOUND**

- OAI tracks Total TKR and Partial/Unicompartmental replacements
- Does NOT track osteotomy procedures separately

### 3. **VAS Pain Scores**

**Searched in:**

- ✅ All clinical data (`AllClinical00.txt`)
- ✅ All columns with "PAIN", "VAS", "VISUAL", "ANALOG" keywords

**Finding:** ❌ **NOT FOUND**

- OAI does not contain VAS pain scores
- Has WOMAC pain subscale (0-20) and KOOS pain (0-100)

---

## Datasets NOT Needed (Checked but Irrelevant)

### 1. **MRI ASSESSMENTS** ❌

- **Why not needed:** KL grades are X-ray based, not MRI
- **Contains:** Cartilage morphometry, WORMS, BLOKS, MOAKS scoring
- **Relevance:** Not relevant for KL grade analysis

### 2. **BIOMARKERS** ❌

- **Why not needed:** Not related to imaging or pain scores
- **Contains:** Serum/urine biomarkers
- **Relevance:** Not relevant for current searches

### 3. **MEDICATION INVENTORY** ❌

- **Why not needed:** Not related to imaging or outcomes
- **Contains:** Current medications
- **Relevance:** Not relevant for current searches

### 4. **HIP RADIOGRAPH SCORING** ❌

- **Why not needed:** We're focused on knee OA
- **Contains:** Hip X-ray assessments
- **Relevance:** Not relevant for knee analysis

---

## What We Found Instead

### 1. **Compartment-Specific Measures (Not KL Grades)**

- ✅ **JSN (Joint Space Narrowing):** `V00XRJSL` (Lateral), `V00XRJSM` (Medial)

  - Scale: 0-3
  - Measures joint space narrowing, not overall OA severity
  - **Not equivalent to KL grades**

- ✅ **Quantitative JSW (Joint Space Width):** Multiple measurements
  - `V00MCMJSW`: Medial Compartment Minimum JSW
  - `V00LJSW*`: Lateral Joint Space Width at various locations
  - Measured in millimeters
  - **Not KL grades, but quantitative measurements**

### 2. **Partial/Unicompartmental Replacements**

- ✅ Found in `Outcomes99.txt`
- 40 events (insufficient for separate model, EPV = 4.0)
- Similar to hemi-prosthesis but not osteotomy

---

## Recommendations

### ✅ **We Have Everything We Need**

**For Current Model:**

- ✅ Overall KL grades (sufficient)
- ✅ WOMAC scores (validated)
- ✅ TKR outcomes (492 events, EPV = 49.2)
- ✅ All required predictors

**For Missing Data:**

1. **Compartment KL grades:** ❌ Not in OAI → Collect at Bergman Clinics if needed
2. **Osteotomy:** ❌ Not in OAI → Collect at Bergman Clinics if needed
3. **VAS:** ❌ Not in OAI → Use VAS→WOMAC conversion (already implemented)

### 📋 **No Need to Download Additional Datasets**

**Datasets that might seem relevant but aren't:**

- ❌ **X-RAY METAANALYSIS** - Summary files, no new data
- ❌ **MRI ASSESSMENTS** - Different imaging modality
- ❌ **ANCILLARY STUDIES** - Specialized sub-studies
- ❌ **FNIH PROJECT** - Post-processed subset

**Conclusion:** We have all the core OAI data needed. Missing items (compartment KL, osteotomy, VAS) are simply not collected in OAI and would need to be collected separately at Bergman Clinics.

---

## Files Generated

- `check_additional_xray_files.py` - Script to check additional X-ray files
- `DATASET_COVERAGE_ASSESSMENT.md` - This document
