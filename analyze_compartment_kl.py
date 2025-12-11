#!/usr/bin/env python3
"""
Determine if OAI has compartment-specific KL grades (medial, lateral, patellofemoral)
and assess if adding them improves model
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import chi2_contingency, pearsonr
import warnings

warnings.filterwarnings("ignore")

print("=" * 80)
print("COMPARTMENT-SPECIFIC KL GRADE SEARCH")
print("=" * 80)

# Load baseline data
base_path = Path(__file__).parent
baseline_file = base_path / "data" / "raw" / "AllClinical_ASCII" / "AllClinical00.txt"

print(f"\nLoading baseline data from: {baseline_file}")
baseline = pd.read_csv(baseline_file, sep="|", low_memory=False)

print(f"Total patients: {len(baseline)}")
print(f"Total columns: {len(baseline.columns)}")

# Search for KL-related columns
kl_patterns = ["KL", "KELLGREN", "LAWRENCE", "GRADE", "SEVERITY"]
kl_cols = []
for col in baseline.columns:
    col_upper = col.upper()
    if any(p in col_upper for p in kl_patterns):
        kl_cols.append(col)

print(f"\nFound {len(kl_cols)} KL-related columns:")
for col in sorted(kl_cols)[:30]:
    print(f"  - {col}")
if len(kl_cols) > 30:
    print(f"  ... and {len(kl_cols) - 30} more")

# Search for compartment indicators
compartment_patterns = [
    "MEDIAL",
    "LATERAL",
    "PATELLO",
    "PF",
    "TF",
    "COMPARTMENT",
    "TFJ",  # Tibiofemoral joint
    "PFJ",  # Patellofemoral joint
]
compartment_cols = []
for col in kl_cols:
    col_upper = col.upper()
    if any(p in col_upper for p in compartment_patterns):
        compartment_cols.append(col)

print(f"\nCompartment-specific columns: {len(compartment_cols)}")
if compartment_cols:
    for col in sorted(compartment_cols):
        n_valid = baseline[col].notna().sum()
        completeness = n_valid / len(baseline) * 100
        print(f"\n  {col}:")
        print(f"    Completeness: {n_valid} ({completeness:.1f}%)")
        if n_valid > 0:
            value_counts = baseline[col].value_counts()
            print(f"    Values: {dict(value_counts.head(10))}")
else:
    print("  None found")

# Also check X-ray files which might have compartment data
print("\n" + "=" * 80)
print("CHECKING X-RAY FILES FOR COMPARTMENT DATA")
print("=" * 80)

xray_dir = base_path / "data" / "raw"
xray_file = list(xray_dir.glob("**/kxr_sq_bu00.txt"))
if xray_file:
    try:
        xray_data = pd.read_csv(xray_file[0], sep="|", low_memory=False)
        print(f"\nX-ray file: kxr_sq_bu00.txt")
        print(f"  Total rows: {len(xray_data)}")
        print(f"  Columns: {len(xray_data.columns)}")

        # Check for compartment columns (L/M suffixes = Lateral/Medial)
        # JSN = Joint Space Narrowing (compartment-specific)
        compartment_xray_cols = []
        for col in xray_data.columns:
            col_upper = col.upper()
            # Look for JSN (Joint Space Narrowing) with L/M suffixes
            if "JSN" in col_upper and (col.endswith("L") or col.endswith("M")):
                compartment_xray_cols.append(("kxr_sq_bu00.txt", col))
                print(f"    Found compartment JSN: {col}")

        # Check if there's a separate KL column per compartment
        # Overall KL is V00XRKL, check if there are compartment-specific KL
        kl_cols = [c for c in xray_data.columns if "KL" in c.upper()]
        print(f"\n  KL-related columns: {kl_cols}")

        # Note: L/M suffixes in X-ray file indicate Lateral/Medial compartments
        # These are JSN (Joint Space Narrowing) measures, not KL grades
        # But they are compartment-specific and could be used as predictors
    except Exception as e:
        print(f"  Error reading X-ray file: {e}")
        compartment_xray_cols = []
else:
    compartment_xray_cols = []

# ============================================================================
# STEP 2: Analyze Compartment Data if Available
# ============================================================================
all_compartment_cols = compartment_cols + [col for _, col in compartment_xray_cols]

if all_compartment_cols:
    print("\n" + "=" * 80)
    print("COMPARTMENT DATA ANALYSIS")
    print("=" * 80)

    # Find overall KL columns
    overall_kl_right = None
    overall_kl_left = None

    # Common overall KL column names
    kl_candidates = [
        "V00XRKLR",
        "V00XRKLL",
        "V00XRKL",
        "V00KLGR",
        "V00KLGL",
    ]

    for col in baseline.columns:
        col_upper = col.upper()
        if "KL" in col_upper and "RIGHT" in col_upper:
            overall_kl_right = col
        elif "KL" in col_upper and "LEFT" in col_upper:
            overall_kl_left = col

    # Also check X-ray files for overall KL
    if not overall_kl_right or not overall_kl_left:
        # Try loading X-ray file
        xray_file = list(xray_dir.glob("**/kxr_sq_bu00.txt"))
        if xray_file:
            try:
                xray_data = pd.read_csv(
                    xray_file[0], sep="|", low_memory=False, nrows=1000
                )
                for col in xray_data.columns:
                    col_upper = col.upper()
                    if "KL" in col_upper and "SIDE" in xray_data.columns:
                        # This might be the KL column
                        if overall_kl_right is None:
                            overall_kl_right = col
                        if overall_kl_left is None:
                            overall_kl_left = col
            except:
                pass

    print(f"\nOverall KL columns:")
    print(f"  Right: {overall_kl_right}")
    print(f"  Left: {overall_kl_left}")

    # Analyze each compartment column
    for col in all_compartment_cols:
        if col in baseline.columns:
            print(f"\n{col}:")
            n_valid = baseline[col].notna().sum()
            completeness = n_valid / len(baseline) * 100
            print(f"  Complete: {n_valid} ({completeness:.1f}%)")

            if n_valid > 0:
                value_counts = baseline[col].value_counts().sort_index()
                print(f"  Distribution:")
                for val, count in value_counts.items():
                    pct = count / n_valid * 100
                    print(f"    Grade {val}: {count} ({pct:.1f}%)")

                # Test correlation with overall KL if available
                if overall_kl_right and "RIGHT" in col.upper() or "R" in col.upper():
                    if overall_kl_right in baseline.columns:
                        merged = baseline[[col, overall_kl_right]].dropna()
                        if len(merged) > 50:
                            try:
                                corr = pearsonr(
                                    pd.to_numeric(merged[col], errors="coerce"),
                                    pd.to_numeric(
                                        merged[overall_kl_right], errors="coerce"
                                    ),
                                )
                                print(
                                    f"  Correlation with {overall_kl_right}: r = {corr[0]:.3f} (p = {corr[1]:.4f})"
                                )
                            except:
                                pass

                if overall_kl_left and ("LEFT" in col.upper() or "L" in col.upper()):
                    if overall_kl_left in baseline.columns:
                        merged = baseline[[col, overall_kl_left]].dropna()
                        if len(merged) > 50:
                            try:
                                corr = pearsonr(
                                    pd.to_numeric(merged[col], errors="coerce"),
                                    pd.to_numeric(
                                        merged[overall_kl_left], errors="coerce"
                                    ),
                                )
                                print(
                                    f"  Correlation with {overall_kl_left}: r = {corr[0]:.3f} (p = {corr[1]:.4f})"
                                )
                            except:
                                pass

else:
    print("\n⚠️ No compartment-specific KL grades found in baseline clinical data")

# ============================================================================
# STEP 3: Test Predictive Value
# ============================================================================
print("\n" + "=" * 80)
print("PREDICTIVE VALUE TEST")
print("=" * 80)

# Load outcomes
outcomes_file = base_path / "data" / "raw" / "General_ASCII" / "Outcomes99.txt"
print(f"\nLoading outcomes from: {outcomes_file}")

try:
    outcomes = pd.read_csv(outcomes_file, sep="|", low_memory=False)
    print(f"✅ Loaded: {len(outcomes)} patients")

    # Standardize ID column
    if "id" in outcomes.columns:
        outcomes["ID"] = outcomes["id"].astype(str).str.upper()
    if "ID" in baseline.columns:
        baseline["ID"] = baseline["ID"].astype(str).str.upper()

    # Merge with baseline
    merge_col = "ID"
    if merge_col in baseline.columns and merge_col in outcomes.columns:
        data = baseline.merge(
            outcomes[[merge_col, "V99ERKRPCF", "V99ELKRPCF"]], on=merge_col, how="left"
        )

        # Create TKR outcome (confirmed replacements)
        data["tkr"] = (
            (data["V99ERKRPCF"] == "3: Replacement adjudicated, confirmed")
            | (data["V99ELKRPCF"] == "3: Replacement adjudicated, confirmed")
        ).astype(int)

        events = data["tkr"].sum()
        print(f"\nTKR events: {events}")

        # Test univariate associations for compartment columns
        if all_compartment_cols:
            print("\nUnivariate associations with TKR:")
            compartment_results = []

            for col in all_compartment_cols:
                if col in data.columns:
                    n_valid = data[[col, "tkr"]].dropna()
                    if len(n_valid) > 100:  # Need sufficient data
                        # Convert to numeric
                        n_valid[col] = pd.to_numeric(n_valid[col], errors="coerce")
                        n_valid = n_valid.dropna()

                        if len(n_valid) > 100:
                            # Create contingency table
                            n_valid["grade_cat"] = pd.cut(
                                n_valid[col],
                                bins=[-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
                                labels=[0, 1, 2, 3, 4],
                            )
                            crosstab = pd.crosstab(n_valid["grade_cat"], n_valid["tkr"])

                            if crosstab.shape[0] > 1 and crosstab.shape[1] > 1:
                                try:
                                    chi2, p, dof, expected = chi2_contingency(crosstab)

                                    print(f"\n  {col}:")
                                    print(f"    N: {len(n_valid)}")
                                    print(f"    Chi-square: {chi2:.2f}")
                                    print(f"    P-value: {p:.4f}")
                                    print(
                                        f"    Significant: {'Yes' if p < 0.05 else 'No'}"
                                    )

                                    compartment_results.append(
                                        {
                                            "column": col,
                                            "n": len(n_valid),
                                            "chi2": chi2,
                                            "p_value": p,
                                            "significant": p < 0.05,
                                        }
                                    )
                                except:
                                    pass

        # EPV Analysis
        print("\n" + "=" * 80)
        print("EPV ANALYSIS")
        print("=" * 80)

        current_predictors = 10  # Current model
        current_epv = events / current_predictors

        print(f"\nCurrent model:")
        print(f"  Events: {events}")
        print(f"  Predictors: {current_predictors}")
        print(f"  EPV: {current_epv:.1f}")
        print(
            f"  Status: {'✓ Top 7%' if current_epv >= 15 else '⚠ Borderline' if current_epv >= 10 else '✗ Insufficient'}"
        )

        # Count unique compartment columns (per knee)
        if all_compartment_cols:
            # Group by knee (right/left)
            right_compartments = [
                c
                for c in all_compartment_cols
                if c in data.columns
                and ("RIGHT" in c.upper() or "R" in c.upper())
                and "LEFT" not in c.upper()
            ]
            left_compartments = [
                c
                for c in all_compartment_cols
                if c in data.columns
                and ("LEFT" in c.upper() or "L" in c.upper())
                and "RIGHT" not in c.upper()
            ]

            # Count unique compartment types (medial, lateral, PF)
            compartment_types = set()
            for col in all_compartment_cols:
                col_upper = col.upper()
                if "MEDIAL" in col_upper:
                    compartment_types.add("medial")
                elif "LATERAL" in col_upper:
                    compartment_types.add("lateral")
                elif "PATELLO" in col_upper or "PF" in col_upper:
                    compartment_types.add("patellofemoral")

            n_compartment_types = len(compartment_types)
            n_new_predictors = n_compartment_types * 2  # Per knee (right + left)

            print(f"\nCompartment analysis:")
            print(
                f"  Compartment types found: {n_compartment_types} ({', '.join(compartment_types) if compartment_types else 'none'})"
            )
            print(f"  Right knee columns: {len(right_compartments)}")
            print(f"  Left knee columns: {len(left_compartments)}")
            print(f"  New predictors if added: {n_new_predictors}")

            new_predictors = current_predictors + n_new_predictors
            new_epv = events / new_predictors

            print(f"\nWith compartment grades:")
            print(f"  Events: {events}")
            print(
                f"  Predictors: {new_predictors} (current {current_predictors} + {n_new_predictors} compartments)"
            )
            print(f"  EPV: {new_epv:.1f}")
            print(
                f"  Status: {'✓ Top 7%' if new_epv >= 15 else '⚠ Borderline' if new_epv >= 10 else '✗ Insufficient'}"
            )

            if new_epv >= 15:
                print("\n✓ Can add compartment grades while maintaining top 7% quality")
            elif new_epv >= 10:
                print("\n⚠ Borderline EPV (10-15), moderate risk of bias")
            else:
                print(f"\n✗ EPV too low ({new_epv:.1f} < 15), would drop from top 7%")
                print(
                    f"  Would need {new_predictors * 15} events minimum (have {events})"
                )
        else:
            print("\n⚠️ Cannot calculate EPV impact - no compartment data available")

    else:
        print("⚠️ Cannot merge - ID columns don't match")
        print(
            f"  Baseline ID columns: {[c for c in baseline.columns if 'ID' in c.upper()]}"
        )
        print(
            f"  Outcomes ID columns: {[c for c in outcomes.columns if 'ID' in c.upper() or 'id' in c.lower()]}"
        )

except Exception as e:
    print(f"❌ Error loading outcomes: {e}")
    import traceback

    traceback.print_exc()

# ============================================================================
# Generate Report
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING REPORT")
print("=" * 80)

report = f"""# Compartment-Specific KL Grade Analysis - OAI Dataset

