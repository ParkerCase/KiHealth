#!/usr/bin/env python3
"""
Find alternative baseline symptom assessments in OAI that could replace/supplement WOMAC
while maintaining model quality
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
import warnings

warnings.filterwarnings("ignore")

print("=" * 80)
print("COMPREHENSIVE PAIN/FUNCTION ASSESSMENT INVENTORY - OAI BASELINE")
print("=" * 80)

# Load baseline clinical data
base_path = Path(__file__).parent
baseline_file = base_path / "data" / "raw" / "AllClinical_ASCII" / "AllClinical00.txt"

print(f"\nLoading baseline data from: {baseline_file}")
baseline = pd.read_csv(baseline_file, sep="|", low_memory=False)

print(f"\nTotal columns in baseline: {len(baseline.columns)}")
print(f"Total patients: {len(baseline)}")

# Categories to search for
assessment_keywords = {
    "Pain": ["PAIN", "ACHE", "SORE", "HURT", "DISCOMFORT", "KPPN"],
    "Function": [
        "WALK",
        "STAIR",
        "STAND",
        "SIT",
        "KNEEL",
        "SQUAT",
        "BEND",
        "CSTIME",
        "WTMWK",
        "400",
    ],
    "Symptom": ["SYMPTOM", "STIFF", "SWELL", "CATCH", "GRIND", "LOCK", "GIVE"],
    "Activity": ["ACTIVITY", "SPORT", "RECREATION", "EXERCISE", "PASE"],
    "Quality of Life": ["QUALITY", "SATISFACTION", "DAILY", "QOL", "KOOS"],
    "Severity": ["SEVERITY", "MILD", "MODERATE", "SEVERE"],
    "Frequency": ["FREQUENCY", "OFTEN", "ALWAYS", "NEVER", "SOMETIMES", "RARELY"],
}

# Find all relevant columns (exclude WOMAC itself)
assessment_columns = {}
for category, keywords in assessment_keywords.items():
    cols = []
    for col in baseline.columns:
        col_upper = col.upper()
        # Exclude WOMAC columns (we're looking for alternatives)
        if "WOM" not in col_upper and any(kw in col_upper for kw in keywords):
            cols.append(col)
    if cols:
        assessment_columns[category] = cols
        print(f"\n{category}: {len(cols)} columns")
        for col in sorted(cols)[:10]:  # Show first 10
            print(f"  - {col}")
        if len(cols) > 10:
            print(f"  ... and {len(cols)-10} more")

# Check data completeness for each
print("\n" + "=" * 80)
print("DATA COMPLETENESS ANALYSIS")
print("=" * 80)

completeness_summary = []
for category, cols in assessment_columns.items():
    for col in cols:
        n_complete = baseline[col].notna().sum()
        completeness = n_complete / len(baseline) * 100

        # Get data type and sample values
        dtype = baseline[col].dtype
        unique_count = baseline[col].nunique()

        # Get sample values (only if numeric or small number of unique values)
        sample_values = None
        if pd.api.types.is_numeric_dtype(baseline[col]):
            sample_values = baseline[col].dropna().head(5).tolist()
        elif unique_count <= 10:
            sample_values = baseline[col].value_counts().head(5).to_dict()

        completeness_summary.append(
            {
                "category": category,
                "column": col,
                "completeness_pct": completeness,
                "n_complete": n_complete,
                "data_type": str(dtype),
                "unique_values": unique_count,
                "sample_values": str(sample_values) if sample_values else "N/A",
            }
        )

# Sort by completeness
completeness_df = pd.DataFrame(completeness_summary).sort_values(
    "completeness_pct", ascending=False
)

print("\nHigh-completeness assessments (≥90% complete):")
high_complete = completeness_df[completeness_df["completeness_pct"] >= 90]
print(f"\nTotal: {len(high_complete)}")

for _, row in high_complete.head(30).iterrows():
    print(f"\n{row['column']}")
    print(f"  Category: {row['category']}")
    print(
        f"  Completeness: {row['completeness_pct']:.1f}% ({row['n_complete']} patients)"
    )
    print(f"  Type: {row['data_type']}")
    print(f"  Unique values: {row['unique_values']}")
    if row["sample_values"] != "N/A":
        print(f"  Sample: {row['sample_values']}")

completeness_df.to_csv("assessment_completeness_inventory.csv", index=False)
print("\n✓ Saved: assessment_completeness_inventory.csv")

# ============================================================================
# STEP 2: Analyze Simpler Clinical Measures (Binary/Ordinal)
# ============================================================================
print("\n" + "=" * 80)
print("SIMPLE BINARY/ORDINAL ASSESSMENTS")
print("=" * 80)

# Focus on simple yes/no or 0-4 scales
simple_assessments = []

for _, row in completeness_df.iterrows():
    col = row["column"]
    unique = row["unique_values"]
    n_complete = row["n_complete"]

    # Skip if too incomplete
    if n_complete < len(baseline) * 0.5:
        continue

    # Get actual value counts
    try:
        value_counts = baseline[col].value_counts().to_dict()
    except:
        continue

    # Binary (2-4 unique values likely yes/no/missing)
    if 2 <= unique <= 4:
        # Check if it looks binary (mostly 0/1 or Yes/No)
        unique_vals = list(value_counts.keys())
        if all(
            str(v).upper() in ["0", "1", "YES", "NO", "Y", "N", "TRUE", "FALSE"]
            for v in unique_vals
            if pd.notna(v)
        ):
            simple_assessments.append(
                {
                    "column": col,
                    "type": "binary",
                    "completeness": row["completeness_pct"],
                    "values": value_counts,
                }
            )

    # Ordinal (3-7 unique values, likely severity scales)
    elif 3 <= unique <= 7:
        # Check if numeric or looks like ordinal scale
        if pd.api.types.is_numeric_dtype(baseline[col]):
            simple_assessments.append(
                {
                    "column": col,
                    "type": "ordinal",
                    "completeness": row["completeness_pct"],
                    "values": value_counts,
                }
            )

print(f"\nFound {len(simple_assessments)} simple assessments")

print("\nBINARY ASSESSMENTS (yes/no type):")
binary = [a for a in simple_assessments if a["type"] == "binary"]
for a in sorted(binary, key=lambda x: x["completeness"], reverse=True)[:20]:
    print(f"\n{a['column']}")
    print(f"  Completeness: {a['completeness']:.1f}%")
    print(f"  Values: {a['values']}")

print("\nORDINAL ASSESSMENTS (severity scales):")
ordinal = [a for a in simple_assessments if a["type"] == "ordinal"]
for a in sorted(ordinal, key=lambda x: x["completeness"], reverse=True)[:20]:
    print(f"\n{a['column']}")
    print(f"  Completeness: {a['completeness']:.1f}%")
    print(f"  Values: {a['values']}")

# ============================================================================
# STEP 3: Test Correlation with WOMAC
# ============================================================================
print("\n" + "=" * 80)
print("CORRELATION WITH WOMAC")
print("=" * 80)

# Load WOMAC for comparison
womac_cols = [c for c in baseline.columns if "WOM" in c.upper() and "TS" in c.upper()]
print(f"\nWOMAC columns available: {womac_cols}")

# Use total WOMAC Right as reference
womac_total = "V00WOMTSR"  # WOMAC Total Right

if womac_total not in baseline.columns:
    print(f"⚠️  {womac_total} not found, checking alternatives...")
    womac_total = None
    for col in womac_cols:
        if baseline[col].notna().sum() > 100:
            womac_total = col
            break

if womac_total:
    print(f"\nUsing {womac_total} as WOMAC reference")
    print(
        f"  Completeness: {baseline[womac_total].notna().sum()} patients ({baseline[womac_total].notna().sum()/len(baseline)*100:.1f}%)"
    )

    correlations = []

    # Test correlations with high-completeness assessments
    for _, row in completeness_df[completeness_df["completeness_pct"] >= 80].iterrows():
        col = row["column"]

        # Skip WOMAC columns
        if "WOM" in col.upper():
            continue

        try:
            # Get numeric version if possible
            if pd.api.types.is_numeric_dtype(baseline[col]):
                data_col = baseline[col]
            else:
                # Try to convert to numeric
                data_col = pd.to_numeric(baseline[col], errors="coerce")

            # Merge on complete cases
            merged = pd.DataFrame(
                {"assessment": data_col, "womac": baseline[womac_total]}
            ).dropna()

            if len(merged) >= 100:  # Need sufficient data
                # Try Pearson correlation
                try:
                    corr_pearson = pearsonr(merged["assessment"], merged["womac"])
                    corr_val = corr_pearson[0]
                    corr_p = corr_pearson[1]
                except:
                    corr_val = np.nan
                    corr_p = np.nan

                # Also try Spearman for ordinal data
                try:
                    corr_spearman = spearmanr(merged["assessment"], merged["womac"])
                    corr_spearman_val = corr_spearman[0]
                except:
                    corr_spearman_val = np.nan

                correlations.append(
                    {
                        "column": col,
                        "category": row["category"],
                        "correlation_pearson": corr_val,
                        "correlation_spearman": corr_spearman_val,
                        "p_value": corr_p,
                        "n_pairs": len(merged),
                        "completeness": row["completeness_pct"],
                        "data_type": row["data_type"],
                        "unique_values": row["unique_values"],
                    }
                )
        except Exception as e:
            # Skip if can't calculate
            pass

    corr_df = pd.DataFrame(correlations)

    if len(corr_df) > 0:
        # Use absolute correlation for ranking
        corr_df["abs_correlation"] = corr_df["correlation_pearson"].abs()
        corr_df = corr_df.sort_values("abs_correlation", ascending=False)

        print("\nTOP CORRELATIONS WITH WOMAC:")
        for _, row in corr_df.head(30).iterrows():
            print(f"\n{row['column']}")
            print(f"  Category: {row['category']}")
            print(
                f"  Pearson r = {row['correlation_pearson']:.3f} (p = {row['p_value']:.4f})"
            )
            if not pd.isna(row["correlation_spearman"]):
                print(f"  Spearman ρ = {row['correlation_spearman']:.3f}")
            print(f"  N pairs: {row['n_pairs']}")
            print(f"  Completeness: {row['completeness']:.1f}%")
            print(f"  Type: {row['data_type']}, Unique: {row['unique_values']}")

        corr_df.to_csv("womac_correlations.csv", index=False)
        print("\n✓ Saved: womac_correlations.csv")
    else:
        print("⚠️  No correlations calculated")
else:
    print("⚠️  WOMAC reference column not found")

# ============================================================================
# STEP 4: Clinical Measure Alternatives
# ============================================================================
print("\n" + "=" * 80)
print("RECOMMENDED WOMAC ALTERNATIVES")
print("=" * 80)

# Criteria:
# 1. ≥95% completeness
# 2. |r| > 0.6 with WOMAC OR simple binary/ordinal that's clinically meaningful
# 3. Easy to collect in clinical practice

recommendations = []

if len(corr_df) > 0:
    # Find best candidates from correlations
    for _, row in corr_df.iterrows():
        col = row["column"]
        abs_corr = (
            abs(row["correlation_pearson"])
            if not pd.isna(row["correlation_pearson"])
            else 0
        )

        if row["completeness"] >= 95 and abs_corr >= 0.6:
            recommendations.append(
                {
                    "column": col,
                    "category": row["category"],
                    "correlation_pearson": row["correlation_pearson"],
                    "correlation_spearman": row["correlation_spearman"],
                    "completeness": row["completeness"],
                    "data_type": row["data_type"],
                    "unique_values": row["unique_values"],
                    "reason": "High correlation + completeness",
                    "priority": "HIGH" if abs_corr >= 0.7 else "MEDIUM",
                }
            )

# Also add simple binary measures that are meaningful
for a in simple_assessments:
    if a["completeness"] >= 95:
        col = a["column"]
        # Check if clinically meaningful keywords
        if any(
            word in col.upper()
            for word in ["PAIN", "WALK", "STIFF", "NIGHT", "REST", "ACTIVITY"]
        ):
            # Check if we have correlation data
            corr_row = (
                corr_df[corr_df["column"] == col]
                if len(corr_df) > 0
                else pd.DataFrame()
            )
            corr_val = (
                corr_row.iloc[0]["correlation_pearson"].item()
                if len(corr_row) > 0
                else None
            )

            recommendations.append(
                {
                    "column": col,
                    "category": "Simple Binary/Ordinal",
                    "correlation_pearson": corr_val if corr_val else "N/A (binary)",
                    "correlation_spearman": None,
                    "completeness": a["completeness"],
                    "data_type": a["type"],
                    "unique_values": len(a["values"]),
                    "reason": "Simple binary/ordinal, clinically meaningful",
                    "priority": "MEDIUM",
                }
            )

# Remove duplicates
seen = set()
unique_recommendations = []
for rec in recommendations:
    if rec["column"] not in seen:
        seen.add(rec["column"])
        unique_recommendations.append(rec)

recommendations = unique_recommendations

print(f"\n{len(recommendations)} recommended alternatives found:")

# Sort by priority and correlation
priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
recommendations_sorted = sorted(
    recommendations,
    key=lambda x: (
        priority_order.get(x.get("priority", "LOW"), 3),
        (
            -abs(x.get("correlation_pearson", 0))
            if isinstance(x.get("correlation_pearson"), (int, float))
            else 0
        ),
    ),
)

for rec in recommendations_sorted[:20]:
    print(f"\n{rec['column']}")
    print(f"  Category: {rec['category']}")
    if isinstance(rec["correlation_pearson"], (int, float)):
        print(f"  Correlation with WOMAC: r = {rec['correlation_pearson']:.3f}")
    else:
        print(f"  Correlation with WOMAC: {rec['correlation_pearson']}")
    print(f"  Completeness: {rec['completeness']:.1f}%")
    print(f"  Type: {rec['data_type']}, Unique values: {rec['unique_values']}")
    print(f"  Reason: {rec['reason']}")
    print(f"  Priority: {rec['priority']}")

# Save recommendations
if recommendations:
    rec_df = pd.DataFrame(recommendations_sorted)
    rec_df.to_csv("recommended_womac_alternatives.csv", index=False)
    print("\n✓ Saved: recommended_womac_alternatives.csv")
else:
    print("\n⚠️  No recommendations found")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
