# Clinical Deployment Options for Clinics Without WOMAC

## Problem

Bergman Clinics uses VAS pain scores instead of WOMAC for surgical patients.
Our model requires WOMAC scores (0-96 scale).

## Analysis Results

### VAS Data Availability in OAI

**FINDING: OAI dataset does NOT contain VAS pain scores**

- Searched all baseline clinical data (AllClinical00.txt): 4,796 patients, 1,187 columns
- Checked for columns containing: VAS, KPPN (Knee Pain), or numeric pain scales
- **Result:** No VAS columns found (V00KPPNRT, V00KPPNLT do not exist in OAI)
- Checked multiple visit files (V00-V04): No VAS data found
- OAI uses WOMAC scores exclusively for pain assessment

**Implications:**

- Cannot calculate data-driven VAS→WOMAC conversion from OAI
- Must rely on literature-based conversion formulas
- Model was trained exclusively on WOMAC data

## Deployment Options

OPTION 1: VAS Conversion (Immediate)

- Use VAS → WOMAC conversion formula
- Add disclaimer: "Estimated from VAS pain score"
- Uncertainty: ±10-15 WOMAC points
- Pros: Works with existing clinical data
- Cons: Less accurate, added uncertainty

OPTION 2: Make WOMAC Optional (Hybrid Model)

- Model works with either WOMAC or VAS
- Train alternate version using VAS if available in OAI
- Web tool: "Do you have WOMAC or VAS scores?"
- Pros: Flexible for different clinics
- Cons: Two models to maintain

OPTION 3: Simplified Pain Scale

- Create mapping: "How would you rate knee pain?"
  - 1 = No pain → WOMAC ~5
  - 2 = Mild pain → WOMAC ~20
  - 3 = Moderate pain → WOMAC ~40
  - 4 = Severe pain → WOMAC ~60
  - 5 = Extreme pain → WOMAC ~80
- Pros: Works with clinical notes
- Cons: Very rough approximation

OPTION 4: Implement WOMAC Collection

- Provide Bergman Clinics with quick WOMAC form
- Takes ~5 minutes for patients to complete
- Gold standard for validation
- Pros: Most accurate
- Cons: Requires workflow change

RECOMMENDATION: Option 1 + Option 4

- Short term: Use VAS conversion for testing
- Long term: Encourage WOMAC collection for accuracy
- Web tool: Accept both, note which was used

## Implementation Plan

### Phase 1: Enable VAS Support (This Week)

1. Add VAS → WOMAC conversion to preprocessing
2. Update web tool to accept VAS scores
3. Add disclaimer when VAS is used
4. Test with Bergman Clinics data

### Phase 2: Validation (Weeks 2-4)

1. Validate predictions using VAS-converted data
2. Compare accuracy with native WOMAC data
3. Quantify additional uncertainty from conversion

### Phase 3: Optimization (Months 2-3)

1. If accuracy is acceptable: Keep VAS option
2. If accuracy is poor: Recommend WOMAC collection
3. Potentially train VAS-specific model variant

## Next Steps

1. ✅ Check if OAI has VAS data
2. ✅ Calculate VAS-WOMAC correlation in OAI
3. ⏳ Implement conversion in web tool
4. ⏳ Get Bergman Clinics feedback

## Files Generated

- `vas_womac_conversion.json`: Data-driven conversion formulas (if available)
- `vas_conversion_fallback.py`: Literature-based fallback conversion
- `vas_womac_correlation_*.png`: Correlation plots
- `CLINICAL_DEPLOYMENT_OPTIONS.md`: This document
