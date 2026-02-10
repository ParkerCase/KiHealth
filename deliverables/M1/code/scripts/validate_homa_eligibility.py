"""Validate HOMA analysis eligibility flagging."""
import pandas as pd

df = pd.read_csv("data/processed/kihealth_unified.csv")

print("=" * 70)
print("HOMA ANALYSIS ELIGIBILITY VALIDATION")
print("=" * 70)

# Check all columns exist
required = [
    "dataset_source",
    "homa_analysis_eligible",
    "invalid_homa_flag",
    "homa_ir",
    "homa_beta",
]
missing = [c for c in required if c not in df.columns]
if missing:
    print(f"\n❌ ERROR: Missing columns: {missing}")
    exit(1)
else:
    print("\n✅ All required columns present")

# Check eligibility by dataset
print("\n" + "=" * 70)
print("HOMA Eligibility by Dataset:")
print("=" * 70)
for source in df.dataset_source.unique():
    data = df[df.dataset_source == source]
    eligible = data.homa_analysis_eligible.sum()
    total = len(data)
    pct = 100 * eligible / total if total else 0
    print(f"{source:20s} {int(eligible):5d} / {total:5d} ({pct:5.1f}%)")

# Verify Frankfurt = 0 eligible
frankfurt_eligible = df[df.dataset_source == "frankfurt"].homa_analysis_eligible.sum()
if frankfurt_eligible > 0:
    print(f"\n❌ ERROR: Frankfurt has {frankfurt_eligible} eligible samples (should be 0)")
else:
    print("\n✅ Frankfurt correctly excluded (0 eligible)")

# Verify DiaBD = 0 eligible
diabd_eligible = df[df.dataset_source == "diabd"].homa_analysis_eligible.sum()
if diabd_eligible > 0:
    print(f"❌ ERROR: DiaBD has {diabd_eligible} eligible samples (should be 0)")
else:
    print("✅ DiaBD correctly excluded (0 eligible)")

# Verify NHANES = all eligible
nhanes = df[df.dataset_source.str.startswith("nhanes")]
nhanes_eligible = nhanes.homa_analysis_eligible.sum()
if nhanes_eligible != len(nhanes):
    print(f"❌ ERROR: NHANES has {nhanes_eligible}/{len(nhanes)} eligible (should be all)")
else:
    print(f"✅ NHANES correctly included ({int(nhanes_eligible)} eligible)")

# Summary statistics
print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)
total_eligible = df.homa_analysis_eligible.sum()
print(f"Total HOMA-eligible samples: {int(total_eligible)}")
print("Expected: 9,086 (NHANES only)")

if total_eligible == 9086:
    print("\n✅ ALL VALIDATION CHECKS PASSED")
else:
    print(f"\n❌ VALIDATION FAILED: Expected 9,086, got {int(total_eligible)}")

print("=" * 70)
