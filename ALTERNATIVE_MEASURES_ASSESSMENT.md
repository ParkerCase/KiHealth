# Assessment: Alternative Measures That Translate to VAS/KOOS/WOMAC

## Executive Summary

**Finding:** There are **functional performance tests** (not patient-reported) that have moderate correlation with WOMAC/KOOS, but **no other strong patient-reported outcome measures** beyond KOOS and WOMAC.

**Best Alternative:** **Chair Stand Time** has moderate correlation (r=0.42) but is a **performance test**, not a subjective patient report.

---

## Detailed Analysis

### 1. Patient-Reported Outcome Measures (PROMs)

#### ✅ **KOOS (Knee Injury and Osteoarthritis Outcome Score)**

- **Type:** Patient-reported (subjective)
- **Data:** 99.9% complete (4,793/4,796 patients)
- **Correlation with WOMAC:** r = -0.909 (very strong)
- **Status:** ✅ **BEST ALTERNATIVE** - Already assessed in previous analysis

#### ✅ **WOMAC (Western Ontario and McMaster Universities Osteoarthritis Index)**

- **Type:** Patient-reported (subjective)
- **Data:** 99.6% complete
- **Status:** ✅ **GOLD STANDARD** - Current model uses this

#### ❌ **VAS (Visual Analog Scale)**

- **Type:** Patient-reported (subjective)
- **Data:** 0% - **NOT AVAILABLE** in OAI
- **Status:** ❌ Not available (literature-based conversion only)

#### ❌ **CESD (Depression Scale)**

- **Type:** Patient-reported (subjective)
- **Data:** 98.6% complete
- **Correlation with WOMAC:** r = 0.277 (weak)
- **Status:** ❌ **Not suitable** - Different construct (depression vs knee symptoms)

#### ❌ **SF-36 (Quality of Life)**

- **Type:** Patient-reported (subjective)
- **Data:** Limited/incomplete in OAI baseline
- **Status:** ❌ **Not available** or incomplete

---

### 2. Functional Performance Tests (NOT Patient-Reported)

These are **objective performance measures**, not subjective patient reports, but they correlate with how patients are doing:

#### ⚠️ **Chair Stand Time (V00CSTIME1)**

- **Type:** Performance test (objective)
- **What it measures:** Time to complete 5 chair stands (seconds)
- **Data:** 94.8% complete (4,549/4,796 patients)
- **Correlation with WOMAC:** r = 0.420 (moderate)
- **Correlation with KOOS Pain:** r = -0.340 (moderate)
- **Conversion R²:** ~0.18 (18% variance explained)
- **Interpretation:**
  - Longer time = worse function = higher WOMAC (more symptoms)
  - Can convert: `WOMAC ≈ intercept + coefficient × Chair_Stand_Time`
- **Status:** ⚠️ **Moderate correlation** - Performance test, not patient report

#### ⚠️ **20m Walk Pace (V0020MPACE)**

- **Type:** Performance test (objective)
- **What it measures:** Walking speed (meters/second)
- **Data:** 99.6% complete
- **Correlation with WOMAC:** r = -0.331 (moderate)
- **Interpretation:**
  - Slower pace = worse function = higher WOMAC
- **Status:** ⚠️ **Moderate correlation** - Performance test

#### ⚠️ **400m Walk Time (V00400MTIM)**

- **Type:** Performance test (objective)
- **What it measures:** Time to walk 400 meters (seconds)
- **Data:** 95.2% complete (4,565/4,796 patients)
- **Correlation with WOMAC:** r = 0.296 (weak-moderate)
- **Correlation with KOOS Pain:** r = -0.222 (weak)
- **Status:** ⚠️ **Weak correlation** - Performance test

#### ❌ **Physical Activity Scale (PASE)**

- **Type:** Self-reported activity questionnaire
- **Data:** 99.4% complete
- **Correlation with WOMAC:** r = -0.078 (very weak)
- **Status:** ❌ **Not suitable** - Very weak correlation

---

## Summary Table

