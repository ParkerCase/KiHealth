# OAI Dataset: Data on Other Body Areas/Joints

**Date:** 2025-12-02  
**Question:** Does OAI dataset contain data for areas other than just knees?

---

## Answer: **YES, but LIMITED**

The OAI (Osteoarthritis Initiative) dataset is **primarily focused on knee OA**, but it does include **limited data on other joints** for comorbidity assessment.

---

## Available Data on Other Joints

### 1. **Hip Osteoarthritis**

- **Variables:**
  - `P01HRSROA`: Hip OA Right (0.9% prevalence)
  - `P01HRSLOA`: Hip OA Left (0.7% prevalence)
  - `P01OAHIPCV`: Hip OA Confirmed (7.0% prevalence)
- **Data Type:** Binary (Yes/No confirmation)
- **Coverage:** ~89% of patients have data

### 2. **Hand Osteoarthritis**

- **Variables:**
  - `P01OAHNDCV`: Hand OA Confirmed (16.3% prevalence)
- **Data Type:** Binary (Yes/No confirmation)
- **Coverage:** ~97% of patients have data

### 3. **Back/Spine Osteoarthritis**

- **Variables:**
  - `P01OABCKCV`: Back OA Confirmed (17.3% prevalence)
  - `V00SPNFX`: Spine fracture history
  - `V00SPNFXAG`: Spine fracture age
- **Data Type:** Binary (Yes/No confirmation)
- **Coverage:** ~96% of patients have data

### 4. **Other Osteoarthritis**

- **Variables:**
  - `P01OAOTHCV`: Other OA Confirmed (9.3% prevalence)
- **Data Type:** Binary (Yes/No confirmation)
- **Coverage:** ~97% of patients have data

### 5. **Hip Fracture History**

- **Variables:**
  - `V00HIPFX`: Hip fracture history (1.0% prevalence)
  - `V00HIPFXAG`: Hip fracture age
- **Data Type:** Binary + age at fracture
- **Coverage:** 100% of patients have data

---

## Data Limitations

### ❌ **NOT Available for Other Joints:**

1. **Detailed Symptom Scores**

   - No WOMAC scores for other joints
   - No pain/stiffness/function measures
   - No patient-reported outcomes

2. **Imaging Data**

   - No X-ray assessments (KL grades) for other joints
   - No MRI data for other joints
   - No quantitative imaging measures

3. **Treatment Data**

   - No treatment-specific to other joints
   - No medication data for other joint conditions
   - No injection data for other joints

4. **Longitudinal Follow-up**

   - Limited follow-up data for other joints
   - Primarily baseline prevalence

5. **Outcome Data**
   - No replacement surgery data for other joints
   - No progression measures for other joints

---

## Prevalence Summary

| Joint/Area       | Prevalence    | Data Quality                                   |
| ---------------- | ------------- | ---------------------------------------------- |
| **Knee OA**      | Primary focus | ✅ Comprehensive (WOMAC, X-ray, MRI, outcomes) |
| **Hand OA**      | 16.3%         | ⚠️ Binary confirmation only                    |
| **Back OA**      | 17.3%         | ⚠️ Binary confirmation only                    |
| **Hip OA**       | 7.0%          | ⚠️ Binary confirmation only                    |
| **Other OA**     | 9.3%          | ⚠️ Binary confirmation only                    |
| **Hip Fracture** | 1.0%          | ⚠️ History only                                |

---

## Use Cases

### ✅ **Suitable For:**

1. **Comorbidity Assessment**

   - Adjusting knee OA models for other joint OA
   - Understanding polyarticular OA burden
   - Confounding variable adjustment

2. **Descriptive Analysis**

   - Prevalence of OA in other joints
   - Co-occurrence patterns
   - General OA burden

3. **Baseline Characteristics**
   - Patient stratification
   - Risk factor analysis
   - Cohort description

### ❌ **NOT Suitable For:**

1. **Modeling Other Joint Outcomes**

   - Insufficient outcome data
   - No detailed symptom measures
   - No treatment response data

2. **Other Joint Prediction Models**

   - No imaging predictors
   - No symptom trajectories
   - No treatment data

3. **Comparative Joint Analysis**
   - Knee data is comprehensive
   - Other joints are binary only
   - Cannot compare severity/progression

---

## Comparison: Knee vs. Other Joints

| Feature            | Knee OA                              | Other Joints   |
| ------------------ | ------------------------------------ | -------------- |
| **Symptom Scores** | ✅ WOMAC (pain, stiffness, function) | ❌ None        |
| **Imaging**        | ✅ X-ray (KL grades), MRI            | ❌ None        |
| **Treatment Data** | ✅ Medications, injections           | ❌ None        |
| **Longitudinal**   | ✅ 7+ timepoints                     | ⚠️ Limited     |
| **Outcomes**       | ✅ TKR surgery, progression          | ❌ None        |
| **Sample Size**    | ✅ 4,796 patients                    | ✅ Same cohort |
| **Data Quality**   | ✅ Comprehensive                     | ⚠️ Binary only |

---

## Conclusion

**OAI is a KNEE-focused dataset** with:

- ✅ **Comprehensive knee OA data** (symptoms, imaging, treatment, outcomes)
- ⚠️ **Limited other joint data** (binary prevalence/confirmation only)

**Recommendation:**

- Use other joint data as **confounders/comorbidities** in knee OA models
- **Do NOT** attempt to build prediction models for other joints
- For other joint modeling, seek dedicated datasets (e.g., hand OA cohorts, hip OA registries)

---

**Variables Found:**

- Hip: `P01HRSROA`, `P01HRSLOA`, `P01OAHIPCV`, `V00HIPFX`, `V00HIPFXAG`
- Hand: `P01OAHNDCV`
- Back: `P01OABCKCV`, `V00SPNFX`, `V00SPNFXAG`
- Other: `P01OAOTHCV`
- General: `P01OADEGCV`, `P01SXKOA`, `P01LSXKOA`, `P01RSXKOA`

**Total:** ~20 variables related to other joints (vs. 100+ for knees)
