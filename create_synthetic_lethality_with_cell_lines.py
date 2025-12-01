"""
SYNTHETIC LETHALITY WITH INDIVIDUAL CELL LINE SCORES
Shows which specific cell lines drive each synthetic lethality hit
"""

import pandas as pd
import numpy as np
from scipy import stats

print("=" * 80)
print("SYNTHETIC LETHALITY WITH INDIVIDUAL CELL LINE SCORES")
print("Including all mutations, all targets, and individual cell line data")
print("=" * 80)

# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: Loading data...")
print("=" * 80)

# Dependency data
dep_df = pd.read_csv("data/raw/depmap/CRISPRGeneEffect.csv", index_col=0)
dep_df = dep_df.reset_index()
dep_df.columns.values[0] = "ModelID"

# Get target gene columns
targets = {
    "STK17A": [
        col for col in dep_df.columns if "STK17A" in col and "STK17B" not in col
    ][0],
    "MYLK4": [col for col in dep_df.columns if "MYLK4" in col][0],
    "TBK1": [col for col in dep_df.columns if "TBK1" in col][0],
    "CLK4": [col for col in dep_df.columns if "CLK4" in col][0],
}

dep_clean = dep_df[["ModelID"] + list(targets.values())].copy()
dep_clean.columns = ["ModelID", "STK17A", "MYLK4", "TBK1", "CLK4"]

# Mutation data
mutations_hotspot = pd.read_csv(
    "data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv"
)
if "ModelID" in mutations_hotspot.columns:
    mutations_hotspot = mutations_hotspot.set_index("ModelID")
else:
    mutations_hotspot = mutations_hotspot.reset_index()
    if "ModelID" in mutations_hotspot.columns:
        mutations_hotspot = mutations_hotspot.set_index("ModelID")

# Model metadata
model_df = pd.read_csv("data/raw/depmap/Model.csv")

# Merge all
merged = dep_clean.merge(
    model_df[["ModelID", "OncotreePrimaryDisease", "StrippedCellLineName"]],
    on="ModelID",
    how="inner",
)
merged = merged[merged["OncotreePrimaryDisease"].notna()]

# Get mutation columns
metadata_cols = [
    "SequencingID",
    "ModelConditionID",
    "IsDefaultEntryForModel",
    "IsDefaultEntryForMC",
]
mutation_cols = [
    col
    for col in mutations_hotspot.columns
    if col not in metadata_cols and "Unnamed" not in col
]

print(f"Dependency data: {len(dep_clean)} cell lines")
print(f"Mutation data: {len(mutations_hotspot)} cell lines")
print(f"Available mutations: {len(mutation_cols)}")
print(f"Merged data: {len(merged)} cell lines")

# ============================================================================
# STEP 2: Find Testable Mutations
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: Identifying testable mutations...")
print("=" * 80)

MIN_MUTANTS = 3
MIN_WT = 10

testable_mutations = []
for mut_col in mutation_cols:
    if mut_col in mutations_hotspot.columns:
        mut_status = mutations_hotspot[mut_col].fillna(0)
        n_mutant = (mut_status == 1).sum()
        n_wt = (mut_status == 0).sum()

        if n_mutant >= MIN_MUTANTS and n_wt >= MIN_WT:
            gene_name = mut_col.split()[0] if " " in mut_col else mut_col
            testable_mutations.append(
                {
                    "gene": gene_name,
                    "column": mut_col,
                    "n_mutant": n_mutant,
                    "n_wt": n_wt,
                }
            )

print(f"Testable mutations: {len(testable_mutations)}")

# ============================================================================
# STEP 3: Run Analysis with Individual Cell Line Scores
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: Running synthetic lethality analysis with cell line details...")
print("=" * 80)

results = []
target_genes = ["STK17A", "MYLK4", "TBK1", "CLK4"]

# Merge mutation data
mut_common = mutations_hotspot.loc[
    mutations_hotspot.index.isin(merged["ModelID"])
].copy()

merged_with_mut = merged.merge(
    mut_common.reset_index()[["ModelID"] + [m["column"] for m in testable_mutations]],
    on="ModelID",
    how="inner",
)

print(f"Cell lines with both dependency and mutation data: {len(merged_with_mut)}")

total_combos = len(testable_mutations) * len(target_genes)
processed = 0

