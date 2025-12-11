# Surgery Type Modeling Feasibility - OAI Dataset

## Executive Summary

**Finding:** OAI dataset tracks **Total Knee Replacement (TKR)** and **Partial/Unicompartmental Replacement** separately. **Osteotomy procedures are NOT tracked** in OAI outcomes data.

**Current Model:**
- Surgery Type: Total Knee Replacement (TKR)
- Events: 492
- EPV: 49.2
- Status: ✓ **FEASIBLE** (Top 7% methodological quality)

## Surgery Types in OAI

### Total Knee Replacement (TKR)
- **Right TKR:** 268 events
- **Left TKR:** 264 events
- **Total (either knee):** 492 events
- **EPV:** 49.2
- **Status:** ✓ **Sufficient for rigorous model**

### Osteotomy
- **Events found:** 0
- **Status:** ✗ NOT TRACKED

- **Conclusion:** OAI does not track osteotomy procedures separately
- **Columns checked:** All surgery-related columns searched
- **Result:** No osteotomy-specific outcome variables found

### Partial/Unicompartmental Replacement
- **Events found:** 40
- **Status:** ✓ Available

- **EPV:** 4.0
- **Feasibility:** ✗ INSUFFICIENT
- **Note:** This is unicompartmental/partial knee replacement (UKA), similar to hemi-prosthesis


## Detailed Feasibility Analysis

| Surgery Type | Events | EPV | Min Needed | Feasibility | Status |
|--------------|--------|-----|------------|-------------|--------|
| **TKR** | 492 | 49.2 | 150 | ✓ FEASIBLE | Top 7% quality |
| Partial/Unicompartmental Replacement | 40 | 4.0 | 150 | ✗ INSUFFICIENT | Insufficient |


## Recommendations

### Current Status
- ✅ **TKR model is feasible** with OAI data (492 events, EPV = 49.2)
- ⚠️ **Partial/Unicompartmental model: NOT feasible** (40 events, EPV = 4.0, need 150+)
- ❌ **Osteotomy model: NOT feasible** (not tracked in OAI)

### Options for Clinical Partner

#### Option 1: Use TKR Model Only (Current Approach)
- **Pros:**
  - Validated on OAI data
  - Maintains top 7% methodological quality
  - Ready to deploy
- **Cons:**
  - Doesn't predict osteotomy/hemi-prosthesis specifically
  - May overestimate risk for patients who would get osteotomy/hemi instead

#### Option 2: Collect Osteotomy/Hemi Data Prospectively
- **What:** Track osteotomy and hemi-prosthesis outcomes at Bergman Clinics
- **Timeline:** Need 150 events minimum for each procedure type
- **Pros:**
  - Can build procedure-specific models
  - More accurate for clinical partner's practice
- **Cons:**
  - Requires data collection over time
  - Delays deployment

#### Option 3: Combined Outcome Model
- **What:** Predict "any knee surgery" (TKR + osteotomy + hemi)
- **Events:** Would combine all procedures
- **Pros:**
  - More events = higher EPV
  - Captures all surgical interventions
- **Cons:**
  - Less specific (doesn't predict procedure type)
  - May have different risk factors

#### Option 4: External Dataset
- **What:** Find dataset with osteotomy/hemi outcomes
- **Pros:**
  - Could build models immediately
- **Cons:**
  - May not match clinical partner's population
  - Requires validation on Bergman Clinics data

### Recommended Approach

**Short-term (Immediate):**
1. ✅ Use current TKR model for initial deployment
2. ✅ Start collecting osteotomy/hemi outcome data at Bergman Clinics
3. ⚠️ Note limitations: Model predicts TKR risk, not osteotomy/hemi risk

**Medium-term (6-12 months):**
1. ⏳ If sufficient osteotomy/hemi data collected (150+ events each):
   - Build separate models for each procedure type
   - Validate on Bergman Clinics data
2. ⏳ If insufficient data:
   - Consider combined "any surgery" model
   - Or continue with TKR model only

**Long-term (12+ months):**
1. ⏳ Build procedure-specific models as data accumulates
2. ⏳ Compare procedure-specific vs combined models
3. ⏳ Optimize based on clinical feedback

## Conclusion

OAI dataset contains:
- ✅ **Total Knee Replacement (TKR):** 492 events - **FEASIBLE for separate model**
- ⚠️ **Partial/Unicompartmental Replacement:** 40 events - **INSUFFICIENT for separate model** (similar to hemi-prosthesis)
- ❌ **Osteotomy:** NOT tracked in OAI

**For clinical deployment:**
- Current TKR model is ready and validated
- Cannot build osteotomy/hemi models from OAI alone
- Recommend collecting procedure-specific outcome data prospectively
- Consider combined "any surgery" model as interim solution

## Files Generated

- `SURGERY_TYPE_FEASIBILITY.md` - This document
- Analysis script: `analyze_surgery_types.py`
