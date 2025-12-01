"""
COMPREHENSIVE CANCER TYPE RANKINGS - ALL TARGETS
Recalculates rankings using CRISPRGeneEffect.csv (correct file)
Includes ALL cancers with dependency data + cell line names
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("COMPREHENSIVE CANCER TYPE RANKINGS - ALL TARGETS")
print("Using CRISPRGeneEffect.csv (negative = dependent)")
print("Including ALL cancers with dependency data + cell line names")
print("=" * 80)

# ============================================================================
# STEP 1: Load Dependency Data (GeneEffect, not GeneDependency!)
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: Loading dependency data (CRISPRGeneEffect.csv)...")
print("=" * 80)

dep_df = pd.read_csv("data/raw/depmap/CRISPRGeneEffect.csv", index_col=0)
dep_df = dep_df.reset_index()
dep_df.columns.values[0] = "ModelID"
print(f"Total cell lines in dependency data: {len(dep_df)}")

# Get target gene columns
targets = {
    "STK17A": [
        col for col in dep_df.columns if "STK17A" in col and "STK17B" not in col
    ][0],
    "STK17B": [col for col in dep_df.columns if "STK17B" in col][0],
    "MYLK4": [col for col in dep_df.columns if "MYLK4" in col][0],
    "TBK1": [col for col in dep_df.columns if "TBK1" in col][0],
    "CLK4": [col for col in dep_df.columns if "CLK4" in col][0],
}

print("\nTarget gene columns found:")
for gene, col in targets.items():
    print(f"  {gene}: {col}")

# Create clean dependency dataframe
dep_clean = dep_df[["ModelID"] + list(targets.values())].copy()
dep_clean.columns = ["ModelID", "STK17A", "STK17B", "MYLK4", "TBK1", "CLK4"]

print(f"\nDependency data shape: {dep_clean.shape}")

# Verify we have negative values (dependent cells)
for gene in ["STK17A", "STK17B", "MYLK4", "TBK1", "CLK4"]:
    min_val = dep_clean[gene].min()
    max_val = dep_clean[gene].max()
    neg_count = (dep_clean[gene] < 0).sum()
    print(
        f"  {gene}: min={min_val:.4f}, max={max_val:.4f}, negative values={neg_count}"
    )

# ============================================================================
# STEP 2: Load Model Metadata
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: Loading model metadata...")
print("=" * 80)

model_df = pd.read_csv("data/raw/depmap/Model.csv")
print(f"Total cell lines in Model.csv: {len(model_df)}")

# Get relevant columns
model_cols = ["ModelID", "OncotreePrimaryDisease", "StrippedCellLineName"]
model_clean = model_df[model_cols].copy()
print(f"Model metadata shape: {model_clean.shape}")

# ============================================================================
# STEP 3: Merge Dependency + Metadata
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: Merging dependency and metadata...")
print("=" * 80)

merged = dep_clean.merge(model_clean, on="ModelID", how="inner")
print(f"Merged data shape: {merged.shape}")
print(f"Cell lines with both dependency and metadata: {len(merged)}")

# Check for missing cancer types
missing_cancer = merged["OncotreePrimaryDisease"].isna().sum()
if missing_cancer > 0:
    print(f"⚠️  Warning: {missing_cancer} cell lines missing cancer type")
    merged = merged[merged["OncotreePrimaryDisease"].notna()]

print(f"Final merged data: {len(merged)} cell lines")
print(f"Unique cancer types: {merged['OncotreePrimaryDisease'].nunique()}")

# ============================================================================
# STEP 4: Calculate Rankings for Each Target
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: Calculating rankings for each target...")
print("=" * 80)

target_genes = ["STK17A", "STK17B", "MYLK4", "TBK1", "CLK4"]

for target in target_genes:
    print(f"\nProcessing {target}...")

    # Group by cancer type
    cancer_groups = (
        merged.groupby("OncotreePrimaryDisease")
        .agg(
            {
                target: ["mean", "count", "std"],
                "StrippedCellLineName": lambda x: ", ".join(x.astype(str)),
            }
        )
        .reset_index()
    )

    # Flatten column names
    cancer_groups.columns = [
        "Cancer",
        f"{target}_mean",
        f"{target}_n",
        f"{target}_std",
        "Cell_Lines",
    ]

    # Fill NaN std with empty string (for n=1 cases)
    cancer_groups[f"{target}_std"] = cancer_groups[f"{target}_std"].fillna("")

    # Sort by dependency (most negative = highest dependency = rank 1)
    cancer_groups = cancer_groups.sort_values(f"{target}_mean").reset_index(drop=True)
    cancer_groups["Rank"] = range(1, len(cancer_groups) + 1)

    # Reorder columns
    cancer_groups = cancer_groups[
        [
            "Rank",
            "Cancer",
            f"{target}_mean",
            f"{target}_n",
            f"{target}_std",
            "Cell_Lines",
        ]
    ]

    # Round mean to 4 decimals
    cancer_groups[f"{target}_mean"] = cancer_groups[f"{target}_mean"].round(4)
    cancer_groups[f"{target}_n"] = cancer_groups[f"{target}_n"].astype(int)

    # Save
    output_file = f"outputs/reports/{target}_COMPLETE_RANKINGS.csv"
    cancer_groups.to_csv(output_file, index=False)

    print(f"  ✅ Saved: {output_file}")
    print(f"  Total cancer types: {len(cancer_groups)}")
    print(
        f"  Most dependent (rank 1): {cancer_groups.iloc[0]['Cancer']} ({cancer_groups.iloc[0][f'{target}_mean']:.4f}, n={cancer_groups.iloc[0][f'{target}_n']})"
    )
    print(
        f"  Least dependent (rank {len(cancer_groups)}): {cancer_groups.iloc[-1]['Cancer']} ({cancer_groups.iloc[-1][f'{target}_mean']:.4f}, n={cancer_groups.iloc[-1][f'{target}_n']})"
    )
    print(f"  Top 3:")
    for idx, row in cancer_groups.head(3).iterrows():
        print(
            f"    {row['Rank']}. {row['Cancer']}: {row[f'{target}_mean']:.4f} (n={row[f'{target}_n']})"
        )

# ============================================================================
# STEP 5: Create Combined Summary
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: Creating combined summary...")
print("=" * 80)

# Get all unique cancers
all_cancers = merged["OncotreePrimaryDisease"].unique()
print(f"Total unique cancer types: {len(all_cancers)}")

# Create summary for each cancer type
summary_data = []
for cancer in sorted(all_cancers):
    cancer_data = merged[merged["OncotreePrimaryDisease"] == cancer]

    row = {"Cancer": cancer, "n_cell_lines": len(cancer_data)}

    # Add mean dependency for each target
    for target in target_genes:
        mean_dep = cancer_data[target].mean()
        row[f"{target}_mean"] = round(mean_dep, 4)

    # Combined score (mean of all 5 targets)
    target_means = [row[f"{target}_mean"] for target in target_genes]
    row["Combined_Score"] = round(np.mean(target_means), 4)

    # Cell line names
    row["Cell_Lines"] = ", ".join(
        cancer_data["StrippedCellLineName"].astype(str).tolist()
    )

    summary_data.append(row)

summary_df = pd.DataFrame(summary_data)
summary_df = summary_df.sort_values("Combined_Score").reset_index(drop=True)
summary_df["Rank"] = range(1, len(summary_df) + 1)

# Reorder columns
cols = (
    ["Rank", "Cancer", "n_cell_lines", "Combined_Score"]
    + [f"{target}_mean" for target in target_genes]
    + ["Cell_Lines"]
)
summary_df = summary_df[cols]

# Save combined summary
summary_file = "outputs/reports/ALL_TARGETS_COMPLETE_RANKINGS.csv"
summary_df.to_csv(summary_file, index=False)

print(f"✅ Saved combined summary: {summary_file}")
print(f"Total cancer types included: {len(summary_df)}")

# ============================================================================
# STEP 6: Verification
# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: Verification")
print("=" * 80)

# Check that all targets have data
for target in target_genes:
    missing = merged[target].isna().sum()
    print(f"{target}: {missing} missing values out of {len(merged)} cell lines")

# Check cancer type counts
print(f"\nCancer type counts:")
print(f"  In merged data: {merged['OncotreePrimaryDisease'].nunique()}")
print(f"  In summary: {summary_df['Cancer'].nunique()}")

# Show sample of data
print("\n" + "=" * 80)
print("SAMPLE: Top 5 cancers by combined score (most dependent)")
print("=" * 80)
display_cols = ["Rank", "Cancer", "n_cell_lines", "Combined_Score"] + [
    f"{target}_mean" for target in target_genes
]
print(summary_df[display_cols].head(5).to_string(index=False))

# Compare with original rankings
print("\n" + "=" * 80)
print("COMPARISON WITH ORIGINAL RANKINGS")
print("=" * 80)
try:
    original = pd.read_csv("data/processed/cancer_type_rankings.csv")
    print(f"Original rankings: {len(original)} cancer types")
    print(f"New rankings: {len(summary_df)} cancer types")
    print(f"Additional cancer types: {len(summary_df) - len(original)}")

    # Check if top cancers match
    print("\nTop 5 STK17A in original vs new:")
    orig_stk17a = original.sort_values("STK17A_dependency_mean").head(5)
    new_stk17a = summary_df.sort_values("STK17A_mean").head(5)
    print("\nOriginal:")
    print(
        orig_stk17a[["OncotreePrimaryDisease", "STK17A_dependency_mean"]].to_string(
            index=False
        )
    )
    print("\nNew:")
    print(new_stk17a[["Cancer", "STK17A_mean"]].to_string(index=False))
except Exception as e:
    print(f"Could not compare: {e}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nFiles created:")
print(f"  1. outputs/reports/STK17A_COMPLETE_RANKINGS.csv")
print(f"  2. outputs/reports/STK17B_COMPLETE_RANKINGS.csv")
print(f"  3. outputs/reports/MYLK4_COMPLETE_RANKINGS.csv")
print(f"  4. outputs/reports/TBK1_COMPLETE_RANKINGS.csv")
print(f"  5. outputs/reports/CLK4_COMPLETE_RANKINGS.csv")
print(f"  6. outputs/reports/ALL_TARGETS_COMPLETE_RANKINGS.csv (combined)")