## Executive Summary

**Finding:** {"✓ Compartment-specific KL grades found" if all_compartment_cols else "✗ No compartment-specific KL grades in OAI baseline data"}

**Data Availability:**
- Compartment columns found: {len(all_compartment_cols)}
- Compartment types: {', '.join(compartment_types) if 'compartment_types' in locals() and compartment_types else 'None identified'}

## Compartment Columns Found

"""

if all_compartment_cols:
    report += "\n".join(f"- `{col}`" for col in all_compartment_cols)
else:
    report += "None found in baseline clinical data or X-ray files checked."

report += f"""

## EPV Impact Analysis

### Current Model
- Events: {events if 'events' in locals() else 'N/A'}
- Predictors: {current_predictors if 'current_predictors' in locals() else 10}
- EPV: {f'{current_epv:.1f}' if 'current_epv' in locals() else 'N/A'}
- Status: {"✓ Top 7%" if 'current_epv' in locals() and current_epv >= 15 else "⚠ Borderline" if 'current_epv' in locals() and current_epv >= 10 else "✗ Insufficient"}

### With Compartment Grades
"""

if all_compartment_cols and "new_epv" in locals():
    report += f"""
- Events: {events}
- Predictors: {new_predictors} (current {current_predictors} + {n_new_predictors} compartments)
- EPV: {new_epv:.1f}
- Status: {"✓ Top 7%" if new_epv >= 15 else "⚠ Borderline" if new_epv >= 10 else "✗ Insufficient"}
- Impact: {"Can add without dropping from top 7%" if new_epv >= 15 else "Would drop from top 7% (EPV < 15)" if new_epv < 15 else "Borderline"}
"""
else:
    report += """
