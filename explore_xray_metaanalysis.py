#!/usr/bin/env python3
"""
Explore X-Ray Metaanalysis dataset for compartment-specific OARSI scores
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

print("=" * 80)
print("X-RAY METAANALYSIS EXPLORATION - OARSI COMPARTMENT SCORES")
print("=" * 80)

base_path = Path("/Users/parkercase/DOC/data/raw")

# Find all metaanalysis files
print("\n1. SEARCHING FOR X-RAY METAANALYSIS FILES")
print("=" * 80)

meta_files = []
for pattern in ["**/*meta*.txt", "**/*Meta*.txt", "**/*META*.txt"]:
    meta_files.extend(list(base_path.glob(pattern)))

# Also check X-Ray directories specifically
xray_dir = base_path / "X-Ray Image Assessments_ASCII"
if xray_dir.exists():
    for subdir in xray_dir.iterdir():
        if subdir.is_dir():
            meta_files.extend(list(subdir.glob("*meta*.txt")))
            meta_files.extend(list(subdir.glob("*Meta*.txt")))

# Remove duplicates
meta_files = list(set(meta_files))

print(f"\nFound {len(meta_files)} potential metaanalysis files:")
for f in sorted(meta_files):
    print(f"  - {f.relative_to(base_path)}")

# Focus on baseline (V00 or 00 suffix)
baseline_meta_files = [
    f
    for f in meta_files
    if "00" in f.stem or "V00" in f.stem or "baseline" in f.stem.lower()
]

print(f"\nBaseline files (V00/00): {len(baseline_meta_files)}")
for f in sorted(baseline_meta_files):
    print(f"  - {f.relative_to(base_path)}")

# ============================================================================
# 2. LOAD AND SEARCH FOR OARSI COMPARTMENT VARIABLES
# ============================================================================
print("\n" + "=" * 80)
print("2. SEARCHING FOR OARSI COMPARTMENT VARIABLES")
print("=" * 80)

oarsi_keywords = ["OARSI", "JSN", "OST", "OSTEO", "COMP", "COMPARTMENT"]
compartment_keywords = ["MED", "LAT", "LATERAL", "MEDIAL", "PF", "PATELLO", "TF"]

oarsi_variables = []
all_columns = {}

for file_path in baseline_meta_files:
    try:
        print(f"\n📄 Loading: {file_path.name}")
        df = pd.read_csv(file_path, sep="|", low_memory=False, nrows=1000)

        print(f"   Columns: {len(df.columns)}")
        print(f"   Rows (sample): {len(df)}")

        # Search for OARSI-related columns
        oarsi_cols = []
        for col in df.columns:
            col_upper = col.upper()
            # Check if contains OARSI or compartment-related terms
            has_oarsi = any(kw in col_upper for kw in oarsi_keywords)
            has_compartment = any(kw in col_upper for kw in compartment_keywords)

            if has_oarsi or (
                has_compartment and ("JSN" in col_upper or "OST" in col_upper)
            ):
                oarsi_cols.append(col)
                oarsi_variables.append(
                    {
                        "file": file_path.name,
                        "variable": col,
                        "has_oarsi": "OARSI" in col_upper,
                        "has_jsn": "JSN" in col_upper,
                        "has_ost": "OST" in col_upper or "OSTEO" in col_upper,
                        "has_compartment": has_compartment,
                    }
                )

        if oarsi_cols:
            print(f"   ✅ Found {len(oarsi_cols)} OARSI/compartment-related columns:")
            for col in oarsi_cols[:10]:
                print(f"      - {col}")
            if len(oarsi_cols) > 10:
                print(f"      ... and {len(oarsi_cols) - 10} more")

        all_columns[file_path.name] = {
            "columns": list(df.columns),
            "n_rows": len(df),
            "oarsi_cols": oarsi_cols,
        }

    except Exception as e:
        print(f"   ❌ Error reading {file_path.name}: {e}")

# If no baseline files found, check all meta files
if not baseline_meta_files and meta_files:
    print("\n⚠️  No baseline-specific files found, checking all meta files...")
    for file_path in meta_files[:5]:  # Check first 5
        try:
            print(f"\n📄 Loading: {file_path.name}")
            df = pd.read_csv(file_path, sep="|", low_memory=False, nrows=100)

            oarsi_cols = [
                c
                for c in df.columns
                if any(kw in c.upper() for kw in oarsi_keywords + compartment_keywords)
            ]

            if oarsi_cols:
                print(f"   ✅ Found {len(oarsi_cols)} potential columns:")
                for col in oarsi_cols[:10]:
                    print(f"      - {col}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

# ============================================================================
# 3. DETAILED ANALYSIS OF OARSI VARIABLES
# ============================================================================
print("\n" + "=" * 80)
print("3. DETAILED OARSI VARIABLE ANALYSIS")
print("=" * 80)

if not oarsi_variables:
    print("\n❌ No OARSI compartment variables found in metaanalysis files")
    print("   Checking if metaanalysis files exist in different location...")

    # Check if there's a separate metaanalysis directory
    meta_dirs = [
        base_path / "X-Ray Image Assessments_ASCII" / "Metaanalysis",
        base_path / "X-Ray Image Assessments_ASCII" / "Meta",
        base_path / "X-Ray Metaanalysis_ASCII",
    ]

    for meta_dir in meta_dirs:
        if meta_dir.exists():
            print(f"\n✅ Found metaanalysis directory: {meta_dir}")
            meta_files = list(meta_dir.glob("*.txt"))
            print(f"   Files: {len(meta_files)}")
            for f in meta_files[:5]:
                print(f"      - {f.name}")

            # Load baseline file if exists
            baseline_file = None
            for f in meta_files:
                if "00" in f.stem or "V00" in f.stem or "baseline" in f.stem.lower():
                    baseline_file = f
                    break

            if baseline_file:
                try:
                    print(f"\n📄 Loading baseline: {baseline_file.name}")
                    df = pd.read_csv(
                        baseline_file, sep="|", low_memory=False, nrows=1000
                    )

                    print(f"   Columns: {len(df.columns)}")
                    print(f"   Sample columns: {list(df.columns[:20])}")

                    # Search for OARSI
                    oarsi_cols = [
                        c
                        for c in df.columns
                        if any(
                            kw in c.upper()
                            for kw in oarsi_keywords + compartment_keywords
                        )
                    ]

                    if oarsi_cols:
                        print(
                            f"\n   ✅ Found {len(oarsi_cols)} OARSI/compartment columns:"
                        )
                        for col in oarsi_cols:
                            print(f"      - {col}")
                            oarsi_variables.append(
                                {
                                    "file": baseline_file.name,
                                    "variable": col,
                                    "has_oarsi": "OARSI" in col.upper(),
                                    "has_jsn": "JSN" in col.upper(),
                                    "has_ost": "OST" in col.upper(),
                                    "has_compartment": any(
                                        kw in col.upper() for kw in compartment_keywords
                                    ),
                                }
                            )
                except Exception as e:
                    print(f"   ❌ Error: {e}")

# ============================================================================
# 4. ANALYZE OARSI VARIABLES IF FOUND
# ============================================================================
if oarsi_variables:
    print("\n" + "=" * 80)
    print("4. OARSI VARIABLE DETAILS")
    print("=" * 80)

    # Group by file
    variables_by_file = {}
    for var in oarsi_variables:
        file = var["file"]
        if file not in variables_by_file:
            variables_by_file[file] = []
        variables_by_file[file].append(var)

    # Load full data for analysis
    oarsi_details = []

    for file_name, vars_list in variables_by_file.items():
        # Find the file
        file_path = None
        for f in meta_files + list(base_path.glob("**/*.txt")):
            if f.name == file_name:
                file_path = f
                break

        if file_path and file_path.exists():
            try:
                print(f"\n📊 Analyzing: {file_name}")
                df = pd.read_csv(file_path, sep="|", low_memory=False)

                print(f"   Total patients: {len(df)}")

                for var_info in vars_list:
                    col = var_info["variable"]
                    if col in df.columns:
                        n_valid = df[col].notna().sum()
                        completeness = n_valid / len(df) * 100

                        # Determine compartment
                        col_upper = col.upper()
                        compartment = "Unknown"
                        if "MED" in col_upper or "MEDIAL" in col_upper:
                            compartment = "Medial TF"
                        elif "LAT" in col_upper or "LATERAL" in col_upper:
                            compartment = "Lateral TF"
                        elif "PF" in col_upper or "PATELLO" in col_upper:
                            compartment = "Patellofemoral"

                        # Determine feature
                        feature = "Unknown"
                        if "JSN" in col_upper:
                            feature = "Joint Space Narrowing"
                        elif "OST" in col_upper or "OSTEO" in col_upper:
                            feature = "Osteophyte"
                        elif "SCL" in col_upper or "SCLEROSIS" in col_upper:
                            feature = "Subchondral Sclerosis"
                        elif "CYS" in col_upper or "CYST" in col_upper:
                            feature = "Subchondral Cyst"

                        # Get scale
                        if pd.api.types.is_numeric_dtype(df[col]):
                            scale_min = df[col].min()
                            scale_max = df[col].max()
                            unique_vals = sorted(df[col].dropna().unique())
                            scale = f"{scale_min:.0f}-{scale_max:.0f}"
                        else:
                            unique_vals = df[col].dropna().unique()
                            scale = f"{len(unique_vals)} categories"

                        oarsi_details.append(
                            {
                                "variable": col,
                                "file": file_name,
                                "compartment": compartment,
                                "feature": feature,
                                "scale": scale,
                                "n_available": n_valid,
                                "completeness_pct": completeness,
                                "is_oarsi": var_info["has_oarsi"],
                            }
                        )

                        print(f"\n   {col}:")
                        print(f"      Compartment: {compartment}")
                        print(f"      Feature: {feature}")
                        print(f"      Scale: {scale}")
                        print(f"      Available: {n_valid} ({completeness:.1f}%)")

            except Exception as e:
                print(f"   ❌ Error analyzing {file_name}: {e}")

# ============================================================================
# 5. CREATE SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 80)
print("5. GENERATING SUMMARY REPORT")
print("=" * 80)

report = """# X-Ray Metaanalysis - OARSI Compartment Scores Analysis

