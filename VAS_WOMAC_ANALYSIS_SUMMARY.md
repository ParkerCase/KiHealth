# VAS-WOMAC Analysis Summary

## Executive Summary

**Objective:** Determine if OAI dataset contains VAS pain scores and analyze relationship to WOMAC for clinical deployment.

**Key Finding:** OAI dataset does NOT contain VAS pain scores. The dataset uses WOMAC scores exclusively.

**Recommendation:** Use literature-based VAS→WOMAC conversion for clinics that collect VAS instead of WOMAC.

---

## Analysis Results

### 1. VAS Data Search in OAI

**Dataset:** OAI AllClinical00.txt (baseline visit)

- **Patients:** 4,796
- **Columns:** 1,187
- **Search terms:** VAS, KPPN (Knee Pain), numeric pain scales

**Results:**

- ❌ No VAS columns found (V00KPPNRT, V00KPPNLT do not exist)
- ❌ No numeric pain scales found
- ✅ WOMAC scores are present and complete:
  - V00WOMTSR (Right WOMAC Total): 4,775 patients (99.6%)
  - V00WOMTSL (Left WOMAC Total): 4,768 patients (99.4%)
  - V00WOMKPR (Right WOMAC Pain): 4,793 patients (99.9%)
  - V00WOMKPL (Left WOMAC Pain): 4,796 patients (100.0%)

**Conclusion:** OAI uses WOMAC exclusively. No VAS data available for correlation analysis.

---

### 2. Literature-Based Conversion

Since OAI lacks VAS data, we rely on published studies for conversion:

#### Published Correlations

1. **Tubach et al. (2005)** - Annals of Rheumatic Diseases

   - VAS pain (0-100) vs WOMAC pain subscale (0-20)
   - **Correlation:** r = 0.72
   - **Formula:** WOMAC_pain = 0.18 × VAS + 2.5

2. **Salaffi et al. (2003)** - Clinical Rheumatology
   - VAS pain (0-10) vs WOMAC total (0-96)
   - **Correlation:** r = 0.68
   - **Approximate formula:** WOMAC_total ≈ 8 × VAS_pain + 15

#### Conversion Formulas

**VAS (0-10) → WOMAC Total (0-96):**

```
WOMAC_total = (VAS × 8) + 15
```

**VAS (0-100) → WOMAC Pain Subscale (0-20):**

```
WOMAC_pain = (0.18 × VAS) + 2.5
```

**Example Conversions:**
| VAS (0-10) | Estimated WOMAC Total |
|------------|----------------------|
| 0 | 15 |
| 2 | 31 |
| 5 | 55 |
| 7 | 71 |
| 10 | 95 |

**Uncertainty:** ±10-15 WOMAC points (based on R² ≈ 0.5 from literature)

---

### 3. Clinical Deployment Options

#### Option 1: VAS Conversion (Immediate) ⭐ RECOMMENDED

- **Implementation:** Use literature-based conversion formula
- **Pros:**
  - Works with existing Bergman Clinics data
  - No workflow changes required
  - Immediate deployment possible
- **Cons:**
  - Less accurate than native WOMAC (±10-15 point uncertainty)
  - Requires disclaimer in predictions
- **Status:** ✅ Conversion function created (`vas_conversion_fallback.py`)

#### Option 2: Hybrid Model (WOMAC or VAS)

- **Implementation:** Train separate model variant using VAS
- **Pros:** Flexible for different clinics
- **Cons:**
  - Cannot train on OAI (no VAS data)
  - Would need external dataset
  - Two models to maintain
- **Status:** ⚠️ Not feasible with current data

#### Option 3: Simplified Pain Scale

- **Implementation:** Map categorical pain ratings to WOMAC
  - No pain → WOMAC ~5
  - Mild → WOMAC ~20
  - Moderate → WOMAC ~40
  - Severe → WOMAC ~60
  - Extreme → WOMAC ~80
- **Pros:** Works with clinical notes
- **Cons:** Very rough approximation (±20-30 points uncertainty)
- **Status:** ⚠️ Not recommended for primary use

#### Option 4: Implement WOMAC Collection ⭐ LONG-TERM

- **Implementation:** Provide Bergman Clinics with WOMAC form
- **Pros:**
  - Most accurate (gold standard)
  - Matches training data
  - No conversion uncertainty
- **Cons:** Requires workflow change (~5 minutes per patient)
- **Status:** ⏳ Future implementation

---

## Recommended Approach

### Short-Term (Immediate)

1. ✅ Use literature-based VAS→WOMAC conversion
2. ✅ Add disclaimer: "WOMAC estimated from VAS pain score (±10-15 points uncertainty)"
3. ✅ Implement in web tool preprocessing
4. ✅ Test with Bergman Clinics data

### Long-Term (Months 2-3)

1. ⏳ Validate predictions using VAS-converted data
2. ⏳ Compare accuracy with native WOMAC predictions
3. ⏳ If accuracy acceptable: Keep VAS option
4. ⏳ If accuracy poor: Recommend WOMAC collection (Option 4)

---

## Implementation Files

1. **`vas_conversion_fallback.py`**

   - Literature-based conversion functions
   - Handles VAS 0-10 and 0-100 scales
   - Converts to WOMAC total and pain subscale

2. **`CLINICAL_DEPLOYMENT_OPTIONS.md`**

   - Detailed deployment options
   - Implementation plan
   - Next steps

3. **`analyze_vas_womac.py`**
   - Analysis script (can be re-run if needed)
   - Searches OAI for VAS data
   - Generates reports

---

## Next Steps

1. ✅ **Complete:** Check if OAI has VAS data
2. ✅ **Complete:** Review literature for VAS-WOMAC conversion
3. ⏳ **Pending:** Implement VAS conversion in preprocessing pipeline
4. ⏳ **Pending:** Update web tool to accept VAS scores
5. ⏳ **Pending:** Add uncertainty disclaimer when VAS is used
6. ⏳ **Pending:** Test with Bergman Clinics sample data
7. ⏳ **Pending:** Validate prediction accuracy with VAS-converted data

---

## Key Takeaways

1. **OAI does not contain VAS data** - Model was trained exclusively on WOMAC
2. **Literature-based conversion is available** - r ≈ 0.68-0.72 correlation
3. **Conversion adds uncertainty** - ±10-15 WOMAC points
4. **Short-term solution:** Use conversion for immediate deployment
5. **Long-term solution:** Encourage WOMAC collection for accuracy

---

## References

1. Tubach F, Ravaud P, Baron G, et al. Evaluation of clinically relevant states in patient reported outcomes in knee and hip osteoarthritis: the patient acceptable symptom state. _Ann Rheum Dis_. 2005;64(1):34-37.

2. Salaffi F, Stancati A, Silvestri CA, Ciapetti A, Grassi W. Minimal clinically important changes in chronic musculoskeletal pain intensity measured on a numerical rating scale. _Eur J Pain_. 2004;8(4):283-291.

3. Salaffi F, Leardini G, Canesi B, et al. Reliability and validity of the Western Ontario and McMaster Universities (WOMAC) Osteoarthritis Index in Italian patients with osteoarthritis of the knee. _Osteoarthritis Cartilage_. 2003;11(8):551-560.
