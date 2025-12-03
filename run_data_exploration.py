#!/usr/bin/env python3
"""
Run all cells from the data exploration notebook
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Set display options for better readability
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_rows", 10)
pd.set_option("display.width", 120)

print("=" * 80)
print("OAI Dataset Exploration")
print("=" * 80)

# ============================================================================
# 1. Load Enrollees Data
# ============================================================================
print("\n" + "=" * 80)
print("1. Loading Enrollees Data")
print("=" * 80)

enrollees_path = "data/raw/General_ASCII/Enrollees.txt"
enrollees = pd.read_csv(enrollees_path, sep="|", low_memory=False)

print("✅ Enrollees file loaded successfully!")
print(f"\nShape: {enrollees.shape}")
print(f"Total patients: {len(enrollees)}")
print(f"Total columns: {len(enrollees.columns)}")
print(f"\nFirst 10 columns: {enrollees.columns.tolist()[:10]}")
print(f"\nData types:\n{enrollees.dtypes.value_counts()}")
print(f"\nMissing values per column (top 10):")
print(enrollees.isnull().sum().sort_values(ascending=False).head(10))

print("\nFirst 5 rows of Enrollees data:")
print(enrollees.head())

# ============================================================================
# 2. Load Outcomes99 Data
# ============================================================================
print("\n" + "=" * 80)
print("2. Loading Outcomes99 Data")
print("=" * 80)

outcomes_path = "data/raw/General_ASCII/Outcomes99.txt"
outcomes = pd.read_csv(outcomes_path, sep="|", low_memory=False)

print("✅ Outcomes99 file loaded successfully!")
print(f"\nShape: {outcomes.shape}")
print(f"Total rows: {len(outcomes)}")
print(f"Total columns: {len(outcomes.columns)}")
print(f"\nFirst 10 columns: {outcomes.columns.tolist()[:10]}")
print(f"\nData types:\n{outcomes.dtypes.value_counts()}")
print(f"\nMissing values per column (top 10):")
print(outcomes.isnull().sum().sort_values(ascending=False).head(10))

print("\nFirst 5 rows of Outcomes99 data:")
print(outcomes.head())

# ============================================================================
# 3. Load SubjectChar00 Data
# ============================================================================
print("\n" + "=" * 80)
print("3. Loading SubjectChar00 Data")
print("=" * 80)

subjectchar_path = "data/raw/General_ASCII/SubjectChar00.txt"
subjectchar = pd.read_csv(subjectchar_path, sep="|", low_memory=False)

print("✅ SubjectChar00 file loaded successfully!")
print(f"\nShape: {subjectchar.shape}")
print(f"Total rows: {len(subjectchar)}")
print(f"Total columns: {len(subjectchar.columns)}")
print(f"\nFirst 10 columns: {subjectchar.columns.tolist()[:10]}")
print(f"\nData types:\n{subjectchar.dtypes.value_counts()}")
print(f"\nMissing values per column (top 10):")
print(subjectchar.isnull().sum().sort_values(ascending=False).head(10))

print("\nFirst 5 rows of SubjectChar00 data:")
print(subjectchar.head())

# ============================================================================
# 4. Load X-Ray Alignment Data
# ============================================================================
print("\n" + "=" * 80)
print("4. Loading X-Ray Alignment Data")
print("=" * 80)

xray_path = (
    "data/raw/X-Ray Image Assessments_ASCII/Alignment_ASCII/flxr_kneealign_cooke01.txt"
)
xray_align = pd.read_csv(xray_path, sep="|", low_memory=False)

print("✅ X-ray alignment file loaded successfully!")
print(f"\nShape: {xray_align.shape}")
print(f"Total rows: {len(xray_align)}")
print(f"Total columns: {len(xray_align.columns)}")
print(f"\nFirst 10 columns: {xray_align.columns.tolist()[:10]}")
print(f"\nData types:\n{xray_align.dtypes.value_counts()}")
print(f"\nMissing values per column (top 10):")
print(xray_align.isnull().sum().sort_values(ascending=False).head(10))

print("\nFirst 5 rows of X-ray alignment data:")
print(xray_align.head())

# ============================================================================
# 5. Data Quality Checks
# ============================================================================
print("\n" + "=" * 80)
print("5. Data Quality Checks")
print("=" * 80)

# 5.1 Check for Common Patient ID Column
print("\n5.1 Checking for Common Patient ID Column")
print("-" * 80)

print("ID columns in each dataset:")
print(f"\nEnrollees: {[col for col in enrollees.columns if 'ID' in col.upper()]}")
print(f"Outcomes99: {[col for col in outcomes.columns if 'ID' in col.upper()]}")
print(f"SubjectChar00: {[col for col in subjectchar.columns if 'ID' in col.upper()]}")
print(f"X-ray Alignment: {[col for col in xray_align.columns if 'ID' in col.upper()]}")

# Check overlap of patient IDs
if "ID" in enrollees.columns:
    enrollees_ids = set(enrollees["ID"].dropna())
    print(f"\n✅ Enrollees has {len(enrollees_ids)} unique patient IDs")

    if "ID" in outcomes.columns:
        outcomes_ids = set(outcomes["ID"].dropna())
        overlap = enrollees_ids.intersection(outcomes_ids)
        print(f"✅ Outcomes99 has {len(outcomes_ids)} unique patient IDs")
        print(
            f"✅ Overlap: {len(overlap)} patients ({len(overlap)/len(enrollees_ids)*100:.1f}%)"
        )

    if "ID" in subjectchar.columns:
        subjectchar_ids = set(subjectchar["ID"].dropna())
        overlap = enrollees_ids.intersection(subjectchar_ids)
        print(f"✅ SubjectChar00 has {len(subjectchar_ids)} unique patient IDs")
        print(
            f"✅ Overlap: {len(overlap)} patients ({len(overlap)/len(enrollees_ids)*100:.1f}%)"
        )

    if "ID" in xray_align.columns:
        xray_ids = set(xray_align["ID"].dropna())
        overlap = enrollees_ids.intersection(xray_ids)
        print(f"✅ X-ray Alignment has {len(xray_ids)} unique patient IDs")
        print(
            f"✅ Overlap: {len(overlap)} patients ({len(overlap)/len(enrollees_ids)*100:.1f}%)"
        )

# 5.2 Summary Statistics
print("\n5.2 Summary Statistics")
print("-" * 80)

summary = pd.DataFrame(
    {
        "Dataset": ["Enrollees", "Outcomes99", "SubjectChar00", "X-ray Alignment"],
        "Rows": [len(enrollees), len(outcomes), len(subjectchar), len(xray_align)],
        "Columns": [
            len(enrollees.columns),
            len(outcomes.columns),
            len(subjectchar.columns),
            len(xray_align.columns),
        ],
        "Memory (MB)": [
            enrollees.memory_usage(deep=True).sum() / 1024**2,
            outcomes.memory_usage(deep=True).sum() / 1024**2,
            subjectchar.memory_usage(deep=True).sum() / 1024**2,
            xray_align.memory_usage(deep=True).sum() / 1024**2,
        ],
    }
)

print(" Dataset Summary:")
print(summary.to_string(index=False))

# 5.3 Check for Data Quality Issues
print("\n5.3 Data Quality Issues")
print("-" * 80)

datasets = {
    "Enrollees": enrollees,
    "Outcomes99": outcomes,
    "SubjectChar00": subjectchar,
    "X-ray Alignment": xray_align,
}

for name, df in datasets.items():
    print(f"\n{name}:")
    print(f"  - Duplicate rows: {df.duplicated().sum()}")
    print(f"  - Columns with >50% missing: {(df.isnull().sum() / len(df) > 0.5).sum()}")
    print(f"  - Columns with all missing: {df.isnull().all().sum()}")

    # Check for potential encoding issues (non-ASCII characters)
    text_cols = df.select_dtypes(include=["object"]).columns
    if len(text_cols) > 0:
        sample_col = text_cols[0]
        try:
            df[sample_col].astype(str).str.encode("ascii")
            print(f"  - Encoding: ✅ ASCII compatible")
        except:
            print(f"  - Encoding: ⚠️ Non-ASCII characters detected")

print("\n" + "=" * 80)
print("✅ Exploration Complete!")
print("=" * 80)
