# Predictor Selection Rationale - Complete Documentation

**Purpose:** Document clinical and statistical rationale for predictor variable selection to meet PROBAST transparency requirements.

---

## Selection Criteria

Variables were selected based on five criteria:

1. **Clinical Relevance** - Evidence-based OA risk factors from literature
2. **Data Availability** - >90% completeness (minimize missing data)
3. **Routine Clinical Accessibility** - Variables available in standard clinical practice
4. **Non-Redundancy** - Avoid multicollinearity and overfitting
5. **EPV Compliance** - Sufficient events per variable (≥15 required)

---

## Included Variables (11 total)

### 1. Demographics (4 variables)

#### Age (V00AGE)

- **Source:** AllClinical00.txt
- **Type:** Continuous (years)
- **Range:** 45-79
- **Missing:** 0%
- **Rationale:**
  - Strongest OA risk factor (age-related cartilage degeneration)
  - Linear relationship with OA progression
  - Routinely available in all clinical settings
- **Evidence:** Age is primary OA risk factor in all major guidelines

#### Sex (P02SEX)

- **Source:** Enrollees.txt
- **Type:** Categorical (Male/Female)
- **Missing:** 0%
- **Rationale:**
  - Female sex is established OA risk factor (hormonal factors)
  - Important for model generalizability
  - Essential demographic confounder
- **Evidence:** Women have 2-3x higher OA prevalence

#### Race (P02RACE)

- **Source:** Enrollees.txt
- **Type:** Categorical (5 categories)
- **Missing:** 0%
- **Rationale:**
  - Important for model generalizability across populations
  - Addresses potential health disparities
  - Required for external validation
- **Evidence:** OA prevalence varies by race/ethnicity

#### Cohort (V00COHORT)

- **Source:** Enrollees.txt
- **Type:** Categorical (Progression/Incidence)
- **Missing:** 0%
- **Rationale:**
  - Progression cohort: Already has OA, predicting progression
  - Incidence cohort: At risk, predicting development
  - Different risk profiles require adjustment
- **Evidence:** Cohort type is major predictor in OAI studies

---

### 2. Clinical Scores (2 variables)

#### WOMAC Total Right (V00WOMTSR)

- **Source:** AllClinical00.txt
- **Type:** Continuous (0-96 scale)
- **Range:** 0-93.9
- **Missing:** 0.44%
- **Rationale:**
  - **Gold standard** OA symptom measure
  - Composite of pain (0-20), stiffness (0-8), function (0-68)
  - Total score = 96 maximum (standard WOMAC)
  - Used total score (not components) to reduce predictor count
- **Evidence:** WOMAC is most validated OA outcome measure

#### WOMAC Total Left (V00WOMTSL)

- **Source:** AllClinical00.txt
- **Type:** Continuous (0-96 scale)
- **Range:** 0-96.0
- **Missing:** 0.58%
- **Rationale:**
  - Bilateral OA is common
  - Left knee symptoms independent predictor
  - Captures overall disease burden
- **Evidence:** Bilateral symptoms increase replacement risk

**Why Total Scores vs. Components?**

- **Trade-off:** Slight loss of granularity for statistical power
- **Benefit:** Reduces predictors from 6 (pain R/L, stiffness R/L, function R/L) to 2
- **EPV impact:** Critical for achieving EPV ≥15
- **Clinical relevance:** Total score is standard clinical metric

---

### 3. Anthropometric (1 variable)

#### BMI (P01BMI)

- **Source:** AllClinical00.txt
- **Type:** Continuous (kg/m²)
- **Range:** 16.9-48.7
- **Missing:** 0.08%
- **Rationale:**
  - **Strongest modifiable risk factor** for OA
  - Mechanical loading increases joint stress
  - Routinely measured in all clinical settings
  - Linear relationship with OA progression
- **Evidence:** Each 5 kg/m² increase = 35% higher OA risk

---

### 4. Imaging (2 variables)

#### KL Grade Right (V00XRKLR)

