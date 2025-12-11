# Compartment-Specific KL Grade Analysis - OAI Dataset

## Executive Summary

**Finding:** ✗ **No compartment-specific KL grades** in OAI baseline data

**Alternative Finding:** ⚠️ OAI has **compartment-specific JSN (Joint Space Narrowing)** measures (medial/lateral), but these are **not KL grades**.

**Data Availability:**

- Compartment-specific KL grades: **0** (not available)
- Compartment-specific JSN measures: **2** (V00XRJSL = Lateral, V00XRJSM = Medial)
- Compartment types: Medial, Lateral (no patellofemoral KL grades)

## Compartment Columns Found

### Compartment-Specific KL Grades

**None found** - OAI does not track separate KL grades for medial, lateral, or patellofemoral compartments.

### Compartment-Specific JSN (Joint Space Narrowing)

**Found in X-ray file (`kxr_sq_bu00.txt`):**

- `V00XRJSL`: Joint Space Narrowing - Lateral compartment (0-3 scale)
- `V00XRJSM`: Joint Space Narrowing - Medial compartment (0-3 scale)

**Note:** These are **not KL grades** but are compartment-specific measures that could potentially be used as alternatives. However, they measure joint space narrowing, not overall OA severity like KL grades.

## EPV Impact Analysis

### Current Model

- Events: 425
- Predictors: 10
- EPV: 42.5
- Status: ✓ Top 7%

### With Compartment Grades

- Cannot calculate - no compartment data available

## Predictive Value

Cannot test - no compartment data available

## Recommendations

### Compartment-Specific KL Grades Not Available

**Conclusion:** OAI does **NOT** track compartment-specific KL grades (medial, lateral, patellofemoral) in the baseline clinical data.

**What OAI Has:**

- ✅ Overall KL grade per knee (V00XRKL) - **Currently used in model**
- ✅ Compartment-specific JSN measures (V00XRJSL, V00XRJSM) - **Available but not KL grades**
- ❌ Compartment-specific KL grades - **Not available**

**Options:**

1. **Use overall KL grade only** (current approach) ⭐ **RECOMMENDED**

   - Validated and sufficient for model
   - Maintains top 7% quality (EPV = 42.5)
   - KL grade is standard measure for OA severity
   - No additional data collection needed

2. **Use compartment-specific JSN as alternative** ⚠️ **NOT RECOMMENDED**

   - JSN measures joint space narrowing, not overall OA severity
   - Different scale (0-3) vs KL grade (0-4)
   - Would require validation that JSN predicts as well as KL
   - Not what clinical partner requested (they want compartment KL grades)

3. **Collect compartment KL data at Bergman Clinics** 📋 **FOR FUTURE**

   - Would need to add to data collection
   - Could improve model specificity
   - Requires validation
   - Would need to assess EPV impact (adding 2-6 predictors)

4. **Check X-ray image files directly**
   - OAI may have compartment grades in image annotations
   - Would require image analysis or manual extraction
   - Not readily available in structured format
   - Low priority given current model performance

## Files Generated

- `COMPARTMENT_KL_ANALYSIS.md` - This document
- Analysis script: `analyze_compartment_kl.py`
