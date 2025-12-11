# X-Ray Metaanalysis - OARSI Compartment Scores Analysis

## Executive Summary

**Finding:** ✅ **OARSI compartment-specific scores ARE AVAILABLE** in OAI X-Ray Semi-Quantitative Scoring files

**Key Discovery:** While the X-Ray Metaanalysis files contain only metadata (quality control info), the **standard Semi-Quantitative Scoring files** (`kxr_sq_bu00.txt`) contain **OARSI-based compartment-specific scores** for medial and lateral tibiofemoral compartments.

**Total Compartment Variables Found:** 14 (7 per compartment: Medial and Lateral TF)

**Note:** These scores use the OARSI (Osteoarthritis Research Society International) scoring system, though variable names don't explicitly include "OARSI" in the name.

---

## Files Checked

### X-Ray Metaanalysis Files

- **Location:** `X-ray-metaanalysis/XRay00.txt`
- **Content:** Metadata only (quality control, positioning, exam type)
- **OARSI Scores:** ❌ None (metadata only)

### Standard X-Ray Semi-Quantitative Scoring Files ✅

- **Location:** `X-Ray Image Assessments_ASCII/Semi-Quant Scoring_ASCII/kxr_sq_bu00.txt`
- **Content:** OARSI-based compartment-specific scores
- **OARSI Scores:** ✅ **FOUND**

---

## OARSI Compartment Variables

### Summary Table

| Variable    | Description                     | Compartment | Scale | N Available | % Complete |
| ----------- | ------------------------------- | ----------- | ----- | ----------- | ---------- |
| `V00XRJSM`  | Joint Space Narrowing           | Medial TF   | 0-3   | 12,752      | 99.5%      |
| `V00XROSTM` | Osteophyte                      | Medial TF   | 0-3   | 7,110       | 55.5%      |
| `V00XRSCFM` | Subchondral Sclerosis (Femoral) | Medial TF   | 0-3   | 5,506       | 43.0%      |
| `V00XRCYFM` | Subchondral Cyst (Femoral)      | Medial TF   | 0-1   | 5,506       | 43.0%      |
| `V00XRCYTM` | Subchondral Cyst (Tibial)       | Medial TF   | 0-1   | 5,506       | 43.0%      |
| `V00XRCHM`  | Chondrocalcinosis               | Medial TF   | 0-1   | 7,109       | 55.5%      |
| `V00XRATTM` | Attrition                       | Medial TF   | 0-3   | 5,506       | 43.0%      |
| `V00XRJSL`  | Joint Space Narrowing           | Lateral TF  | 0-3   | 12,751      | 99.5%      |
| `V00XROSTL` | Osteophyte                      | Lateral TF  | 0-3   | 7,110       | 55.5%      |
| `V00XRSCFL` | Subchondral Sclerosis (Femoral) | Lateral TF  | 0-3   | 5,506       | 43.0%      |
| `V00XRCYFL` | Subchondral Cyst (Femoral)      | Lateral TF  | 0-1   | 5,506       | 43.0%      |
| `V00XRCYTL` | Subchondral Cyst (Tibial)       | Lateral TF  | 0-1   | 5,506       | 43.0%      |
| `V00XRCHL`  | Chondrocalcinosis               | Lateral TF  | 0-1   | 7,109       | 55.5%      |
| `V00XRATTL` | Attrition                       | Lateral TF  | 0-2   | 5,506       | 43.0%      |

**Total:** 14 compartment-specific variables

---

## Compartments Scored

### ✅ Medial Tibiofemoral (TF) Compartment

- **Variables:** 7 features
- **Features:** JSN, Osteophyte, Subchondral Sclerosis, Subchondral Cyst (femoral & tibial), Chondrocalcinosis, Attrition
- **Best Completeness:** JSN (99.5%)

### ✅ Lateral Tibiofemoral (TF) Compartment

- **Variables:** 7 features
- **Features:** JSN, Osteophyte, Subchondral Sclerosis, Subchondral Cyst (femoral & tibial), Chondrocalcinosis, Attrition
- **Best Completeness:** JSN (99.5%)

### ❌ Patellofemoral Compartment

- **Variables:** 0
- **Status:** Not scored separately in OAI
- **Note:** Patellofemoral OA is assessed via overall KL grade only

---

## Features Scored Per Compartment

### 1. Joint Space Narrowing (JSN)

- **Medial:** `V00XRJSM` (0-3 scale, 99.5% complete)
- **Lateral:** `V00XRJSL` (0-3 scale, 99.5% complete)
- **Best available:** Highest completeness of all features

### 2. Osteophytes

- **Medial:** `V00XROSTM` (0-3 scale, 55.5% complete)
- **Lateral:** `V00XROSTL` (0-3 scale, 55.5% complete)

### 3. Subchondral Sclerosis

- **Medial Femoral:** `V00XRSCFM` (0-3 scale, 43.0% complete)
- **Lateral Femoral:** `V00XRSCFL` (0-3 scale, 43.0% complete)

### 4. Subchondral Cysts

- **Medial Femoral:** `V00XRCYFM` (0-1 scale, 43.0% complete)
- **Medial Tibial:** `V00XRCYTM` (0-1 scale, 43.0% complete)
- **Lateral Femoral:** `V00XRCYFL` (0-1 scale, 43.0% complete)
- **Lateral Tibial:** `V00XRCYTL` (0-1 scale, 43.0% complete)

### 5. Chondrocalcinosis

