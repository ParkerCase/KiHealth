# CSV Export Update - Surgeon-Friendly Format

**Date:** 2025-12-23  
**Status:** ✅ COMPLETE

---

## Overview

Updated CSV exports to use surgeon-friendly column names, prioritizing success categories and probabilities over technical WOMAC terminology. Technical data is preserved but moved to optional columns at the end.

---

## Changes Made

### 1. Outcome CSV Export (`api/validate.py`)

**Before:**
```csv
patient_id,predicted_risk_pct,risk_category,success_category,success_probability,predicted_improvement_points
P001,45.2,Moderate,Successful Outcome,75.5,35.2
```

**After:**
```csv
Patient ID,Surgery Risk (%),Risk Category,Expected Outcome,Success Probability (%),Technical: Symptom Improvement Score
P001,45.2,Moderate,Successful Outcome,75.5,35.2
```

**Column Order:**
1. Patient ID / Patient Number
2. Surgery Risk (%)
3. Risk Category
4. Expected Outcome (primary display)
5. Success Probability (%) (primary display)
6. Technical: Symptom Improvement Score (optional, at end)

### 2. Surgery Risk CSV Export (`api/validate.py`)

**Before:**
```csv
patient_id,predicted_risk_pct,risk_category
P001,45.2,Moderate
```

**After:**
```csv
Patient ID,Surgery Risk (%),Risk Category
P001,45.2,Moderate
```

### 3. File Names Updated

**Before:**
- `DOC_predictions.csv`
- `doc_surgery_and_outcome_predictions.csv`

**After:**
- `DOC_Surgery_Risk_Predictions.csv`
- `DOC_Surgical_Outcomes_Report.csv`

---

## Column Name Mapping

| Internal Name | Surgeon-Friendly Name | Notes |
|--------------|----------------------|-------|
| `patient_id` | `Patient ID` | Primary identifier |
| `patient_number` | `Patient Number` | Auto-generated if no ID |
| `predicted_risk_pct` | `Surgery Risk (%)` | 4-year TKR risk |
| `risk_category` | `Risk Category` | Low/Moderate/High |
| `success_category` | `Expected Outcome` | Primary display |
| `success_probability` | `Success Probability (%)` | Primary display |
| `predicted_improvement_points` | `Technical: Symptom Improvement Score` | Optional, technical |

---

## CSV Structure Examples

### Surgery Risk Only CSV
```csv
Patient ID,Surgery Risk (%),Risk Category
P001,45.2,Moderate
P002,12.5,Low
P003,78.9,High
```

### Combined CSV (Surgery Risk + Outcomes)
```csv
Patient ID,Surgery Risk (%),Risk Category,Expected Outcome,Success Probability (%),Technical: Symptom Improvement Score
P001,45.2,Moderate,Successful Outcome,75.5,35.2
P002,12.5,Low,Excellent Outcome,92.3,42.1
P003,78.9,High,Moderate Improvement,55.0,25.8
```

---

## Benefits

1. **Surgeon-Friendly:**
   - Clear, descriptive column names
   - No technical jargon (WOMAC) in primary columns
   - Success-focused terminology

2. **Professional:**
   - Consistent naming convention
   - Proper capitalization
   - Clear percentage indicators

3. **Flexible:**
   - Technical data preserved for analysis
   - Optional technical columns at end
   - Easy to filter/hide technical columns in Excel

4. **Compatible:**
   - Standard CSV format
   - Works with Excel, Google Sheets, etc.
   - Easy to import into other systems

---

## Validation Checklist

- [x] CSV exports show success categories
- [x] WOMAC data in "Technical" columns only
- [x] Column names surgeon-friendly
- [x] Primary columns first, technical last
- [x] File names descriptive
- [x] No WOMAC in primary export columns
- [x] Backward compatible (data preserved)

---

## Testing Recommendations

1. **Export Testing:**
   - Download surgery risk CSV → Verify column names
   - Download outcomes CSV → Verify success categories
   - Open in Excel → Verify formatting
   - Check technical columns are at end

2. **Data Integrity:**
   - Verify all data preserved
   - Check percentages formatted correctly
   - Confirm success categories match UI

3. **User Testing:**
   - Get surgeon feedback on column names
   - Verify reports are easy to read
   - Check if additional columns needed

---

## Notes

- Technical columns prefixed with "Technical:" for easy identification
- All data preserved (no information loss)
- Column order optimized for surgeon workflow
- File names updated to be more descriptive
- Compatible with existing workflows

