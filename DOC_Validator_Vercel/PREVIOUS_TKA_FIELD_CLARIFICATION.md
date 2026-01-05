# Previous TKA Field - Clarification Document

**Date:** $(date)  
**Status:** ⚠️ **FIELD DOES NOT CURRENTLY EXIST**

---

## Current Situation

### Model Predictors (Current)
The TKR risk prediction model currently uses **8 predictors**:
1. Age (V00AGE)
2. Sex (P02SEX)
3. BMI (P01BMI)
4. WOMAC Right (V00WOMTSR)
5. WOMAC Left (V00WOMTSL)
6. KL Grade Right (V00XRKLR)
7. KL Grade Left (V00XRKLL)
8. Family History (P01FAMKR)

**❌ "Previous TKA" is NOT currently a predictor in the model.**

---

## If Adding "Previous TKA" Field

### Option 1: Add as Placeholder (No Model Impact)
- ✅ Add field to form with clear labeling
- ✅ Store data for future use
- ❌ **NOT used in current predictions**
- ✅ **PROBAST compliant** (no model changes)

### Option 2: Add as New Predictor (Requires Model Retraining)
- ✅ Add field to form
- ✅ Include in model training
- ⚠️ **Requires model retraining** with new predictor
- ⚠️ **May affect PROBAST compliance** (new predictor changes model)
- ⚠️ **Requires validation** of new model

---

## Recommended Implementation (Placeholder)

If you want to add this field for future use:

### Form Field
```html
<div class="form-field">
  <label for="previous_tka_other_knee">Previous TKA on Other Knee (Optional):</label>
  <select id="previous_tka_other_knee">
    <option value="">Not specified (defaults to No)</option>
    <option value="1">Yes - Had TKR on opposite knee</option>
    <option value="0">No - No previous TKR</option>
  </select>
  <small style="display: block; margin-top: 4px; color: #666;">
    Has the patient had total knee replacement on the opposite knee? 
    Patients who already had TKR on one knee are more likely to eventually need TKR on the other knee.
  </small>
</div>
```

### Backend Handling
- Store value but **don't use in predictions** (current model doesn't include it)
- Can be exported in CSV for future analysis
- Document that it's collected but not used in current model

---

## PROBAST Compliance Impact

### If Added as Placeholder (Option 1)
- ✅ **PROBAST Compliant** - No model changes
- ✅ Maintains top 7% status
- ✅ Field collected but not used in predictions

### If Added as Predictor (Option 2)
- ⚠️ **Requires Model Retraining**
- ⚠️ **New PROBAST Assessment Needed**
- ⚠️ **May affect compliance** depending on:
  - Sample size for new predictor
  - EPV (events per variable) ratio
  - Model performance with new predictor

---

## Recommendation

**Add as placeholder field** with clear labeling:
- ✅ Clear label: "Previous TKA on Other Knee"
- ✅ Help text explaining what it means
- ✅ Collected but not used in current predictions
- ✅ Stored for future model enhancement
- ✅ PROBAST compliant (no model changes)

This allows you to:
1. Collect the data now
2. Use it for future model improvements
3. Maintain current PROBAST compliance
4. Have clear labeling from the start

---

## Next Steps

Please confirm:
1. Do you want to add this field as a **placeholder** (not used in predictions)?
2. Or do you want to add it as a **new predictor** (requires model retraining)?

