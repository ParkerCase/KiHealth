"""
Generate Xata Schema for StarX Therapeutics Database
=====================================================

This creates the exact table schemas you need in Xata with semantic search enabled.
"""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Xata schema configuration
SCHEMA = {
    "tables": [
        {
            "name": "cancer_rankings",
            "columns": [
                {"name": "cancer_type", "type": "string"},
                {"name": "rank", "type": "int"},
                {"name": "overall_score", "type": "float"},
                {"name": "confidence_tier", "type": "string"},
                {"name": "depmap_score", "type": "float"},
                {"name": "expression_score", "type": "float"},
                {"name": "mutation_score", "type": "float"},
                {"name": "copy_number_score", "type": "float"},
                {"name": "literature_score", "type": "float"},
                {"name": "n_cell_lines", "type": "int"},
                {"name": "n_validated_lines", "type": "int"},
                {"name": "validation_available", "type": "bool"},
                {"name": "significant_sl_hits", "type": "int"},
                {"name": "key_findings", "type": "text"},
                {"name": "stk17a_score", "type": "float"},
                {"name": "mylk4_score", "type": "float"},
                {"name": "tbk1_score", "type": "float"},
                {"name": "clk4_score", "type": "float"},
                {"name": "summary", "type": "text"},  # Enable semantic search on this!
                {"name": "last_updated", "type": "datetime"}
            ]
        },
        {
            "name": "target_scores",
            "columns": [
                {"name": "cancer_type", "type": "string"},
                {"name": "cancer_rank", "type": "int"},
                {"name": "target_gene", "type": "string"},
                {"name": "dependency_score", "type": "float"},
                {"name": "cancer_overall_score", "type": "float"},
                {"name": "confidence_tier", "type": "string"},
                {"name": "n_cell_lines", "type": "int"},
                {"name": "validation_available", "type": "bool"},
                {"name": "summary", "type": "text"}  # Semantic search enabled
            ]
        },
        {
            "name": "synthetic_lethality",
            "columns": [
                {"name": "mutation", "type": "string"},
                {"name": "target_gene", "type": "string"},
                {"name": "n_mutant_lines", "type": "int"},
                {"name": "n_wt_lines", "type": "int"},
                {"name": "mutant_mean_score", "type": "float"},
                {"name": "wt_mean_score", "type": "float"},
                {"name": "effect_size", "type": "float"},
                {"name": "p_value", "type": "float"},
                {"name": "is_significant", "type": "bool"},
                {"name": "most_dependent_line", "type": "string"},
                {"name": "mutant_lines_sample", "type": "json"},
                {"name": "summary", "type": "text"}  # Semantic search enabled
            ]
        },
        {
            "name": "cell_line_dependencies",
            "columns": [
                {"name": "cancer_type", "type": "string"},
                {"name": "target_gene", "type": "string"},
                {"name": "mean_dependency_score", "type": "float"},
                {"name": "n_lines_tested", "type": "int"},
                {"name": "cancer_overall_rank", "type": "int"},
                {"name": "summary", "type": "text"}  # Semantic search enabled
            ]
        },
        {
            "name": "papers",
            "columns": [
                {"name": "pubmed_id", "type": "string"},
                {"name": "title", "type": "string"},
                {"name": "abstract", "type": "text"},  # Main semantic search field
                {"name": "authors", "type": "string"},
                {"name": "journal", "type": "string"},
                {"name": "publication_date", "type": "datetime"},
                {"name": "cancer_types", "type": "multiple"},
                {"name": "target_genes", "type": "multiple"},
                {"name": "relevance_score", "type": "float"},
                {"name": "citation_count", "type": "int"}
            ]
        }
    ]
}

# Save schema
with open(OUTPUT_DIR / "xata_schema.json", "w") as f:
    json.dump(SCHEMA, f, indent=2)

print("✅ Created xata_schema.json")
print()
print("📋 Xata Setup Instructions:")
print("=" * 60)
print()
print("You already have Xata configured! Database:")
print("   https://Parker-Case-s-workspace-s4h25u.us-east-1.xata.sh/db/starx-therapeutics")
print()
print("To create tables:")
print()
print("Option 1: Use Xata CLI (recommended)")
print("   1. Install: npm install -g @xata.io/cli")
print("   2. Run: xata schema edit")
print("   3. Paste the schema from xata_schema.json")
print()
print("Option 2: Use Xata Web UI")
print("   1. Go to: https://app.xata.io")
print("   2. Select your 'starx-therapeutics' database")
print("   3. Create each table manually using the schema")
print()
print("Option 3: Use the Python SDK (automated)")
print("   Run: python xata_integration/upload_to_xata.py")
print()
print("🔍 Enable Semantic Search:")
print("   In Xata UI, for each table:")
print("   1. Go to table settings")
print("   2. Find the 'summary' column")
print("   3. Enable 'Vector Search'")
print("   4. Select OpenAI ada-002 embeddings (free tier)")
print()

# Generate TypeScript types for Next.js
typescript_types = """
// Auto-generated Xata types for Next.js
// Location: src/xata.ts

export interface CancerRanking {
  id: string;
  cancer_type: string;
  rank: number;
  overall_score: number;
  confidence_tier: 'HIGH' | 'MEDIUM' | 'LOW';
  depmap_score: number;
  expression_score: number;
  mutation_score: number;
  copy_number_score: number;
  literature_score: number;
  n_cell_lines: number;
  n_validated_lines: number;
  validation_available: boolean;
  significant_sl_hits: number;
  key_findings: string;
  stk17a_score: number;
  mylk4_score: number;
  tbk1_score: number;
  clk4_score: number;
  summary: string;
  last_updated: Date;
}

export interface TargetScore {
  id: string;
  cancer_type: string;
  cancer_rank: number;
  target_gene: string;
  dependency_score: number;
  cancer_overall_score: number;
  confidence_tier: string;
  n_cell_lines: number;
  validation_available: boolean;
  summary: string;
}

export interface SyntheticLethality {
  id: string;
  mutation: string;
  target_gene: string;
  n_mutant_lines: number;
  n_wt_lines: number;
  mutant_mean_score: number;
  wt_mean_score: number;
  effect_size: number;
  p_value: number;
  is_significant: boolean;
  most_dependent_line: string;
  mutant_lines_sample: string[];
  summary: string;
}
"""

with open(OUTPUT_DIR / "xata_types.ts", "w") as f:
    f.write(typescript_types)

print("✅ Also created xata_types.ts for Next.js")
print()