## Executive Summary

"""

if oarsi_variables:
    report += f"""**Finding:** ✅ **OARSI compartment-specific scores FOUND** in X-Ray Metaanalysis dataset

**Total Variables Found:** {len(oarsi_variables)}
**Files Containing OARSI Data:** {len(variables_by_file) if 'variables_by_file' in locals() else 1}

"""
else:
    report += """**Finding:** ❌ **No OARSI compartment-specific scores found** in X-Ray Metaanalysis files checked

**Note:** OAI may not have separate metaanalysis files, or OARSI compartment scores may be in the standard X-Ray Assessment files (which we already checked).

"""

report += f"""
## Files Checked

"""

if meta_files:
    report += f"**Total metaanalysis files found:** {len(meta_files)}\n\n"
    for f in sorted(meta_files)[:10]:
        report += f"- `{f.relative_to(base_path)}`\n"
    if len(meta_files) > 10:
        report += f"- ... and {len(meta_files) - 10} more\n"
else:
    report += "**No metaanalysis files found in expected locations**\n\n"
    report += "**Searched locations:**\n"
    report += "- `X-Ray Image Assessments_ASCII/**/*meta*.txt`\n"
    report += "- `X-Ray Metaanalysis_ASCII/` (if exists)\n"

if baseline_meta_files:
    report += f"\n**Baseline files (V00/00):** {len(baseline_meta_files)}\n\n"
    for f in sorted(baseline_meta_files):
        report += f"- `{f.relative_to(base_path)}`\n"

report += f"""
## OARSI Compartment Variables