- **Medial:** `V00XRCHM` (0-1 scale, 55.5% complete)
- **Lateral:** `V00XRCHL` (0-1 scale, 55.5% complete)

### 6. Attrition

- **Medial:** `V00XRATTM` (0-3 scale, 43.0% complete)
- **Lateral:** `V00XRATTL` (0-2 scale, 43.0% complete)

---

## Data Completeness

### Overall Statistics

- **Total OAI patients:** 4,796
- **Total knee observations:** 12,813 (both knees per patient)
- **Patients with JSN data:** ~6,375 (99.5% of knees = ~99.5% of patients)
- **Patients with osteophyte data:** ~3,555 (55.5% of knees)

### Completeness by Feature Type

- **High Completeness (≥90%):**
  - Joint Space Narrowing (Medial & Lateral): 99.5%
- **Moderate Completeness (50-90%):**

  - Osteophytes: 55.5%
  - Chondrocalcinosis: 55.5%

- **Lower Completeness (<50%):**
  - Subchondral Sclerosis: 43.0%
  - Subchondral Cysts: 43.0%
  - Attrition: 43.0%

### Missing Data Patterns

- **JSN:** Nearly complete (99.5%) - best feature for modeling
- **Osteophytes/Chondrocalcinosis:** Moderate completeness (55.5%) - likely only scored for certain patient subsets
- **Sclerosis/Cysts/Attrition:** Lower completeness (43.0%) - likely only scored when present or for specific analyses

---

## Comparison with Standard X-Ray Files

### What We Already Knew

- ✅ Overall KL grade (`V00XRKL`) - 99.5% complete
- ✅ Compartment-specific JSN (`V00XRJSM`, `V00XRJSL`) - 99.5% complete

### What We Discovered

- ✅ **OARSI compartment-specific scores for multiple features:**
  - Osteophytes (medial & lateral)
  - Subchondral sclerosis (medial & lateral)
  - Subchondral cysts (medial & lateral, femoral & tibial)
  - Chondrocalcinosis (medial & lateral)
  - Attrition (medial & lateral)

### What's Still Missing

- ❌ Compartment-specific KL grades (not available)
- ❌ Patellofemoral compartment scores (not available)
- ❌ Overall OARSI grade per compartment (would need to calculate from features)

---

## OARSI Scoring System

### Scale Definitions (Typical OARSI)

- **JSN (Joint Space Narrowing):** 0-3

  - 0 = Normal
  - 1 = Mild narrowing
  - 2 = Moderate narrowing
  - 3 = Severe narrowing/obliteration

- **Osteophytes:** 0-3

  - 0 = None
  - 1 = Small
  - 2 = Moderate
  - 3 = Large

- **Subchondral Sclerosis:** 0-3

  - 0 = None
  - 1-3 = Increasing severity

- **Subchondral Cysts:** 0-1 (binary)

  - 0 = Absent
  - 1 = Present

- **Chondrocalcinosis:** 0-1 (binary)

  - 0 = Absent
  - 1 = Present

- **Attrition:** 0-3
  - 0 = None
  - 1-3 = Increasing severity

---

## Recommendations

### ✅ **OARSI Compartment Scores ARE Available**

**Conclusion:** OAI **does contain** OARSI-based compartment-specific scores, but they are in the **standard Semi-Quantitative Scoring files**, not in separate "metaanalysis" files.

### For Model Enhancement

1. **Use JSN scores** (recommended)

   - Highest completeness (99.5%)
   - Already identified in previous analysis
   - Strong predictor of OA severity

2. **Consider adding osteophyte scores** (optional)

   - Moderate completeness (55.5%)
   - Could improve model specificity
   - Would need to handle missing data

3. **EPV Impact Assessment**
   - Current model: 10 predictors, EPV = 42.5
   - Adding 2 JSN scores (medial + lateral): 12 predictors, EPV = 35.4 ✅ Still ≥ 15
   - Adding all 14 compartment scores: 24 predictors, EPV = 17.7 ✅ Still ≥ 15
   - **Can add compartment scores while maintaining top 7% quality**

### Implementation Considerations

1. **Data Integration**

   - X-ray file uses `ID` and `SIDE` (1=Right, 2=Left)
   - Need to merge with main dataset
   - May need to pivot from knee-level to patient-level

2. **Missing Data Handling**

   - JSN: Nearly complete, minimal imputation needed
   - Other features: 43-55% complete, need imputation strategy

3. **Feature Selection**
   - Start with JSN (highest completeness)
   - Add osteophytes if improves model
   - Other features may be less useful due to lower completeness

---

## Answer to Question

**"Does X-Ray Metaanalysis contain compartment-specific severity scores that we don't already have?"**

**Answer:**

- ❌ **X-Ray Metaanalysis files** (`XRay00.txt`) contain only metadata, not scores
- ✅ **Standard X-Ray Semi-Quantitative files** (`kxr_sq_bu00.txt`) contain **OARSI compartment-specific scores** that we **didn't fully identify before**

**What's New:**

- We already knew about JSN (medial/lateral)
- We **discovered** OARSI scores for osteophytes, sclerosis, cysts, chondrocalcinosis, and attrition
- These are compartment-specific (medial/lateral TF) but use OARSI scoring system

**Recommendation:** Use JSN scores (already identified) as they have highest completeness. Other OARSI features are available but have lower completeness (43-55%).

---

## Files Generated

- `explore_xray_metaanalysis.py` - Analysis script
- `XRAY_METAANALYSIS_OARSI_REPORT.md` - This document
