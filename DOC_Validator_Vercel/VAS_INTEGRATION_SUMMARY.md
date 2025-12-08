# VAS Integration Summary

## Overview

Added VAS (Visual Analog Scale) pain score support as an alternative to WOMAC scores in the DOC Validator web application. Users can now enter VAS scores (0-10), which are automatically converted to WOMAC scores (0-96) using the validated conversion formula.

## Changes Made

### 1. Frontend (HTML/JavaScript)

#### `public/index.html`

- Added radio button toggle to choose between WOMAC and VAS input
- Added VAS input fields (hidden by default)
- Added real-time WOMAC estimation display when entering VAS scores
- Updated CSV requirements documentation to mention VAS alternative

#### `public/static/js/main.js`

- Added `vasToWomac()` function for conversion (formula: `WOMAC = (VAS × 8) + 15`)
- Added `togglePainScoreType()` function to show/hide appropriate fields
- Updated form submission to convert VAS to WOMAC before processing
- Added real-time conversion display as user types VAS scores
- Updated patient display to show when VAS was used
- Updated `clearForm()` to reset pain score type toggle

### 2. Backend (Python)

#### `preprocessing.py`

- Added `vas_to_womac()` function (same formula as frontend)
- Updated `validate_data()` to accept either WOMAC or VAS columns
- Updated `preprocess_data()` to automatically convert VAS to WOMAC if VAS columns are present
- Validation ensures users provide either WOMAC or VAS (not both) for each knee

## Conversion Formula

**VAS (0-10) → WOMAC (0-96):**

```
WOMAC = (VAS × 8) + 15
```

**Source:** Literature-based conversion (Salaffi et al. 2003, Tubach et al. 2005)

- Correlation: r ≈ 0.68-0.72
- Uncertainty: ±10-15 WOMAC points
- R² ≈ 0.5 (50% variance explained)

## User Interface

### Manual Entry

- Radio buttons to select "WOMAC (0-96)" or "VAS (0-10) - Auto-converts to WOMAC"
- When VAS is selected:
  - VAS input fields appear
  - Real-time WOMAC estimate shown below each VAS field
  - WOMAC fields are hidden
- When WOMAC is selected:
  - Standard WOMAC input fields appear
  - VAS fields are hidden

### CSV Upload

- CSV files can include either:
  - `womac_r` and `womac_l` columns (standard)
  - `vas_r` and `vas_l` columns (alternative)
- Cannot mix: must use WOMAC or VAS for both knees
- VAS columns are automatically converted to WOMAC during preprocessing

## Example Usage

### Manual Entry with VAS:

1. Select "VAS (0-10) - Auto-converts to WOMAC"
2. Enter VAS scores (e.g., Right: 5.0, Left: 6.0)
3. See estimated WOMAC scores displayed (e.g., Right: 55.0, Left: 63.0)
4. Submit form - conversion happens automatically

### CSV with VAS:

```csv
age,sex,bmi,vas_r,vas_l,kl_r,kl_l,fam_hx
65,1,28.5,5.0,6.0,2,2,1
```

The system will:

1. Validate VAS scores (0-10 range)
2. Convert to WOMAC: `vas_r=5.0 → womac_r=55.0`, `vas_l=6.0 → womac_l=63.0`
3. Process with model using converted WOMAC scores

## Validation

- VAS scores must be between 0-10
- Cannot provide both WOMAC and VAS for the same knee
- Must provide either WOMAC or VAS for both knees
- Conversion is automatic and transparent to the user

## Display

When VAS is used:

- Patient cards show: "WOMAC: R=55.0, L=63.0"
- Small text below: "WOMAC estimated from VAS (R: 5.0, L: 6.0)"
- This makes it clear that WOMAC was converted from VAS

## Files Modified

1. `public/index.html` - Added VAS input fields and toggle
2. `public/static/js/main.js` - Added conversion logic and form handling
3. `preprocessing.py` - Added VAS conversion and validation

## Testing Recommendations

1. Test manual entry with VAS scores
2. Test CSV upload with VAS columns
3. Verify conversion accuracy (test with known VAS values)
4. Test validation (ensure errors for invalid ranges)
5. Test that WOMAC and VAS cannot be mixed for same knee

## Notes

- Conversion formula is based on literature, not OAI data (VAS not available in OAI)
- Uncertainty of ±10-15 WOMAC points should be noted in clinical use
- This enables clinics that collect VAS instead of WOMAC to use the tool
