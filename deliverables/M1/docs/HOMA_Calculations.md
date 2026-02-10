# HOMA Calculations

Formulas and validation for HOMA-IR and HOMA-beta used in KiHealth Diabetes M1.

## Formulas (Matthews et al.)

- **HOMA-IR** (insulin resistance):  
  `HOMA-IR = (fasting_glucose_mg_dL × fasting_insulin_μU_mL) / 405`

- **HOMA-beta** (beta-cell function):  
  `HOMA-beta = (360 × fasting_insulin_μU_mL) / (fasting_glucose_mg_dL − 63)`

**Units:**
- Fasting plasma/serum glucose: **mg/dL**
- Fasting serum insulin: **μU/mL** (same as mU/L)

**Important:** HOMA is only valid with **fasting** glucose and insulin. Do not use 2-hour OGTT insulin (e.g. Pima Indians / Frankfurt dataset); those samples are flagged `invalid_homa_flag=True` and excluded from HOMA modeling.

**Reference:** Matthews DR, et al. Homeostasis model assessment: insulin resistance and beta-cell function from fasting plasma glucose and insulin concentrations in man. *Diabetologia* 1985;28(7):412–419.

## Unit conversion

- **Glucose mmol/L → mg/dL:**  
  `glucose_mg_dL = glucose_mmol_L × 18.0182`
- **Glucose mg/dL → mmol/L:**  
  `glucose_mmol_L = glucose_mg_dL / 18.0182`

Use mg/dL in the formulas above; convert from mmol/L when needed (e.g. NHANES LBDGLUSI, Manchester CGM).

## Edge cases

| Case | HOMA-IR | HOMA-beta |
|------|--------|-----------|
| Missing glucose or insulin | NaN | NaN |
| Glucose ≤ 0 or insulin ≤ 0 | NaN | NaN |
| Glucose ≤ 63 mg/dL | Valid if insulin > 0 | NaN (denominator ≤ 0) |

Implementation: `src/features/homa_calculations.py` returns NaN for invalid inputs and supports both scalars and pandas Series.

## Validation

- **Numerical check:**  
  Glucose = 100 mg/dL, Insulin = 10 μU/mL  
  → HOMA-IR = 100×10/405 ≈ 2.47  
  → HOMA-beta = 360×10/(100−63) ≈ 97.3  

- **Unit tests:**  
  `pytest tests/test_homa_calculations.py`

## Data source mapping

| Source | Glucose variable | Insulin variable | Units |
|--------|-------------------|------------------|--------|
| NIHANES | LBXGLU | LBXIN | mg/dL, μU/mL |
| Frankfurt | Glucose | Insulin | mg/dL, μU/mL |
| DiaBD | Glucose | Insulin | mg/dL, μU/mL |

Use these variables with `add_homa_columns()` or `homa_ir()` / `homa_beta()` directly.
