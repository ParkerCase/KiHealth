"""
COMPREHENSIVE CANCER TYPE RANKINGS - ALL TARGETS
WITH INDIVIDUAL CELL LINE DEPENDENCY SCORES
Shows mean dependency AND individual cell line scores for each cancer type
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("COMPREHENSIVE CANCER TYPE RANKINGS - WITH INDIVIDUAL SCORES")
print("Using CRISPRGeneEffect.csv (negative = dependent)")
print("Including ALL cancers + cell line names + individual dependency scores")
print("=" * 80)

# ============================================================================
# STEP 1: Load Dependency Data
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

# ============================================================================
# STEP 2: Load Model Metadata
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: Loading model metadata...")
print("=" * 80)

model_df = pd.read_csv("data/raw/depmap/Model.csv")
model_cols = ["ModelID", "OncotreePrimaryDisease", "StrippedCellLineName"]
model_clean = model_df[model_cols].copy()

# ============================================================================
# STEP 3: Merge Dependency + Metadata
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: Merging dependency and metadata...")
print("=" * 80)

merged = dep_clean.merge(model_clean, on="ModelID", how="inner")
merged = merged[merged["OncotreePrimaryDisease"].notna()]
print(
    f"Merged data: {len(merged)} cell lines, {merged['OncotreePrimaryDisease'].nunique()} cancer types"
)

# ============================================================================
# STEP 4: Calculate Rankings with Individual Scores
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: Calculating rankings with individual cell line scores...")
print("=" * 80)

target_genes = ["STK17A", "STK17B", "MYLK4", "TBK1", "CLK4"]

for target in target_genes:
    print(f"\nProcessing {target}...")

    results = []

    for cancer in sorted(merged["OncotreePrimaryDisease"].unique()):
        cancer_data = merged[merged["OncotreePrimaryDisease"] == cancer].copy()

        if len(cancer_data) == 0:
            continue

        # Calculate statistics
        mean_dep = cancer_data[target].mean()
        n = len(cancer_data)
        std_dep = cancer_data[target].std() if n > 1 else np.nan

        # Create individual cell line scores string
        # Format: "CellLine1: score1, CellLine2: score2, ..."
        cell_line_scores = []
        for _, row in cancer_data.iterrows():
            cell_name = str(row["StrippedCellLineName"])
            score = row[target]
            cell_line_scores.append(f"{cell_name}: {score:.4f}")

        cell_scores_str = ", ".join(cell_line_scores)

        # Also create a summary showing range
        min_score = cancer_data[target].min()
        max_score = cancer_data[target].max()
        range_str = f"Range: {min_score:.4f} to {max_score:.4f}"

        # Find most dependent cell line
        most_dep_idx = cancer_data[target].idxmin()
        most_dep_cell = cancer_data.loc[most_dep_idx, "StrippedCellLineName"]
        most_dep_score = cancer_data.loc[most_dep_idx, target]

        results.append(
            {
                "Cancer": cancer,
                f"{target}_mean": round(mean_dep, 4),
                f"{target}_n": n,
                f"{target}_std": round(std_dep, 4) if not np.isnan(std_dep) else "",
                f"{target}_min": round(min_score, 4),
                f"{target}_max": round(max_score, 4),
                f"{target}_range": range_str,
                f"{target}_most_dependent_cell": f"{most_dep_cell} ({most_dep_score:.4f})",
                "Cell_Lines": ", ".join(
                    cancer_data["StrippedCellLineName"].astype(str).tolist()
                ),
                "Individual_Scores": cell_scores_str,
            }
        )

    # Create DataFrame
    results_df = pd.DataFrame(results)

    # Sort by mean dependency (most negative = highest dependency = rank 1)
    results_df = results_df.sort_values(f"{target}_mean").reset_index(drop=True)
    results_df["Rank"] = range(1, len(results_df) + 1)

    # Reorder columns
    cols = [
        "Rank",
        "Cancer",
        f"{target}_mean",
        f"{target}_n",
        f"{target}_std",
        f"{target}_min",
        f"{target}_max",
        f"{target}_range",
        f"{target}_most_dependent_cell",
        "Cell_Lines",
        "Individual_Scores",
    ]
    results_df = results_df[cols]

    # Save
    output_file = f"outputs/reports/{target}_COMPLETE_RANKINGS_WITH_SCORES.csv"
    results_df.to_csv(output_file, index=False)

    print(f"  ✅ Saved: {output_file}")
    print(f"  Total cancer types: {len(results_df)}")
    print(
        f"  Most dependent (rank 1): {results_df.iloc[0]['Cancer']} ({results_df.iloc[0][f'{target}_mean']:.4f}, n={results_df.iloc[0][f'{target}_n']})"
    )

    # Show example with individual scores
    print(f"\n  Example - {results_df.iloc[0]['Cancer']}:")
    print(f"    Mean: {results_df.iloc[0][f'{target}_mean']:.4f}")
    print(f"    Range: {results_df.iloc[0][f'{target}_range']}")
    print(f"    Most dependent: {results_df.iloc[0][f'{target}_most_dependent_cell']}")
    if results_df.iloc[0][f"{target}_n"] <= 5:  # Show all if 5 or fewer
        print(f"    Individual scores: {results_df.iloc[0]['Individual_Scores']}")

# ============================================================================
# STEP 5: Create Combined Summary with Individual Scores
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: Creating combined summary with individual scores...")
print("=" * 80)

summary_data = []
for cancer in sorted(merged["OncotreePrimaryDisease"].unique()):
    cancer_data = merged[merged["OncotreePrimaryDisease"] == cancer].copy()

    row = {"Cancer": cancer, "n_cell_lines": len(cancer_data)}

    # Add mean dependency and individual scores for each target
    for target in target_genes:
        mean_dep = cancer_data[target].mean()
        row[f"{target}_mean"] = round(mean_dep, 4)

        # Individual scores for this target
        cell_scores = []
        for _, r in cancer_data.iterrows():
            cell_name = str(r["StrippedCellLineName"])
            score = r[target]
            cell_scores.append(f"{cell_name}: {score:.4f}")
        row[f"{target}_individual_scores"] = ", ".join(cell_scores)

        # Range info
        row[f"{target}_min"] = round(cancer_data[target].min(), 4)
        row[f"{target}_max"] = round(cancer_data[target].max(), 4)
        row[f"{target}_most_dependent"] = (
            f"{cancer_data.loc[cancer_data[target].idxmin(), 'StrippedCellLineName']} ({cancer_data[target].min():.4f})"
        )

    # Combined score
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
    + [f"{target}_min" for target in target_genes]
    + [f"{target}_max" for target in target_genes]
    + [f"{target}_most_dependent" for target in target_genes]
    + ["Cell_Lines"]
    + [f"{target}_individual_scores" for target in target_genes]
)
summary_df = summary_df[cols]

# Save
summary_file = "outputs/reports/ALL_TARGETS_COMPLETE_RANKINGS_WITH_SCORES.csv"
summary_df.to_csv(summary_file, index=False)

print(f"✅ Saved combined summary: {summary_file}")
print(f"Total cancer types: {len(summary_df)}")

# Show example
print("\n" + "=" * 80)
print("EXAMPLE: Non-Hodgkin Lymphoma (showing individual scores)")
print("=" * 80)
nhl = summary_df[summary_df["Cancer"] == "Non-Hodgkin Lymphoma"]
if len(nhl) > 0:
    nhl_row = nhl.iloc[0]
    print(f"\nCancer: {nhl_row['Cancer']}")
    print(f"Mean STK17A dependency: {nhl_row['STK17A_mean']:.4f}")
    print(f"Range: {nhl_row['STK17A_min']:.4f} to {nhl_row['STK17A_max']:.4f}")
    print(f"Most dependent cell line: {nhl_row['STK17A_most_dependent']}")
    print(f"\nIndividual STK17A scores:")
    scores = nhl_row["STK17A_individual_scores"].split(", ")
    for score in scores:
        cell, val = score.split(": ")
        if float(val) < -0.2:  # Highlight highly dependent
            print(f"  ⭐ {cell}: {val} (HIGHLY DEPENDENT)")
        else:
            print(f"    {cell}: {val}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nFiles created:")
print(f"  1. outputs/reports/STK17A_COMPLETE_RANKINGS_WITH_SCORES.csv")
print(f"  2. outputs/reports/STK17B_COMPLETE_RANKINGS_WITH_SCORES.csv")
print(f"  3. outputs/reports/MYLK4_COMPLETE_RANKINGS_WITH_SCORES.csv")
print(f"  4. outputs/reports/TBK1_COMPLETE_RANKINGS_WITH_SCORES.csv")
print(f"  5. outputs/reports/CLK4_COMPLETE_RANKINGS_WITH_SCORES.csv")
print(f"  6. outputs/reports/ALL_TARGETS_COMPLETE_RANKINGS_WITH_SCORES.csv")