- **Source:** MeasInventory.csv
- **Type:** Ordinal (0-4)
- **Range:** 0-4
- **Missing:** 6.82%
- **Distribution:**
  - Grade 0: 37.8%
  - Grade 1: 17.5%
  - Grade 2: 27.6%
  - Grade 3: 13.6%
  - Grade 4: 3.4%
- **Rationale:**
  - **Validated structural OA severity** measure
  - Strongest imaging predictor of progression
  - Standard radiographic assessment
  - Balanced distribution (not heavily skewed)
- **Evidence:** KL grade ≥2 is inclusion criterion for many OA trials

#### KL Grade Left (V00XRKLL)

- **Source:** MeasInventory.csv
- **Type:** Ordinal (0-4)
- **Range:** 0-4
- **Missing:** 6.53%
- **Distribution:**
  - Grade 0: 39.7%
  - Grade 1: 17.7%
  - Grade 2: 25.5%
  - Grade 3: 13.9%
  - Grade 4: 3.2%
- **Rationale:**
  - Bilateral assessment captures overall structural severity
  - Independent predictor from right knee
- **Evidence:** Higher KL grade = higher replacement risk

**KL Grade Interpretation:**

- 0: Normal
- 1: Doubtful (minimal changes)
- 2: Mild (definite osteophytes, possible joint space narrowing)
- 3: Moderate (moderate joint space narrowing)
- 4: Severe (severe joint space narrowing, large osteophytes)

---

### 5. Physical Function (1 variable)

#### Walking Distance - 400m Walk Time (V00400MTIM)

- **Source:** AllClinical00.txt
- **Type:** Continuous (seconds)
- **Range:** 42-900 seconds (0.7-15 minutes)
- **Missing:** 4.82% (231/4,796 patients)
- **Rationale:**
  - **Objective performance measure** - complements patient-reported WOMAC
  - Routinely assessed in orthopedic clinical practice
  - Strong evidence base in OA literature
  - Captures functional limitation independently from WOMAC
  - Standardized OAI protocol (400m walk test)
- **Evidence:**
  - Walking speed/distance well-established OA predictor
  - Slower walking associated with higher OA risk
  - Used in multiple OAI publications
- **Clinical Relevance:**
  - "How far can you walk?" is intuitive for patients
  - Part of standard functional assessment
  - Orthopedic surgeons routinely use this measure
- **Data Quality:**
  - 95.2% complete (acceptable <20% threshold)
  - Handled via MICE imputation (same as other variables)

### 6. Risk Factors (1 variable)

#### Family History (P01FAMKR)

- **Source:** SubjectChar00.txt
- **Type:** Categorical (Yes/No/Unknown)
- **Missing:** 0%
- **Rationale:**
  - **Strong genetic predisposition** indicator
  - Heritability of OA estimated at 40-65%
  - Routinely assessed in clinical history
  - Simple binary/categorical variable
- **Evidence:** Family history doubles OA risk

---

## Excluded Variables (with rationale)

### Pain VAS Scores

- **Variables:** V00KPPNRT, V00KPPNLT (if they exist)
- **Rationale:**
  - Redundant with WOMAC pain component (already in total score)
  - Limited availability in AllClinical00
  - WOMAC pain is more validated
- **Impact:** Low (WOMAC total captures pain)

### Physical Function Tests (Partial Inclusion)

- **Variables:** V00WTMWK (20m walk), V00CSTIME (chair stand)
- **Status:** V00400MTIM (400m walk time) **INCLUDED** - see above
- **Rationale for 20m walk/chair stand exclusion:**
  - Redundant with WOMAC function component
  - Higher missingness than 400m walk time
  - 400m walk time selected as best functional performance measure
- **Impact:** Low (400m walk time captures functional limitations, complements WOMAC)

### Individual WOMAC Components

- **Variables:** V00WOMKPR, V00WOMKPL (pain), V00WOMSTFR, V00WOMSTFL (stiffness), V00WOMADLR, V00WOMADLL (function)
- **Rationale:**
  - **Critical for EPV:** Using total scores reduces predictors from 6 to 2
  - Total score is standard clinical metric
  - Components are highly correlated (multicollinearity risk)
- **Impact:** Moderate (lose granularity but gain statistical power)
- **Decision:** EPV compliance prioritized over granularity

