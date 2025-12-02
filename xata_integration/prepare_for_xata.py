"""
StarX Therapeutics - Xata Data Preparation Script
==================================================

This script transforms your processed analysis data into Xata-ready format
with rich text summaries for AI/ML semantic search.

SAFE TO RUN: Only reads from data/processed/ and writes to xata_integration/output/
Does NOT modify any existing files or code.
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# File paths (READ ONLY - won't modify these)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = Path(__file__).parent / "output"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

print("🔬 StarX Therapeutics → Xata Data Preparation")
print("=" * 60)
print(f"📂 Reading from: {DATA_DIR}")
print(f"📝 Writing to: {OUTPUT_DIR}")
print()

# =============================================================================
# 1. CANCER RANKINGS TABLE
# =============================================================================
print("📊 Processing cancer rankings...")

rankings_df = pd.read_csv(DATA_DIR / "final_integrated_rankings_COMPLETE.csv")

cancer_rankings = []
for _, row in rankings_df.iterrows():
    # Create rich text summary for semantic search
    summary_parts = []
    summary_parts.append(
        f"{row['cancer_type']} ranks #{row['rank']} with overall score {row['overall_score']:.3f}"
    )
    summary_parts.append(f"Confidence: {row['confidence_tier']}")

    if row["n_cell_lines"] > 0:
        summary_parts.append(f"Tested in {int(row['n_cell_lines'])} cell lines")

    if row["validation_data_available"]:
        summary_parts.append(
            f"IC50 validation available ({int(row['n_validated_cell_lines'])} lines)"
        )

    if row["significant_SL_hits"] > 0:
        summary_parts.append(
            f"{int(row['significant_SL_hits'])} significant synthetic lethality hits"
        )

    # Add target-specific info
    target_scores = []
    for target in ["STK17A", "MYLK4", "TBK1", "CLK4"]:
        score = row[f"{target}_dependency_mean"]
        if score < -0.15:
            target_scores.append(
                f"{target} shows strong dependency (score: {score:.3f})"
            )
        elif score < -0.08:
            target_scores.append(
                f"{target} shows moderate dependency (score: {score:.3f})"
            )

    if target_scores:
        summary_parts.extend(target_scores)

    summary_parts.append(row["key_findings"])

    record = {
        "cancer_type": row["cancer_type"],
        "rank": int(row["rank"]),
        "overall_score": float(row["overall_score"]),
        "confidence_tier": row["confidence_tier"],
        "depmap_score": float(row["depmap_score_normalized"]),
        "expression_score": float(row["expression_score_normalized"]),
        "mutation_score": float(row["mutation_context_score"]),
        "copy_number_score": float(row["copy_number_score"]),
        "literature_score": float(row["literature_score_normalized"]),
        "n_cell_lines": int(row["n_cell_lines"]),
        "n_validated_lines": (
            int(row["n_validated_cell_lines"])
            if pd.notna(row["n_validated_cell_lines"])
            else 0
        ),
        "validation_available": bool(row["validation_data_available"]),
        "significant_sl_hits": (
            int(row["significant_SL_hits"])
            if pd.notna(row["significant_SL_hits"])
            else 0
        ),
        "key_findings": row["key_findings"],
        # Individual target scores
        "stk17a_score": float(row["STK17A_dependency_mean"]),
        "mylk4_score": float(row["MYLK4_dependency_mean"]),
        "tbk1_score": float(row["TBK1_dependency_mean"]),
        "clk4_score": float(row["CLK4_dependency_mean"]),
        # Rich summary for semantic search (THIS IS KEY!)
        "summary": " | ".join(summary_parts),
        "last_updated": datetime.now().isoformat(),
    }

    cancer_rankings.append(record)

# Save as JSON for Xata
with open(OUTPUT_DIR / "cancer_rankings.json", "w") as f:
    json.dump(cancer_rankings, f, indent=2)

print(f"✅ Created cancer_rankings.json ({len(cancer_rankings)} records)")
print(f"   Top cancer: {cancer_rankings[0]['cancer_type']}")
print()

# =============================================================================
# 2. INDIVIDUAL TARGET SCORES TABLE
# =============================================================================
print(" Processing individual target scores...")

target_scores = []
for _, row in rankings_df.iterrows():
    for target in ["STK17A", "MYLK4", "TBK1", "CLK4"]:
        dependency_score = row[f"{target}_dependency_mean"]

        # Create rich summary
        summary = f"{target} in {row['cancer_type']}: "
        if dependency_score < -0.15:
            summary += f"Strong dependency (score: {dependency_score:.3f}). "
        elif dependency_score < -0.08:
            summary += f"Moderate dependency (score: {dependency_score:.3f}). "
        else:
            summary += f"Weak/no dependency (score: {dependency_score:.3f}). "

        summary += f"Cancer overall rank: #{int(row['rank'])} with {row['confidence_tier']} confidence."

        if row["validation_data_available"]:
            summary += " IC50 validation data available."

        record = {
            "cancer_type": row["cancer_type"],
            "cancer_rank": int(row["rank"]),
            "target_gene": target,
            "dependency_score": float(dependency_score),
            "cancer_overall_score": float(row["overall_score"]),
            "confidence_tier": row["confidence_tier"],
            "n_cell_lines": int(row["n_cell_lines"]),
            "validation_available": bool(row["validation_data_available"]),
            "summary": summary,  # For semantic search
        }

        target_scores.append(record)

with open(OUTPUT_DIR / "target_scores.json", "w") as f:
    json.dump(target_scores, f, indent=2)

print(f"✅ Created target_scores.json ({len(target_scores)} records)")
print()

# =============================================================================
# 3. SYNTHETIC LETHALITY TABLE
# =============================================================================
print("🧬 Processing synthetic lethality data...")

# Read synthetic lethality file (may be large)
try:
    sl_df = pd.read_csv(DATA_DIR / "synthetic_lethality_COMPLETE_WITH_CELL_LINES.csv")

    # Filter to only significant hits (p < 0.10 and marked as synthetic lethal)
    significant_sl = sl_df[sl_df["is_synthetic_lethal"] == True].copy()

    sl_records = []
    for _, row in significant_sl.head(500).iterrows():  # Limit to top 500 for now
        # Parse cell lines
        mutant_lines = (
            row["mutant_cell_lines"].split(", ")
            if pd.notna(row["mutant_cell_lines"])
            else []
        )

        # Create rich summary
        summary = f"{row['mutation']} mutation shows synthetic lethality with {row['target']}. "
        summary += f"Effect size: {row['mean_diff']:.3f} (p={row['p_value']:.4f}). "
        summary += f"Tested in {int(row['n_mutant'])} mutant lines vs {int(row['n_wt'])} wild-type lines. "

        if mutant_lines:
            summary += (
                f"Most dependent mutant line: {row['most_dependent_mutant_cell']}"
            )

        record = {
            "mutation": row["mutation"],
            "target_gene": row["target"],
            "n_mutant_lines": int(row["n_mutant"]),
            "n_wt_lines": int(row["n_wt"]),
            "mutant_mean_score": float(row["mutant_mean"]),
            "wt_mean_score": float(row["wt_mean"]),
            "effect_size": float(row["mean_diff"]),
            "p_value": float(row["p_value"]),
            "is_significant": bool(row["is_synthetic_lethal"]),
            "most_dependent_line": (
                str(row["most_dependent_mutant_cell"])
                if pd.notna(row["most_dependent_mutant_cell"])
                else ""
            ),
            "mutant_lines_sample": mutant_lines[:5],  # First 5 for reference
            "summary": summary,  # For semantic search
        }

        sl_records.append(record)

    with open(OUTPUT_DIR / "synthetic_lethality.json", "w") as f:
        json.dump(sl_records, f, indent=2)

    print(f"✅ Created synthetic_lethality.json ({len(sl_records)} significant hits)")
    print()
except Exception as e:
    print(f"⚠️  Skipping synthetic lethality (error: {e})")
    print()

# =============================================================================
# 4. CELL LINE DATA TABLE
# =============================================================================
print("🧫 Processing cell line dependency data...")

# We'll create a sample of top dependent cell lines across all targets
cell_line_records = []

# Get top 100 overall cancer types
for _, row in rankings_df.head(100).iterrows():
    cancer_type = row["cancer_type"]

    for target in ["STK17A", "MYLK4", "TBK1", "CLK4"]:
        score = row[f"{target}_dependency_mean"]

        if score < -0.08:  # Only include meaningful dependencies
            summary = f"Cell lines from {cancer_type} show dependency on {target}. "
            summary += f"Mean dependency score: {score:.3f}. "
            summary += f"Cancer ranks #{int(row['rank'])} overall."

            record = {
                "cancer_type": cancer_type,
                "target_gene": target,
                "mean_dependency_score": float(score),
                "n_lines_tested": int(row["n_cell_lines"]),
                "cancer_overall_rank": int(row["rank"]),
                "summary": summary,
            }

            cell_line_records.append(record)

with open(OUTPUT_DIR / "cell_line_dependencies.json", "w") as f:
    json.dump(cell_line_records, f, indent=2)

print(f"✅ Created cell_line_dependencies.json ({len(cell_line_records)} records)")
print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 60)
print("✨ DATA PREPARATION COMPLETE!")
print()
print("📁 Generated files in xata_integration/output/:")
print("   1. cancer_rankings.json          - Main cancer type rankings")
print("   2. target_scores.json            - Per-target dependency scores")
print("   3. synthetic_lethality.json      - Mutation context hits")
print("   4. cell_line_dependencies.json   - Cell line dependencies")
print()
print("🚀 Next steps:")
print("   1. Review the generated JSON files")
print("   2. Run: python xata_integration/create_xata_schema.py")
print("   3. Follow the Xata setup instructions")
print()
