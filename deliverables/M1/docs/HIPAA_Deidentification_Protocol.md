# HIPAA De-identification Protocol

**Project:** KiHealth Diabetes Prediction (Transfer Learning)  
**Date:** January 28, 2026  
**Prepared by:** Parker Case, Stroom AI LLC

---

## Data Storage Location

All project data resides in **specific folders within the TL-KiHealth folder** (`Diabetes-KiHealth/TL-KiHealth/`):

| Folder | Contents |
|--------|----------|
| 2013-14-NHANES | NHANES 2013-2014 cycle (DEMO, GLU, INS, GHB, BMX, DIQ) |
| 2015-16-NHANES | NHANES 2015-2016 cycle (DEMO, GLU, INS, GHB, BMX, DIQ) |
| NIHANES | NHANES 2017-2020 and 2021-2023 cycles |
| NHANES-Diabetes | Diabetes Questionnaire (DIQ) files from CDC |
| CHNS | China Health and Nutrition Survey 2009 |
| Frankfurt | Pima Indians Diabetes Dataset |
| DiaBD | DiaBD dataset |

---

## Safe Harbor Method Compliance

All datasets in this project comply with HIPAA Safe Harbor de-identification requirements (45 CFR §164.514(b)(2)).

### Source Data Classification

| Dataset | Source | De-identification Status |
|---------|--------|-------------------------|
| NHANES 2013-2014 | CDC public-use files | ✅ Pre-de-identified by NCHS |
| NHANES 2015-2016 | CDC public-use files | ✅ Pre-de-identified by NCHS |
| NHANES 2017-2020 | CDC public-use files | ✅ Pre-de-identified by NCHS |
| NHANES 2021-2023 | CDC public-use files | ✅ Pre-de-identified by NCHS |
| CHNS 2009 | UNC/NIH public-use files | ✅ Pre-de-identified by UNC |
| Frankfurt (Pima) | UCI ML Repository | ✅ Public research dataset |
| DiaBD | Mendeley Data Repository | ✅ Public research dataset |
| KiHealth proprietary (future) | Client data | Will be de-identified before integration |

### HIPAA Safe Harbor - 18 Identifiers Verification

| # | Identifier | Status | Verification |
|---|------------|--------|--------------|
| 1 | Names | ✅ Not present | patient_id is study-generated (e.g., nhanes_2017_2020_12345) |
| 2 | Geographic < State | ✅ Not present | No city/zip/address data included |
| 3 | Dates (except year) | ✅ Compliant | Only survey_year (2009, 2013-2014, 2015-2016, 2017-2020, 2021-2023) |
| 4 | Phone/Fax/Email | ✅ Not present | N/A |
| 5 | SSN | ✅ Not present | N/A |
| 6 | Medical Record # | ✅ Not present | N/A |
| 7 | Health Plan # | ✅ Not present | N/A |
| 8 | Account # | ✅ Not present | N/A |
| 9 | Certificate/License # | ✅ Not present | N/A |
| 10 | Vehicle ID | ✅ Not present | N/A |
| 11 | Device ID/Serial # | ✅ Not present | N/A |
| 12 | URLs | ✅ Not present | N/A |
| 13 | IP Addresses | ✅ Not present | N/A |
| 14 | Biometric IDs | ✅ Not applicable | DNA methylation (when added) will be anonymized |
| 15 | Photos | ✅ Not present | N/A |
| 16 | Other Unique IDs | ✅ Compliant | patient_id format prevents re-identification |
| 17 | Ages >89 | ✅ N/A | Max age in dataset: 86 years |
| 18 | Small Geographic | ✅ Not present | N/A |

### Data Processing Protocol

**All data sources:**
- Downloaded from public repositories or government agencies
- Already de-identified by source institution
- No PHI present in original files
- No re-identification methods applied

**KiHealth proprietary data (future integration):**
- Will receive de-identified methylation data only
- No patient names, MRNs, or direct identifiers
- Age top-coded at 89 if applicable
- Only year-level dates

### Validation

**Method:** Manual review of all data files  
**Date:** January 28, 2026  
**Reviewer:** Parker Case  
**Conclusion:** All data passed Safe Harbor checklist. Zero re-identification risk identified.

---

**Document Version:** 1.0  
**Last Updated:** January 28, 2026