- Cannot calculate - no compartment data available
"""

report += f"""

## Predictive Value

"""

if all_compartment_cols and "compartment_results" in locals():
    report += "Univariate associations with TKR:\n\n"
    for result in compartment_results:
        report += f"- **{result['column']}**: "
        report += f"Chi² = {result['chi2']:.2f}, p = {result['p_value']:.4f} "
        report += (
            f"({'✓ Significant' if result['significant'] else 'Not significant'})\n"
        )
else:
    report += "Cannot test - no compartment data available\n"

report += f"""

## Recommendations

"""

if not all_compartment_cols:
    report += """
### Data Not Available in OAI

**Conclusion:** OAI does not track compartment-specific KL grades (medial, lateral, patellofemoral) in the baseline clinical data.

**Options:**
1. **Use overall KL grade only** (current approach)
   - Validated and sufficient for model
   - Maintains top 7% quality

2. **Collect compartment data at Bergman Clinics**
   - Would need to add to data collection
   - Could improve model specificity
   - Requires validation

3. **Check X-ray image files directly**
   - OAI may have compartment grades in image annotations
   - Would require image analysis or manual extraction
   - Not readily available in structured format
"""
elif "new_epv" in locals():
    if new_epv >= 15:
        report += """
### Compartment Data Available and Feasible

