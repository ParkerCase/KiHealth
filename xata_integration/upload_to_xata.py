"""
Upload StarX Data to Xata
==========================

This script uploads your prepared JSON data to Xata.
Requires: pip install xata
"""

import json
import os
from pathlib import Path
from xata.client import XataClient

# Configuration
OUTPUT_DIR = Path(__file__).parent / "output"
DATABASE_URL = "https://Parker-Case-s-workspace-s4h25u.us-east-1.xata.sh/db/starx-therapeutics:main"

# Initialize Xata client
# Make sure XATA_API_KEY is in your .env file
xata = XataClient(db_url=DATABASE_URL)

print("🚀 Uploading StarX Data to Xata")
print("=" * 60)
print()

# =============================================================================
# Upload Cancer Rankings
# =============================================================================
print("📊 Uploading cancer rankings...")

with open(OUTPUT_DIR / "cancer_rankings.json") as f:
    cancer_rankings = json.load(f)

# Bulk insert (Xata supports up to 1000 records per request)
batch_size = 100
for i in range(0, len(cancer_rankings), batch_size):
    batch = cancer_rankings[i:i+batch_size]
    
    try:
        xata.data().bulk_insert("cancer_rankings", {
            "records": batch
        })
        print(f"   ✅ Uploaded batch {i//batch_size + 1} ({len(batch)} records)")
    except Exception as e:
        print(f"   ❌ Error in batch {i//batch_size + 1}: {e}")

print(f"✅ Finished cancer_rankings ({len(cancer_rankings)} total)")
print()

# =============================================================================
# Upload Target Scores
# =============================================================================
print("🎯 Uploading target scores...")

with open(OUTPUT_DIR / "target_scores.json") as f:
    target_scores = json.load(f)

for i in range(0, len(target_scores), batch_size):
    batch = target_scores[i:i+batch_size]
    
    try:
        xata.data().bulk_insert("target_scores", {
            "records": batch
        })
        print(f"   ✅ Uploaded batch {i//batch_size + 1} ({len(batch)} records)")
    except Exception as e:
        print(f"   ❌ Error in batch {i//batch_size + 1}: {e}")

print(f"✅ Finished target_scores ({len(target_scores)} total)")
print()

# =============================================================================
# Upload Synthetic Lethality
# =============================================================================
print("🧬 Uploading synthetic lethality data...")

sl_file = OUTPUT_DIR / "synthetic_lethality.json"
if sl_file.exists():
    with open(sl_file) as f:
        sl_records = json.load(f)
    
    for i in range(0, len(sl_records), batch_size):
        batch = sl_records[i:i+batch_size]
        
        try:
            xata.data().bulk_insert("synthetic_lethality", {
                "records": batch
            })
            print(f"   ✅ Uploaded batch {i//batch_size + 1} ({len(batch)} records)")
        except Exception as e:
            print(f"   ❌ Error in batch {i//batch_size + 1}: {e}")
    
    print(f"✅ Finished synthetic_lethality ({len(sl_records)} total)")
else:
    print("⚠️  No synthetic_lethality.json found, skipping")
print()

# =============================================================================
# Upload Cell Line Dependencies
# =============================================================================
print("🧫 Uploading cell line dependencies...")

with open(OUTPUT_DIR / "cell_line_dependencies.json") as f:
    cell_lines = json.load(f)

for i in range(0, len(cell_lines), batch_size):
    batch = cell_lines[i:i+batch_size]
    
    try:
        xata.data().bulk_insert("cell_line_dependencies", {
            "records": batch
        })
        print(f"   ✅ Uploaded batch {i//batch_size + 1} ({len(batch)} records)")
    except Exception as e:
        print(f"   ❌ Error in batch {i//batch_size + 1}: {e}")

print(f"✅ Finished cell_line_dependencies ({len(cell_lines)} total)")
print()

# =============================================================================
# Summary
# =============================================================================
print("=" * 60)
print("✨ UPLOAD COMPLETE!")
print()
print("🔍 Next Steps:")
print("   1. Go to: https://app.xata.io")
print("   2. Select 'starx-therapeutics' database")
print("   3. Enable semantic search on 'summary' columns:")
print("      - cancer_rankings.summary")
print("      - target_scores.summary")
print("      - synthetic_lethality.summary")
print("      - cell_line_dependencies.summary")
print()
print("   4. Test semantic search:")
print('      Query: "melanoma with NRAS mutations"')
print('      Query: "glioblastoma high dependency"')
print('      Query: "TBK1 synthetic lethality"')
print()
print("🚀 Ready to build your dashboard!")
print()