"""

if oarsi_variables and "oarsi_details" in locals():
    report += f"""
### Summary Table

| Variable | Description | Compartment | Feature | Scale | N Available | % Complete |
|----------|-------------|-------------|---------|-------|-------------|------------|
"""

    for detail in oarsi_details:
        report += f"| `{detail['variable']}` | {detail['feature']} | {detail['compartment']} | {detail['feature']} | {detail['scale']} | {detail['n_available']} | {detail['completeness_pct']:.1f}% |\n"

    # Group by compartment
    compartments_found = set(d["compartment"] for d in oarsi_details)
    features_found = set(d["feature"] for d in oarsi_details)

    report += f"""
### Compartments Scored

"""
    for comp in sorted(compartments_found):
        comp_vars = [d for d in oarsi_details if d["compartment"] == comp]
        report += f"- **{comp}**: {len(comp_vars)} variables\n"

    report += f"""
### Features Scored

"""
    for feat in sorted(features_found):
        feat_vars = [d for d in oarsi_details if d["feature"] == feat]
        report += f"- **{feat}**: {len(feat_vars)} variables\n"

    # Data completeness
    total_patients = 4796
    if oarsi_details:
        max_available = max(d["n_available"] for d in oarsi_details)
        max_completeness = max(d["completeness_pct"] for d in oarsi_details)

        report += f"""
