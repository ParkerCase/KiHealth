# Assessment: Can Subjective Feeling Measures Replace WOMAC?

## Executive Summary

**YES - KOOS (Knee Injury and Osteoarthritis Outcome Score) has sufficient data and very strong correlation with WOMAC to potentially serve as an alternative.**

**Key Finding:** KOOS Pain Right has:

- **99.9% data completeness** (4,793/4,796 patients) - actually slightly better than WOMAC (99.6%)
- **Very strong correlation** with WOMAC: r = -0.909
- **High conversion accuracy:** R² = 0.826 for KOOS→WOMAC conversion
- **Knee-specific and validated** outcome measure

---

## Detailed Analysis

### 1. KOOS (Knee Injury and Osteoarthritis Outcome Score)

#### Data Availability

| Measure                    | Patients | % Complete | Correlation with WOMAC |
| -------------------------- | -------- | ---------- | ---------------------- |
| **KOOS Pain Right (KPR)**  | 4,793    | **99.9%**  | **r = -0.909**         |
| KOOS Pain Left (KPL)       | 4,794    | 100.0%     | r = -0.517             |
| KOOS Stiffness Right (YMR) | 4,796    | 100.0%     | r = -0.789             |
| KOOS Function Right (FSR)  | 3,582    | 74.7%      | r = -0.730             |
| KOOS Quality of Life (QOL) | 4,795    | 100.0%     | r = -0.666             |
| **WOMAC Total Right**      | 4,775    | 99.6%      | r = 1.000 (reference)  |

**Key Observations:**

- KOOS Pain Right has **better data completeness** than WOMAC (99.9% vs 99.6%)
- Only **1 patient** has WOMAC but not KOOS
- **19 patients** have KOOS but not WOMAC (could use KOOS for these)
- **Overlap:** 4,774 patients (99.5%) have both measures

#### Correlation Analysis

**KOOS Pain Right vs WOMAC Total Right:**

- **Pearson correlation:** r = -0.909 (very strong)
- **Note:** Negative correlation is expected because:
  - KOOS: Higher score = **better** (less pain)
  - WOMAC: Higher score = **worse** (more pain)
- **Sample size:** 4,774 patients with both measures

#### Conversion Feasibility

**KOOS → WOMAC Conversion Formula:**

```
WOMAC = -0.18 + 0.77 × (100 - KOOS_Pain)
```

**Conversion Accuracy:**

- **R² = 0.826** (82.6% variance explained)
- **Correlation:** r = 0.909

**Example Conversions:**
| KOOS Pain | Inverted | Predicted WOMAC | Interpretation |
|-----------|----------|-----------------|----------------|
| 0 (worst) | 100 | 76.9 | Severe pain |
| 25 | 75 | 57.6 | Moderate-severe |
| 50 | 50 | 38.4 | Moderate |
| 75 | 25 | 19.1 | Mild |
| 100 (best) | 0 | -0.2\* | No pain |

\*Note: Formula predicts slightly negative at best KOOS, but actual range is 0-96

---

### 2. CESD (Depression Scale)

#### Data Availability

- **21 items** in CESD scale
- **4,731 patients** (98.6%) have complete CESD data
- **Correlation with WOMAC:** r = 0.277 (weak)

#### Assessment

- ❌ **Not suitable as WOMAC replacement**
- Weak correlation indicates different construct (depression vs knee symptoms)
- Not knee-specific
- Useful as additional predictor, but not as primary outcome measure

---

### 3. Other Subjective Measures

#### SF-36 (Quality of Life)

- Limited availability in OAI baseline data
- Not knee-specific
- Not assessed in detail (appears incomplete)

#### Other Pain Measures

- **V00400PAIN:** Categorical (which knee had pain during 400m walk)
  - Not a continuous scale
  - Not suitable as WOMAC replacement

---

## Feasibility Assessment

### Model Training Feasibility

**Current Model (WOMAC):**

- Training data: 4,775 patients (99.6%)

**Alternative Model (KOOS):**