for mut_info in testable_mutations:
    mut_gene = mut_info["gene"]
    mut_col = mut_info["column"]

    for target_gene in target_genes:
        processed += 1
        if processed % 100 == 0:
            print(
                f"  Progress: {processed}/{total_combos} ({processed/total_combos*100:.1f}%)"
            )

        # Split into mutant and wild-type
        mutant_data = merged_with_mut[merged_with_mut[mut_col] == 1][
            ["ModelID", target_gene, "StrippedCellLineName", "OncotreePrimaryDisease"]
        ].dropna(subset=[target_gene])

        wt_data = merged_with_mut[merged_with_mut[mut_col] == 0][
            ["ModelID", target_gene, "StrippedCellLineName", "OncotreePrimaryDisease"]
        ].dropna(subset=[target_gene])

        if len(mutant_data) < MIN_MUTANTS or len(wt_data) < MIN_WT:
            continue

        # Calculate statistics
        mutant_mean = mutant_data[target_gene].mean()
        wt_mean = wt_data[target_gene].mean()
        mean_diff = mutant_mean - wt_mean

        # Statistical test
        try:
            t_stat, p_val = stats.ttest_ind(
                mutant_data[target_gene], wt_data[target_gene], equal_var=False
            )
        except:
            continue

        # Individual cell line scores for mutants
        mutant_scores = []
        for _, row in mutant_data.iterrows():
            cell_name = str(row["StrippedCellLineName"])
            score = row[target_gene]
            cancer = str(row["OncotreePrimaryDisease"])
            mutant_scores.append(f"{cell_name} ({cancer}): {score:.4f}")

        # Individual cell line scores for WT
        wt_scores = []
        for _, row in wt_data.iterrows():
            cell_name = str(row["StrippedCellLineName"])
            score = row[target_gene]
            cancer = str(row["OncotreePrimaryDisease"])
            wt_scores.append(f"{cell_name} ({cancer}): {score:.4f}")

        # Find most dependent mutant cell line
        most_dep_idx = mutant_data[target_gene].idxmin()
        most_dep_cell = mutant_data.loc[most_dep_idx, "StrippedCellLineName"]
        most_dep_score = mutant_data.loc[most_dep_idx, target_gene]
        most_dep_cancer = mutant_data.loc[most_dep_idx, "OncotreePrimaryDisease"]

        # Store result
        results.append(
            {
                "mutation": mut_gene,
                "mutation_column": mut_col,
                "target": target_gene,
                "n_mutant": len(mutant_data),
                "n_wt": len(wt_data),
                "mutant_mean": round(mutant_mean, 4),
                "wt_mean": round(wt_mean, 4),
                "mean_diff": round(mean_diff, 4),
                "p_value": p_val,
                "is_synthetic_lethal": mean_diff < 0,
                "most_dependent_mutant_cell": f"{most_dep_cell} ({most_dep_cancer}): {most_dep_score:.4f}",
                "mutant_cell_lines": ", ".join(
                    mutant_data["StrippedCellLineName"].astype(str).tolist()
                ),
                "mutant_individual_scores": ", ".join(mutant_scores),
                "wt_cell_lines": ", ".join(
                    wt_data["StrippedCellLineName"].astype(str).tolist()[:20]
                )
                + ("..." if len(wt_data) > 20 else ""),  # Limit WT for readability
                "wt_individual_scores": ", ".join(wt_scores[:10])
                + ("..." if len(wt_scores) > 10 else ""),  # Limit WT scores
            }
        )

results_df = pd.DataFrame(results)
print(f"\nTotal combinations tested: {len(results_df)}")

# ============================================================================
# STEP 4: Filter for True Synthetic Lethality
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: Filtering for true synthetic lethality...")
print("=" * 80)

# True SL: negative mean_diff (mutants more dependent) AND significant
true_sl = results_df[
    (results_df["mean_diff"] < 0) & (results_df["p_value"] < 0.10)
].copy()

true_sl = true_sl.sort_values("mean_diff").reset_index(drop=True)
true_sl["Rank"] = range(1, len(true_sl) + 1)

print(f"True synthetic lethality hits: {len(true_sl)}")

# Save complete results
complete_file = "data/processed/synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv"
results_df.to_csv(complete_file, index=False)
print(f"✅ Saved complete results: {complete_file}")

# Save true SL hits
sl_file = "data/processed/true_synthetic_lethality_WITH_CELL_LINES.csv"
true_sl.to_csv(sl_file, index=False)
print(f"✅ Saved true SL hits: {sl_file}")

# Show example
print("\n" + "=" * 80)
print("EXAMPLE: Top 3 Synthetic Lethality Hits")
print("=" * 80)
for idx, row in true_sl.head(3).iterrows():
    print(f"\n{row['Rank']}. {row['mutation']} × {row['target']}")
    print(f"   Effect size: {row['mean_diff']:.4f} (p={row['p_value']:.4e})")
    print(f"   Mutant cells: n={row['n_mutant']}, mean={row['mutant_mean']:.4f}")
    print(f"   WT cells: n={row['n_wt']}, mean={row['wt_mean']:.4f}")
    print(f"   Most dependent mutant: {row['most_dependent_mutant_cell']}")
    print(f"   Mutant cell lines: {row['mutant_cell_lines'][:100]}...")
    print(f"   Mutant individual scores (first 5):")
    scores = row["mutant_individual_scores"].split(", ")[:5]
    for score in scores:
        if ":" in score:
            parts = score.split(": ")
            if len(parts) == 2:
                cell_info, val = parts
                val_float = float(val)
                if val_float < -0.3:
                    print(f"     ⭐ {cell_info}: {val} (HIGHLY DEPENDENT)")
                elif val_float < -0.1:
                    print(f"     ✅ {cell_info}: {val} (Dependent)")
                else:
                    print(f"     {cell_info}: {val}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
