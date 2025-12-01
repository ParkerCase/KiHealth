#!/usr/bin/env python3
"""
Add Mutation Flags to Cancer Rankings
=====================================
This script adds boolean mutation flags to the cancer_rankings CSV
to enable queries like "Show me cancers with NRAS mutations and high TBK1 dependency"

Usage:
    python add_mutation_flags_to_rankings.py
"""

import pandas as pd
import os
from pathlib import Path

print("=" * 80)
print("Adding Mutation Flags to Cancer Rankings")
print("=" * 80)

# File paths
base_dir = Path(__file__).parent
mutation_file = base_dir / "data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv"
model_file = base_dir / "data/raw/depmap/Model.csv"
rankings_file = (
    base_dir / "data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED.csv"
)
output_file = (
    base_dir
    / "data/processed/FINAL_COMPREHENSIVE_RANKINGS_94_PERCENT_INTEGRATED_WITH_MUTATIONS.csv"
)

# Common mutations to track (based on synthetic lethality analysis and common cancer mutations)
COMMON_MUTATIONS = [
    "NRAS",
    "KRAS",
    "BRAF",
    "TP53",
    "PIK3CA",
    "PTEN",
    "EGFR",
    "APC",
    "SMAD4",
    "CDKN2A",
    "RB1",
    "NF1",
    "ARID1A",
    "CTNNB1",
    "IDH1",
    "IDH2",
    "FLT3",
    "NPM1",
    "DNMT3A",
    "TET2",
    "ASXL1",
]

print(f"\n1. Loading mutation data from: {mutation_file.name}")
print(f"   Loading model metadata from: {model_file.name}")
print(f"   Loading rankings from: {rankings_file.name}")

# Load mutation matrix (hotspot mutations)
print("\n   Reading mutation matrix (this may take a moment)...")
mutations_df = pd.read_csv(mutation_file, low_memory=False)

# Load model metadata to map ModelID to cancer type
print("   Reading model metadata...")
models_df = pd.read_csv(model_file, low_memory=False)

# Load current rankings
print("   Reading cancer rankings...")
rankings_df = pd.read_csv(rankings_file)

print(f"\n   ✓ Loaded {len(mutations_df)} mutation records")
print(f"   ✓ Loaded {len(models_df)} model records")
print(f"   ✓ Loaded {len(rankings_df)} cancer rankings")

# Get mutation columns that exist in the mutation matrix
print(f"\n2. Identifying mutation columns in mutation matrix...")
mutation_cols = [
    col for col in mutations_df.columns if any(mut in col for mut in COMMON_MUTATIONS)
]
print(f"   Found {len(mutation_cols)} mutation columns")

# Map ModelID to cancer type (OncotreePrimaryDisease)
print("\n3. Mapping ModelID to cancer type...")
model_to_cancer = dict(zip(models_df["ModelID"], models_df["OncotreePrimaryDisease"]))
print(f"   ✓ Mapped {len(model_to_cancer)} models to cancer types")

# Add cancer type to mutation data
mutations_df["cancer_type"] = mutations_df["ModelID"].map(model_to_cancer)

# Filter to only models with cancer type mapping
mutations_df = mutations_df[mutations_df["cancer_type"].notna()]

print(f"   ✓ {len(mutations_df)} mutation records have cancer type mapping")

# Aggregate mutations by cancer type
print(f"\n4. Aggregating mutations by cancer type...")
print(f"   Checking for: {', '.join(COMMON_MUTATIONS)}")

# Create a dictionary to store mutation flags per cancer type
cancer_mutations = {}

for cancer_type in rankings_df["cancer_type"].unique():
    # Get all cell lines for this cancer type
    cancer_mut_data = mutations_df[mutations_df["cancer_type"] == cancer_type]

    if len(cancer_mut_data) == 0:
        # No mutation data for this cancer type
        cancer_mutations[cancer_type] = {mut: False for mut in COMMON_MUTATIONS}
        continue

    # Check each mutation
    mutation_flags = {}
    for mutation in COMMON_MUTATIONS:
        # Find columns that contain this mutation name
        mut_cols = [col for col in mutation_cols if mutation in col]

        if not mut_cols:
            mutation_flags[mutation] = False
            continue

        # Check if any cell line in this cancer type has this mutation
        # Mutation value > 0 means mutation is present
        has_mutation = False
        for col in mut_cols:
            if col in cancer_mut_data.columns:
                # Check if any cell line has mutation (value > 0)
                if (cancer_mut_data[col] > 0).any():
                    has_mutation = True
                    break

        mutation_flags[mutation] = has_mutation

    cancer_mutations[cancer_type] = mutation_flags

print(f"   ✓ Processed {len(cancer_mutations)} cancer types")

# Add mutation flags to rankings
print(f"\n5. Adding mutation flags to rankings...")
for mutation in COMMON_MUTATIONS:
    col_name = f"has_{mutation}"
    rankings_df[col_name] = rankings_df["cancer_type"].map(
        lambda ct: cancer_mutations.get(ct, {}).get(mutation, False)
    )
    # Count how many cancers have this mutation
    count = rankings_df[col_name].sum()
    print(f"   ✓ {mutation}: {count} cancer types have this mutation")

# Reorder columns: put mutation flags after cancer_type but before scores
print(f"\n6. Reordering columns...")
base_cols = ["Rank", "cancer_type", "n_cell_lines", "overall_score", "confidence_tier"]
mutation_cols = [f"has_{mut}" for mut in COMMON_MUTATIONS]
other_cols = [
    col for col in rankings_df.columns if col not in base_cols + mutation_cols
]

new_column_order = base_cols + mutation_cols + other_cols
rankings_df = rankings_df[new_column_order]

# Save updated rankings
print(f"\n7. Saving updated rankings...")
rankings_df.to_csv(output_file, index=False)
print(f"   ✓ Saved to: {output_file.name}")
print(f"   ✓ Total columns: {len(rankings_df.columns)}")
print(f"   ✓ Total rows: {len(rankings_df)}")

# Summary statistics
print(f"\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\nMutation flags added for {len(COMMON_MUTATIONS)} mutations:")
for mutation in COMMON_MUTATIONS:
    count = rankings_df[f"has_{mutation}"].sum()
    percentage = (count / len(rankings_df)) * 100
    print(f"  - {mutation}: {count} cancers ({percentage:.1f}%)")

print(f"\n✅ Successfully created: {output_file.name}")
print(f"\nNext steps:")
print(f"  1. Review the new CSV file")
print(f"  2. Import into Xata as an update to cancer_rankings table")
print(f"  3. Update semantic search to handle mutation queries")