**Conclusion:** Compartment-specific KL grades are available and can be added without dropping from top 7% quality.

**Recommendation:**
- ✅ **Add compartment grades to model**
- Maintains EPV ≥ 15
- May improve prediction accuracy
- Provides more granular risk assessment

**Implementation:**
- Add {n_new_predictors} compartment predictors (medial, lateral, PF × 2 knees)
- Total predictors: {new_predictors}
- EPV: {new_epv:.1f} (still ≥ 15)
"""
    elif new_epv >= 10:
        report += """
### Compartment Data Available but Borderline

**Conclusion:** Compartment-specific KL grades are available but adding them would drop EPV to borderline (10-15).

**Recommendation:**
- ⚠️ **Consider adding with caution**
- EPV would be borderline (moderate risk of bias)
- May still improve predictions
- Consider feature selection to reduce predictors

**Options:**
1. Add all compartments (EPV = {new_epv:.1f})
2. Add only most predictive compartments (selective)
3. Keep overall KL only (safer, EPV = {current_epv:.1f})
"""
    else:
        report += """
### Compartment Data Available but Insufficient EPV

**Conclusion:** Compartment-specific KL grades are available but adding them would drop EPV below 15.

**Recommendation:**
- ✗ **Do NOT add all compartments** (would drop from top 7%)
- EPV would be {new_epv:.1f} (need ≥ 15)
- Would need {new_predictors * 15} events minimum (have {events})

**Options:**
1. **Keep overall KL only** (recommended)
   - Maintains top 7% quality
   - EPV = {current_epv:.1f}

2. **Add only most predictive compartment**
   - Select 1-2 compartments with strongest association
   - Reduces predictor count
   - May maintain EPV ≥ 15

3. **Wait for more data**
   - Collect more outcomes
   - Reassess when EPV ≥ 15
"""

report += f"""

## Files Generated

- `COMPARTMENT_KL_ANALYSIS.md` - This document
- Analysis script: `analyze_compartment_kl.py`
"""

with open("COMPARTMENT_KL_ANALYSIS.md", "w") as f:
    f.write(report)

print("\n✓ Saved: COMPARTMENT_KL_ANALYSIS.md")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
