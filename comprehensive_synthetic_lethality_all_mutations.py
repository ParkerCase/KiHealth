"""
COMPREHENSIVE SYNTHETIC LETHALITY ANALYSIS
Tests ALL available mutations against the 4 targets (STK17A, MYLK4, TBK1, CLK4)

This script:
1. Loads all mutation data (hotspot mutations)
2. Tests every mutation gene that has sufficient samples (≥3 mutants, ≥10 WT)
3. Applies multiple testing correction (FDR)
4. Identifies all true synthetic lethality hits
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings

warnings.filterwarnings("ignore")


# FDR correction (Benjamini-Hochberg) - manual implementation
def fdr_correction(p_values, alpha=0.10):
    """
    Apply Benjamini-Hochberg FDR correction
    Returns: rejected (boolean array), p_adjusted (array)
    """
    p_values = np.array(p_values)
    n = len(p_values)

    # Sort p-values and get indices
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # Calculate adjusted p-values
    p_adjusted = np.zeros(n)
    for i in range(n - 1, -1, -1):  # Start from the end
        if i == n - 1:
            p_adjusted[sorted_indices[i]] = sorted_p[i]
        else:
            p_adjusted[sorted_indices[i]] = min(
                sorted_p[i] * n / (i + 1), p_adjusted[sorted_indices[i + 1]]
            )

    # Bonferroni correction
    p_bonf = p_values * n
    p_bonf = np.minimum(p_bonf, 1.0)  # Cap at 1.0

    rejected = p_adjusted < alpha

    return rejected, p_adjusted, p_bonf


print("=" * 80)
print("COMPREHENSIVE SYNTHETIC LETHALITY ANALYSIS")
print("Testing ALL mutations against 4 targets")
print("=" * 80)

# ============================================================================
# STEP 1: Load Dependency Data
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: Loading dependency data...")
print("=" * 80)

depmap = pd.read_csv("data/raw/depmap/CRISPRGeneDependency.csv", index_col=0)
depmap = depmap.reset_index()
depmap.columns.values[0] = "ModelID"
print(f"Total cell lines in dependency data: {len(depmap)}")

# Get target gene columns
targets = {
    "STK17A": [
        col for col in depmap.columns if "STK17A" in col and "STK17B" not in col
    ][0],
    "MYLK4": [col for col in depmap.columns if "MYLK4" in col][0],
    "TBK1": [col for col in depmap.columns if "TBK1" in col][0],
    "CLK4": [col for col in depmap.columns if "CLK4" in col][0],
}

print("\nTarget gene columns found:")
for gene, col in targets.items():
    print(f"  {gene}: {col}")

# Create clean dependency dataframe
dep_clean = depmap[["ModelID"] + list(targets.values())].copy()
dep_clean.columns = ["ModelID", "STK17A", "MYLK4", "TBK1", "CLK4"]

print(f"\nDependency data shape: {dep_clean.shape}")
print(f"Cell lines with dependency data: {len(dep_clean)}")

# ============================================================================
# STEP 2: Load Mutation Data
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: Loading mutation data...")
print("=" * 80)

mutations_hotspot = pd.read_csv(
    "data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv"
)
print(f"Total rows in mutation file: {len(mutations_hotspot)}")

# Set ModelID as index for easier merging
if "ModelID" in mutations_hotspot.columns:
    mutations_hotspot = mutations_hotspot.set_index("ModelID")
else:
    # If ModelID is not a column, it might be the first column after index
    mutations_hotspot = mutations_hotspot.reset_index()
    if "ModelID" in mutations_hotspot.columns:
        mutations_hotspot = mutations_hotspot.set_index("ModelID")

print(f"Mutation data shape: {mutations_hotspot.shape}")
print(f"Sample ModelIDs: {mutations_hotspot.index[:3].tolist()}")

# Identify mutation gene columns (exclude metadata columns)
metadata_cols = [
    "SequencingID",
    "ModelConditionID",
    "IsDefaultEntryForModel",
    "IsDefaultEntryForMC",
]
mutation_cols = [col for col in mutations_hotspot.columns if col not in metadata_cols]

print(f"\nTotal mutation gene columns: {len(mutation_cols)}")
print(f"Sample mutation genes: {mutation_cols[:5]}")

# ============================================================================
# STEP 3: Find Common Cell Lines
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: Finding common cell lines...")
print("=" * 80)

common_ids = set(dep_clean["ModelID"]).intersection(set(mutations_hotspot.index))
print(f"Cell lines with BOTH dependency and mutation data: {len(common_ids)}")

# Filter both datasets to common cell lines
dep_common = dep_clean[dep_clean["ModelID"].isin(common_ids)].copy()
mut_common = mutations_hotspot.loc[mutations_hotspot.index.isin(common_ids)].copy()

print(f"Dependency data (filtered): {len(dep_common)}")
print(f"Mutation data (filtered): {len(mut_common)}")

# ============================================================================
# STEP 4: Identify Testable Mutations
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: Identifying testable mutations...")
print("=" * 80)

# Minimum sample size requirements
MIN_MUTANTS = 3
MIN_WT = 10

testable_mutations = []
for mut_col in mutation_cols:
    if mut_col in mut_common.columns:
        # Count mutants and WT in common cell lines
        mut_status = mut_common[mut_col].fillna(0)
        n_mutant = (mut_status == 1).sum()
        n_wt = (mut_status == 0).sum()

        if n_mutant >= MIN_MUTANTS and n_wt >= MIN_WT:
            # Extract gene name (format: "GENE_NAME (ENTREZ_ID)")
            gene_name = mut_col.split()[0] if " " in mut_col else mut_col
            testable_mutations.append(
                {
                    "gene": gene_name,
                    "column": mut_col,
                    "n_mutant": n_mutant,
                    "n_wt": n_wt,
                }
            )

print(
    f"Mutations with sufficient samples (≥{MIN_MUTANTS} mutants, ≥{MIN_WT} WT): {len(testable_mutations)}"
)
print(f"\nTop 20 mutations by mutant count:")
for i, mut in enumerate(
    sorted(testable_mutations, key=lambda x: x["n_mutant"], reverse=True)[:20], 1
):
    print(
        f"  {i:2d}. {mut['gene']:15s}: {mut['n_mutant']:4d} mutants, {mut['n_wt']:4d} WT"
    )

# ============================================================================
# STEP 5: Run Synthetic Lethality Analysis
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: Running synthetic lethality analysis...")
print("=" * 80)
print(
    f"Testing {len(testable_mutations)} mutations × 4 targets = {len(testable_mutations) * 4} combinations"
)

results = []
target_genes = ["STK17A", "MYLK4", "TBK1", "CLK4"]

# Merge dependency and mutation data once
merged = dep_common.merge(
    mut_common.reset_index()[["ModelID"] + [m["column"] for m in testable_mutations]],
    on="ModelID",
    how="inner",
)

print(f"Merged data shape: {merged.shape}")

# Progress tracking
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

        # Split into mutant and wild-type groups
        mutant_deps = merged[merged[mut_col] == 1][target_gene].dropna()
        wt_deps = merged[merged[mut_col] == 0][target_gene].dropna()

        # Double-check sample sizes (should already be filtered, but just in case)
        if len(mutant_deps) < MIN_MUTANTS or len(wt_deps) < MIN_WT:
            continue

        # Calculate statistics
        mutant_mean = mutant_deps.mean()
        wt_mean = wt_deps.mean()
        mean_diff = mutant_mean - wt_mean

        # Welch's t-test (unequal variances)
        try:
            t_stat, p_val = stats.ttest_ind(mutant_deps, wt_deps, equal_var=False)
        except:
            continue

        # Store result
        results.append(
            {
                "mutation": mut_gene,
                "mutation_column": mut_col,
                "target": target_gene,
                "n_mutant": len(mutant_deps),
                "n_wt": len(wt_deps),
                "mutant_mean": mutant_mean,
                "wt_mean": wt_mean,
                "mean_diff": mean_diff,
                "p_value": p_val,
                "is_synthetic_lethal": mean_diff < 0,  # Negative = SL
            }
        )

# Convert to DataFrame
results_df = pd.DataFrame(results)
print(f"\nTotal combinations tested: {len(results_df)}")

# ============================================================================
# STEP 6: Multiple Testing Correction
# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: Applying multiple testing correction...")
print("=" * 80)

# Apply FDR correction (Benjamini-Hochberg)
p_values = results_df["p_value"].values
rejected, p_adjusted, p_bonf = fdr_correction(p_values, alpha=0.10)
results_df["p_adjusted_fdr"] = p_adjusted
results_df["significant_fdr"] = rejected

# Bonferroni correction
results_df["p_adjusted_bonf"] = p_bonf
results_df["significant_bonf"] = p_bonf < 0.10

# Original significance (p < 0.10, no correction)
results_df["significant_uncorrected"] = results_df["p_value"] < 0.10

print(
    f"Significant hits (uncorrected p < 0.10): {results_df['significant_uncorrected'].sum()}"
)
print(
    f"Significant hits (FDR corrected, q < 0.10): {results_df['significant_fdr'].sum()}"
)
print(
    f"Significant hits (Bonferroni corrected, p < 0.10): {results_df['significant_bonf'].sum()}"
)

# ============================================================================
# STEP 7: Identify True Synthetic Lethality Hits
# ============================================================================
print("\n" + "=" * 80)
print("STEP 7: Identifying true synthetic lethality hits...")
print("=" * 80)

# True SL: negative mean_diff (mutants more dependent) AND significant
true_sl_uncorrected = results_df[
    (results_df["mean_diff"] < 0) & (results_df["significant_uncorrected"])
].copy()

true_sl_fdr = results_df[
    (results_df["mean_diff"] < 0) & (results_df["significant_fdr"])
].copy()

true_sl_bonf = results_df[
    (results_df["mean_diff"] < 0) & (results_df["significant_bonf"])
].copy()

print(f"True synthetic lethality hits (uncorrected): {len(true_sl_uncorrected)}")
print(f"True synthetic lethality hits (FDR corrected): {len(true_sl_fdr)}")
print(f"True synthetic lethality hits (Bonferroni corrected): {len(true_sl_bonf)}")

# Sort by effect size (most negative = strongest)
if len(true_sl_uncorrected) > 0:
    true_sl_uncorrected = true_sl_uncorrected.sort_values("mean_diff")
    print("\n" + "=" * 80)
    print("TOP 20 SYNTHETIC LETHALITY HITS (Uncorrected)")
    print("=" * 80)
    print(
        true_sl_uncorrected[
            [
                "mutation",
                "target",
                "mean_diff",
                "p_value",
                "p_adjusted_fdr",
                "n_mutant",
                "n_wt",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

if len(true_sl_fdr) > 0:
    true_sl_fdr = true_sl_fdr.sort_values("mean_diff")
    print("\n" + "=" * 80)
    print("TOP 20 SYNTHETIC LETHALITY HITS (FDR Corrected)")
    print("=" * 80)
    print(
        true_sl_fdr[
            [
                "mutation",
                "target",
                "mean_diff",
                "p_value",
                "p_adjusted_fdr",
                "n_mutant",
                "n_wt",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

# ============================================================================
# STEP 8: Save Results
# ============================================================================
print("\n" + "=" * 80)
print("STEP 8: Saving results...")
print("=" * 80)

# Save complete results
output_file = "data/processed/comprehensive_synthetic_lethality_all_mutations.csv"
results_df.to_csv(output_file, index=False)
print(f"✅ Saved complete results: {output_file}")

# Save true SL hits (uncorrected)
if len(true_sl_uncorrected) > 0:
    sl_file = "data/processed/true_synthetic_lethality_all_mutations.csv"
    true_sl_uncorrected.to_csv(sl_file, index=False)
    print(f"✅ Saved true SL hits (uncorrected): {sl_file}")

# Save true SL hits (FDR corrected)
if len(true_sl_fdr) > 0:
    sl_fdr_file = "data/processed/true_synthetic_lethality_fdr_corrected.csv"
    true_sl_fdr.to_csv(sl_fdr_file, index=False)
    print(f"✅ Saved true SL hits (FDR corrected): {sl_fdr_file}")

# Create summary by target
print("\n" + "=" * 80)
print("SUMMARY BY TARGET GENE")
print("=" * 80)

for target in target_genes:
    target_results = true_sl_uncorrected[true_sl_uncorrected["target"] == target]
    print(f"\n{target}: {len(target_results)} synthetic lethality hits")
    if len(target_results) > 0:
        print(
            target_results[["mutation", "mean_diff", "p_value", "n_mutant"]]
            .head(10)
            .to_string(index=False)
        )

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nTotal mutations tested: {len(testable_mutations)}")
print(f"Total combinations tested: {len(results_df)}")
print(f"True synthetic lethality hits (uncorrected): {len(true_sl_uncorrected)}")
print(f"True synthetic lethality hits (FDR corrected): {len(true_sl_fdr)}")