### Biomarkers

- **Variables:** Various serum biomarkers from Biomarkers00.txt
- **Rationale:**
  - Limited clinical utility (not routinely available)
  - Variable availability across patients
  - Less predictive than clinical/imaging variables
  - Would require specialized lab tests
- **Impact:** Low (not standard of care)

### Previous Knee Injury

- **Variables:** P01INJR, P01INJL
- **Rationale:**
  - Higher missingness than family history
  - Less predictive than other included variables
  - Less evidence base than family history
- **Impact:** Low (family history captures genetic risk)

### Physical Activity Scale

- **Variables:** V00PASE
- **Rationale:**
  - Complex categorical variable (less interpretable)
  - Partially captured by BMI and WOMAC function
  - Missingness: 0.6% (acceptable but not critical)
- **Impact:** Low (redundant with other variables)

### Work Status

- **Variables:** V00WORK7
- **Rationale:**
  - Less directly related to OA progression
  - Social determinant (less biological mechanism)
  - Lower predictive value than included variables
- **Impact:** Low (not primary OA risk factor)

---

## EPV Ratio Optimization Strategy

### Initial Variable Count: 17+

- Demographics: 4
- WOMAC components: 6 (pain R/L, stiffness R/L, function R/L)
- Physical function: 2
- Imaging: 2
- Risk factors: 3+

**EPV with 17 predictors:** 171 / 17 = **10.06** ❌ (insufficient)

### Optimized Variable Count: 10

- Demographics: 4
- WOMAC total: 2 (composite scores)
- Anthropometric: 1
- Imaging: 2
- Risk factors: 1

**EPV with 10 predictors:** 171 / 10 = **17.10** ✅ (adequate)

### Strategy Applied

1. **Used composite scores** (WOMAC total) instead of components
2. **Selected most predictive variables** from each category
3. **Excluded redundant variables** (VAS, physical tests)
4. **Prioritized EPV compliance** over variable count

**Result:** Achieved EPV ≥15 while maintaining clinical relevance

---

## Clinical Validation

### Variables Align with OA Risk Factors

**Established OA Risk Factors (from literature):**

1. ✅ Age - Included
2. ✅ Female sex - Included
3. ✅ BMI - Included
4. ✅ Symptom severity (WOMAC) - Included
5. ✅ Structural severity (KL grade) - Included
6. ✅ Family history - Included

**All major OA risk factors represented** ✅

### Variables Available in Routine Care

**Standard clinical assessment includes:**

- ✅ Demographics (age, sex, race)
- ✅ BMI (routinely measured)
- ✅ WOMAC scores (standard OA questionnaire)
- ✅ X-ray KL grade (standard imaging)
- ✅ Family history (standard history)

**No specialized tests required** ✅

---

## Statistical Considerations

### Multicollinearity Avoidance

**High correlations avoided:**

- WOMAC components vs. total (used total only)
- Pain VAS vs. WOMAC pain (excluded VAS)
- Physical tests vs. WOMAC function (excluded tests)

**Result:** Independent predictors with minimal correlation

### Missing Data Strategy

**Variables selected with <20% missing:**

- All variables: <7% missing (except KL grades at 6.5-6.8%)
- KL grades: Acceptable missingness (6.5-6.8%)
- All others: <1% missing

**Result:** Minimal missing data impact

---

## Final Variable List Summary

| Category       | Variables              | Count  | Rationale                                  |
| -------------- | ---------------------- | ------ | ------------------------------------------ |
| Demographics   | Age, Sex, Race, Cohort | 4      | Established risk factors, generalizability |
| Clinical       | WOMAC Total R/L        | 2      | Gold standard symptom measure              |
| Anthropometric | BMI                    | 1      | Strongest modifiable risk factor           |
| Imaging        | KL Grade R/L           | 2      | Validated structural severity              |
| Risk Factors   | Family History         | 1      | Genetic predisposition                     |
| **Total**      |                        | **10** | **EPV = 17.10** ✅                         |

---

**Status:** ✅ Fully documented and justified

**PROBAST Compliance:** ✅ Transparent predictor selection with clinical and statistical rationale
