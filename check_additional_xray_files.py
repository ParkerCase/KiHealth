#!/usr/bin/env python3
"""
Check additional X-ray assessment files for compartment-specific KL grades
or other relevant data we might have missed
"""

import pandas as pd
from pathlib import Path

base_path = Path("/Users/parkercase/DOC/data/raw")

print("=" * 80)
print("CHECKING ADDITIONAL X-RAY ASSESSMENT FILES")
print("=" * 80)

# Files to check
files_to_check = {
    "Semi-Quant Scoring": [
        "X-Ray Image Assessments_ASCII/Semi-Quant Scoring_ASCII/kxr_sq_bu00.txt",
        "X-Ray Image Assessments_ASCII/Semi-Quant Scoring_ASCII/kxr_sq_rel_bu00.txt",  # Reliability study
    ],
    "Quantitative JSW": [
        "X-Ray Image Assessments_ASCII/Quant JSW_ASCII/kxr_qjsw_duryea00.txt",
        "X-Ray Image Assessments_ASCII/Quant JSW_ASCII/kxr_qjsw_rel_duryea00.txt",  # Reliability
    ],
    "Alignment": [
        "X-Ray Image Assessments_ASCII/Alignment_ASCII/kxr_fta_duryea00.txt",
    ],
}

compartment_keywords = [
    "MEDIAL",
    "LATERAL",
    "PATELLO",
    "PF",
    "COMPARTMENT",
    "TFJ",
    "PFJ",
    "JSN",  # Joint Space Narrowing
    "JSW",  # Joint Space Width
]

kl_keywords = ["KL", "KELLGREN", "LAWRENCE", "GRADE"]

results = []

for category, file_paths in files_to_check.items():
    print(f"\n{'='*80}")
    print(f"{category}")
    print(f"{'='*80}")

    for file_path in file_paths:
        full_path = base_path / file_path
        if not full_path.exists():
            print(f"\n⚠️  File not found: {file_path}")
            continue

        try:
            # Read first few rows to get column names
            df = pd.read_csv(full_path, sep="|", low_memory=False, nrows=100)

            print(f"\n📄 {full_path.name}:")
            print(f"   Columns: {len(df.columns)}")

            # Check for compartment-specific columns
            compartment_cols = []
            kl_cols = []
            jsn_cols = []

            for col in df.columns:
                col_upper = col.upper()
                # Check for compartment indicators
                if any(kw in col_upper for kw in compartment_keywords):
                    compartment_cols.append(col)
                # Check for KL grades
                if any(kw in col_upper for kw in kl_keywords):
                    kl_cols.append(col)
                # Check for JSN specifically
                if "JSN" in col_upper:
                    jsn_cols.append(col)

            if compartment_cols:
                print(f"   ✅ Compartment-related columns: {len(compartment_cols)}")
                for col in compartment_cols[:10]:
                    print(f"      - {col}")
                if len(compartment_cols) > 10:
                    print(f"      ... and {len(compartment_cols) - 10} more")

            if kl_cols:
                print(f"   📊 KL-related columns: {len(kl_cols)}")
                for col in kl_cols:
                    print(f"      - {col}")

            if jsn_cols:
                print(f"   📏 JSN columns: {len(jsn_cols)}")
                for col in jsn_cols:
                    print(f"      - {col}")

            # Check if any compartment columns also have KL
            compartment_kl = [
                c
                for c in compartment_cols
                if any(kw in c.upper() for kw in kl_keywords)
            ]
            if compartment_kl:
                print(
                    f"   ⭐ COMPARTMENT-SPECIFIC KL GRADES FOUND: {len(compartment_kl)}"
                )
                for col in compartment_kl:
                    print(f"      - {col}")
                    # Get sample data
                    if col in df.columns:
                        n_valid = df[col].notna().sum()
                        print(
                            f"        Valid: {n_valid}/{len(df)} ({n_valid/len(df)*100:.1f}%)"
                        )
                        if n_valid > 0:
                            print(
                                f"        Values: {df[col].value_counts().head(5).to_dict()}"
                            )

            results.append(
                {
                    "category": category,
                    "file": full_path.name,
                    "compartment_cols": len(compartment_cols),
                    "kl_cols": len(kl_cols),
                    "jsn_cols": len(jsn_cols),
                    "compartment_kl": len(compartment_kl),
                    "compartment_kl_names": compartment_kl,
                }
            )

        except Exception as e:
            print(f"\n❌ Error reading {file_path}: {e}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

compartment_kl_found = any(r["compartment_kl"] > 0 for r in results)

if compartment_kl_found:
    print("\n✅ COMPARTMENT-SPECIFIC KL GRADES FOUND!")
    for r in results:
        if r["compartment_kl"] > 0:
            print(f"\n  {r['file']}:")
            print(f"    Compartment KL columns: {r['compartment_kl_names']}")
else:
    print("\n❌ No compartment-specific KL grades found in additional files")

# Check Quantitative JSW files more carefully (they might have compartment-specific measures)
print("\n" + "=" * 80)
print("DETAILED CHECK: QUANTITATIVE JSW FILES")
print("=" * 80)

jsw_file = (
    base_path / "X-Ray Image Assessments_ASCII/Quant JSW_ASCII/kxr_qjsw_duryea00.txt"
)
if jsw_file.exists():
    try:
        jsw_df = pd.read_csv(jsw_file, sep="|", low_memory=False, nrows=1000)
        print(f"\n📄 {jsw_file.name}:")
        print(f"   Total columns: {len(jsw_df.columns)}")
        print(f"   Sample columns: {list(jsw_df.columns[:20])}")

        # Look for compartment indicators in column names
        compartment_jsw = [
            c
            for c in jsw_df.columns
            if any(kw in c.upper() for kw in ["MEDIAL", "LATERAL", "PF", "PATELLO"])
        ]
        if compartment_jsw:
            print(f"\n   ✅ Compartment-specific JSW columns: {len(compartment_jsw)}")
            for col in compartment_jsw:
                print(f"      - {col}")
                n_valid = jsw_df[col].notna().sum()
                if n_valid > 0:
                    print(
                        f"        Valid: {n_valid}/{len(jsw_df)} ({n_valid/len(jsw_df)*100:.1f}%)"
                    )
                    if pd.api.types.is_numeric_dtype(jsw_df[col]):
                        print(
                            f"        Range: {jsw_df[col].min():.2f} to {jsw_df[col].max():.2f}"
                        )
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

if compartment_kl_found:
    print("\n✅ Found compartment-specific KL grades!")
    print("   → Should investigate these files further")
    print("   → May need to integrate into model")
else:
    print("\n❌ No compartment-specific KL grades found")
    print("   → OAI does not appear to have this data")
    print("   → Would need to collect at Bergman Clinics if needed")

print("\n" + "=" * 80)
