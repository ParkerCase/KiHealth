#!/usr/bin/env python3
"""
Update literature scores with curated STK17A papers from STARX team
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

print("=" * 80)
print("UPDATING LITERATURE SCORES WITH CURATED STK17A PAPERS")
print("=" * 80)

# Load current scores
lit_scoring = pd.read_csv(DATA_PROCESSED / "literature_scoring.csv")

# Load curated papers
curated_papers = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "StarXData" / "literature_metadata_STK17A.csv")

# Count valid papers (exclude "Not found" and "Information not accessible")
valid_papers = curated_papers[
    (~curated_papers['Title'].str.contains('Not found', na=False)) &
    (~curated_papers['Main_Finding'].str.contains('not accessible', na=False))
]

print(f"\n✓ Loaded {len(curated_papers)} curated STK17A papers")
print(f"✓ {len(valid_papers)} papers have valid metadata")

# Map papers to cancer types based on titles/findings
cancer_type_mapping = {
    'Glioblastoma': 2,  # Papers 3, 15
    'Diffuse Glioma': 2,  # Same as glioblastoma
    'Pancreatic Adenocarcinoma': 1,  # Paper 2
    'Head and Neck Squamous Cell Carcinoma': 1,  # Paper 5
    'Ovarian Epithelial Tumor': 1,  # Paper 6
    'Cervical Adenocarcinoma': 3,  # Papers 8, 11, 14
    'Cervical Squamous Cell Carcinoma': 3,  # Same cervical cancer group
    'Mixed Cervical Carcinoma': 3,
    'Colorectal Adenocarcinoma': 1,  # Paper 10
    'Gastric Adenocarcinoma': 1,  # Paper 12
}

# Update STK17A counts for specific cancer types
for cancer_type, additional_papers in cancer_type_mapping.items():
    if cancer_type in lit_scoring['cancer_type'].values:
        lit_scoring.loc[lit_scoring['cancer_type'] == cancer_type, 'STK17A_paper_count'] += additional_papers

# Recalculate total counts and scores
lit_scoring['total_paper_count'] = (
    lit_scoring['STK17A_paper_count'] + 
    lit_scoring['MYLK4_paper_count'] + 
    lit_scoring['TBK1_paper_count'] + 
    lit_scoring['CLK4_paper_count']
)

lit_scoring['recent_paper_count'] = lit_scoring['total_paper_count']  # Assume curated papers are recent
lit_scoring['literature_confidence_score'] = lit_scoring['total_paper_count'].apply(lambda x: min(1.0, x / 80))
lit_scoring['has_clinical_evidence'] = lit_scoring['recent_paper_count'] > 0

# Save updated scores
output_file = DATA_PROCESSED / "literature_scoring.csv"
lit_scoring.to_csv(output_file, index=False)

print(f"\n✓ Updated literature scores saved to: {output_file}")

# Show top 10 cancer types by literature score
print("\nTop 10 cancer types by updated literature score:")
top_10 = lit_scoring.nlargest(10, 'literature_confidence_score')[
    ['cancer_type', 'STK17A_paper_count', 'TBK1_paper_count', 'total_paper_count', 'literature_confidence_score']
]
print(top_10.to_string(index=False))

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"Total STK17A papers added: {lit_scoring['STK17A_paper_count'].sum()}")
print(f"Cancer types with STK17A papers: {(lit_scoring['STK17A_paper_count'] > 0).sum()}")
print(f"Cancer types with high literature (score > 0.1): {(lit_scoring['literature_confidence_score'] > 0.1).sum()}")

print("\n✅ Literature scoring updated with curated STARX team papers")