| Measure               | Type             | Data % | Correlation | R²    | Suitable?        |
| --------------------- | ---------------- | ------ | ----------- | ----- | ---------------- |
| **KOOS Pain Right**   | Patient-reported | 99.9%  | r = -0.909  | 0.826 | ✅ **YES**       |
| **WOMAC Total Right** | Patient-reported | 99.6%  | r = 1.000   | 1.000 | ✅ Reference     |
| **Chair Stand Time**  | Performance test | 94.8%  | r = 0.420   | ~0.18 | ⚠️ Moderate      |
| **20m Walk Pace**     | Performance test | 99.6%  | r = -0.331  | ~0.11 | ⚠️ Moderate      |
| **400m Walk Time**    | Performance test | 95.2%  | r = 0.296   | ~0.09 | ⚠️ Weak          |
| **PASE Activity**     | Self-reported    | 99.4%  | r = -0.078  | ~0.01 | ❌ No            |
| **CESD Depression**   | Patient-reported | 98.6%  | r = 0.277   | ~0.08 | ❌ No            |
| **VAS Pain**          | Patient-reported | 0%     | N/A         | N/A   | ❌ Not available |

---

## Key Findings

### ✅ **Patient-Reported Measures (Subjective "How Patient is Doing")**

1. **KOOS** - ✅ **BEST ALTERNATIVE**

   - Very strong correlation (r = -0.909)
   - Excellent data completeness (99.9%)
   - Patient-reported (subjective)
   - Knee-specific

2. **WOMAC** - ✅ **GOLD STANDARD**

   - Current model uses this
   - Patient-reported (subjective)
   - Knee-specific

3. **VAS** - ❌ **NOT AVAILABLE** in OAI
   - Would need literature-based conversion
   - Patient-reported (subjective)

### ⚠️ **Performance Tests (Objective "How Patient is Doing")**

1. **Chair Stand Time** - ⚠️ **Moderate correlation**

   - r = 0.420 with WOMAC
   - **NOT patient-reported** - it's a performance test
   - Could convert but less ideal than patient reports
   - Missing data: 5.2% of patients

2. **20m Walk Pace** - ⚠️ **Moderate correlation**
   - r = -0.331 with WOMAC
   - **NOT patient-reported** - it's a performance test
   - Less correlation than Chair Stand

### ❌ **Not Suitable**

- **PASE (Physical Activity):** Very weak correlation (r = -0.078)
- **CESD (Depression):** Weak correlation, different construct
- **SF-36:** Not available/incomplete in OAI

---

## Recommendations

### For Patient-Reported Subjective Measures:

1. **Primary:** Use **KOOS** if available

   - Best correlation with WOMAC (r = -0.909)
   - Excellent data completeness
   - Patient-reported (subjective)
   - Can convert KOOS→WOMAC with high accuracy

2. **Secondary:** Use **VAS** if KOOS not available

   - Literature-based conversion (r ≈ 0.68-0.72)
   - Patient-reported (subjective)
   - Less accurate than KOOS

3. **Tertiary:** Use **WOMAC** (gold standard)
   - Current model uses this
   - Best option if available

### For Performance Tests (Objective Measures):

1. **Chair Stand Time** could be used as proxy:

   - Moderate correlation (r = 0.420)
   - **BUT:** It's a performance test, not patient-reported
   - Less ideal than patient-reported measures
   - Missing 5.2% of patients

2. **20m Walk Pace** could be used:
   - Moderate correlation (r = -0.331)
   - **BUT:** Performance test, not patient-reported
   - Less correlation than Chair Stand

### Clinical Deployment Strategy:

**Option 1: Patient-Reported Measures (Preferred)**

- Ask: "Do you have WOMAC, KOOS, or VAS scores?"
- Priority: WOMAC > KOOS > VAS
- All are patient-reported (subjective)

**Option 2: Performance Tests (Fallback)**

- If no patient-reported measures available
- Use Chair Stand Time or Walk Tests
- **Note:** These are objective performance tests, not subjective reports
- Less ideal but better than nothing

---

## Conclusion

**Answer to Question:** "Is there anything based on how the patient is doing that translates to VAS/KOOS/WOMAC?"

**YES - But Limited Options:**

1. ✅ **KOOS** - Patient-reported, very strong correlation (r = -0.909)
2. ✅ **VAS** - Patient-reported, but NOT in OAI (literature conversion only)
3. ⚠️ **Chair Stand Time** - Performance test (not patient-reported), moderate correlation (r = 0.420)
4. ⚠️ **Walk Tests** - Performance tests (not patient-reported), moderate correlation

**Key Distinction:**

- **Patient-reported (subjective):** KOOS, WOMAC, VAS ✅
- **Performance tests (objective):** Chair Stand, Walk Tests ⚠️

**Best Answer:** **KOOS is the best patient-reported alternative** to WOMAC, with very strong correlation and excellent data completeness.
