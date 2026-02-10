"""Validate CHNS addition to unified dataset."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

def main():
    csv_path = PROJECT_ROOT / "data" / "processed" / "kihealth_unified.csv"
    if not csv_path.exists():
        print(f"ERROR: Unified CSV not found: {csv_path}")
        print("Run: python scripts/merge_chns_2009.py then build_unified_kihealth(save_path=...)")
        return 1

    print("=" * 70)
    print("CHNS ADDITION VALIDATION")
    print("=" * 70)

    df = pd.read_csv(csv_path)

    # Check CHNS is present
    chns = df[df.dataset_source == "chns_2009"]
    print(f"\n1. CHNS rows in unified dataset: {len(chns)} / {len(df)}")

    if len(chns) == 0:
        print("❌ ERROR: No CHNS data found!")
        return 1

    if len(chns) < 9500:
        print(f"⚠️ WARNING: Expected ~9,549 CHNS rows, got {len(chns)}")
    else:
        print(f"✅ CHNS row count: {len(chns)} (expected ~9,549)")

    # Check HOMA eligibility
    chns_eligible = chns[chns.homa_analysis_eligible]
    print(f"\n2. CHNS HOMA-eligible: {len(chns_eligible)} / {len(chns)} ({100 * len(chns_eligible) / len(chns):.1f}%)")

    if len(chns_eligible) < 9400:
        print(f"⚠️ WARNING: Expected ~9,479 eligible, got {len(chns_eligible)}")
    else:
        print(f"✅ CHNS HOMA-eligible count: {len(chns_eligible)}")

    # Check key variables
    print(f"\n3. Key variables present:")
    required_vars = ["age_years", "sex", "bmi_kg_m2", "glucose_mg_dl", "insulin_uU_ml", "hba1c_percent"]
    for var in required_vars:
        missing_pct = 100 * chns[var].isna().sum() / len(chns)
        status = "✅" if missing_pct < 5 else "⚠️"
        print(f"  {status} {var:20s} {missing_pct:5.1f}% missing")

    # Check total HOMA-eligible
    total_eligible = int(df.homa_analysis_eligible.sum())
    print(f"\n4. Total HOMA-eligible samples: {total_eligible}")
    print(f"   Expected: ~18,565 (9,086 NHANES + 9,479 CHNS)")

    if total_eligible < 18000:
        print(f"⚠️ WARNING: Expected ~18,565, got {total_eligible}")
    else:
        print(f"✅ Total HOMA-eligible matches expectation")

    # Dataset breakdown
    print(f"\n5. HOMA-eligible by dataset:")
    eligible_by_source = df[df.homa_analysis_eligible].groupby("dataset_source").size()
    print(eligible_by_source.to_string())

    print("\n" + "=" * 70)
    if len(chns) > 9500 and len(chns_eligible) > 9400 and total_eligible > 18000:
        print("✅ ALL VALIDATION CHECKS PASSED")
    else:
        print("⚠️ SOME CHECKS FAILED - REVIEW ABOVE")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