### Data Completeness

- **Total OAI patients:** {total_patients}
- **Max patients with OARSI data:** {max_available} ({max_completeness:.1f}%)
- **Variables with >90% completeness:** {len([d for d in oarsi_details if d['completeness_pct'] >= 90])}
- **Variables with >50% completeness:** {len([d for d in oarsi_details if d['completeness_pct'] >= 50])}

"""

else:
    report += """
**No OARSI compartment variables found.**

This could mean:
1. OARSI compartment scores are not in metaanalysis files (may be in standard X-Ray Assessment files)
2. Metaanalysis files use different naming conventions
3. OARSI compartment scoring was not performed in OAI

"""

report += f"""
## Comparison with Standard X-Ray Files

**Standard X-Ray Assessment files we already checked:**
- `kxr_sq_bu00.txt` - Contains overall KL grades and JSN (medial/lateral)
- `kxr_qjsw_duryea00.txt` - Contains quantitative JSW measurements

**What we found in standard files:**
- ✅ Overall KL grade (V00XRKL)
- ✅ Compartment-specific JSN (V00XRJSL, V00XRJSM)
- ❌ Compartment-specific KL grades
- ❌ OARSI compartment scores

"""

if oarsi_variables:
    report += """
**What metaanalysis files add:**
- ✅ OARSI compartment-specific scores
- ✅ More detailed compartment scoring

"""
else:
    report += """
**What metaanalysis files add:**
- ❌ No additional OARSI compartment scores found

**Conclusion:** OARSI compartment scores are likely not available in OAI, or are in the standard X-Ray Assessment files (which we already checked).

"""

report += f"""
## Recommendations

"""

if oarsi_variables:
    report += """
1. ✅ **Use OARSI compartment scores from metaanalysis files**
   - More granular than overall KL grade
   - Compartment-specific severity assessment
   - Could improve model specificity

2. ⚠️ **Assess EPV impact**
   - Adding compartment scores would increase predictor count
   - Need to ensure EPV remains ≥ 15

3. 📋 **Integration considerations**
   - May need to merge metaanalysis files with main dataset
   - Check for ID matching issues
   - Validate completeness

"""
else:
    report += """
1. ✅ **Continue using overall KL grade** (current approach)
   - Validated and sufficient
   - Maintains top 7% quality
   - No additional data needed

2. 📋 **If compartment scores needed:**
   - Would need to collect at Bergman Clinics
   - OAI does not appear to have OARSI compartment scores
   - Standard X-Ray files have JSN but not OARSI compartment KL grades

"""

report += f"""
## Files Generated

- `explore_xray_metaanalysis.py` - Analysis script
- `XRAY_METAANALYSIS_OARSI_REPORT.md` - This document

"""

with open("XRAY_METAANALYSIS_OARSI_REPORT.md", "w") as f:
    f.write(report)

print("\n✅ Saved: XRAY_METAANALYSIS_OARSI_REPORT.md")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