- Training data: 4,793 patients (99.9%)
- **Gain:** +18 patients (0.4% increase)
- **Loss:** Only 1 patient would be excluded

**Conclusion:** ✅ **KOOS provides MORE training data, not less**

### Clinical Deployment Feasibility

**Advantages of KOOS:**

- ✅ Very strong correlation with WOMAC (r = -0.909)
- ✅ Better data completeness (99.9% vs 99.6%)
- ✅ Knee-specific and validated outcome measure
- ✅ Can convert KOOS→WOMAC with high accuracy (R² = 0.826)
- ✅ Same scale (0-100) as many clinical tools

**Considerations:**

- ⚠️ Scoring is inverted (higher = better) vs WOMAC (higher = worse)
- ⚠️ Need to verify if Bergman Clinics collect KOOS
- ⚠️ Model would need retraining or conversion layer

**Conversion Approach:**

- Option 1: Convert KOOS→WOMAC using formula, then use existing model
- Option 2: Retrain model using KOOS directly (would need outcome data with KOOS)

---

## Recommendations

### Short-Term (Immediate)

1. ✅ **KOOS is viable alternative** - has sufficient data and strong correlation
2. ✅ **Can use KOOS→WOMAC conversion** for clinics that collect KOOS
3. ⚠️ **Verify with Bergman Clinics:** Do they collect KOOS or only VAS?

### Medium-Term (Weeks 2-4)

1. If clinics collect KOOS:

   - Implement KOOS→WOMAC conversion
   - Test prediction accuracy with converted data
   - Compare with native WOMAC predictions

2. If clinics collect neither WOMAC nor KOOS:
   - Use VAS→WOMAC conversion (from previous analysis)
   - Consider KOOS as alternative if they're willing to collect it

### Long-Term (Months 2-3)

1. If KOOS adoption is high:
   - Consider training KOOS-specific model variant
   - Could improve accuracy by avoiding conversion step
   - Would need outcome data linked to KOOS scores

---

## Data Summary Table

| Measure               | Patients | % Complete | Correlation    | Suitable?             |
| --------------------- | -------- | ---------- | -------------- | --------------------- |
| **WOMAC Total Right** | 4,775    | 99.6%      | r = 1.000      | ✅ Reference          |
| **KOOS Pain Right**   | 4,793    | **99.9%**  | **r = -0.909** | ✅ **YES**            |
| KOOS Stiffness Right  | 4,796    | 100.0%     | r = -0.789     | ✅ Good               |
| KOOS Function Right   | 3,582    | 74.7%      | r = -0.730     | ⚠️ Lower completeness |
| KOOS Quality of Life  | 4,795    | 100.0%     | r = -0.666     | ✅ Good               |
| CESD (Depression)     | 4,731    | 98.6%      | r = 0.277      | ❌ Weak correlation   |
| VAS Pain              | 0        | 0%         | N/A            | ❌ Not available      |

---

## Conclusion

**YES - There is sufficient data on subjective feeling (KOOS) to potentially use it instead of WOMAC.**

**Key Points:**

1. **KOOS Pain Right** has excellent data completeness (99.9%)
2. **Very strong correlation** with WOMAC (r = -0.909)
3. **High conversion accuracy** (R² = 0.826)
4. **More data available** than WOMAC (4,793 vs 4,775 patients)
5. **Knee-specific and validated** outcome measure

**Next Steps:**

1. Verify if Bergman Clinics collect KOOS
2. If yes: Implement KOOS→WOMAC conversion
3. If no: Continue with VAS→WOMAC conversion (from previous analysis)
4. Consider KOOS as preferred alternative to VAS (better correlation than VAS)

---

## Files Referenced

- `analyze_vas_womac.py` - VAS analysis script
- `vas_conversion_fallback.py` - VAS→WOMAC conversion
- `CLINICAL_DEPLOYMENT_OPTIONS.md` - Deployment options
- `VAS_WOMAC_ANALYSIS_SUMMARY.md` - VAS analysis summary
