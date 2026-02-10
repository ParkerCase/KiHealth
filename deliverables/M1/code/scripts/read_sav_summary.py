#!/usr/bin/env python3
"""
One-off: read an SPSS .sav file and print structure + sample.
Requires: pip install pyreadstat
Usage: python scripts/read_sav_summary.py
"""
import sys
from pathlib import Path

try:
    import pyreadstat
except ImportError:
    print("Install pyreadstat first: pip install pyreadstat")
    sys.exit(1)

SAV_PATH = Path(__file__).resolve().parents[1] / "data" / "New-OA-Data" / "CHECK_T0_DANS_nsin_ENG_20161128.sav"

def main():
    if not SAV_PATH.exists():
        print(f"File not found: {SAV_PATH}")
        sys.exit(1)
    df, meta = pyreadstat.read_sav(str(SAV_PATH))
    print("=== FILE FOUND ===\n")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}\n")
    print("=== COLUMN NAMES & TYPES ===\n")
    for c in df.columns:
        print(f"  {c!r}  {df[c].dtype}")
    print("\n=== LABEL (if any) ===\n")
    if meta.column_names_to_labels:
        for name, label in list(meta.column_names_to_labels.items())[:20]:
            print(f"  {name!r} -> {label}")
        if len(meta.column_names_to_labels) > 20:
            print(f"  ... and {len(meta.column_names_to_labels) - 20} more")
    print("\n=== FIRST 5 ROWS (all columns) ===\n")
    print(df.head().to_string())
    print("\n=== VALUE COUNTS FOR FIRST 10 COLUMNS ===\n")
    for c in list(df.columns)[:10]:
        vc = df[c].value_counts(dropna=False)
        print(f"{c!r}: {len(vc)} distinct values; sample: {dict(vc.head(3))}")
    # Optional: write CSV for full inspection
    out_csv = SAV_PATH.with_suffix(".csv")
    df.to_csv(out_csv, index=False)
    print(f"\n=== EXPORTED FULL DATA TO ===\n  {out_csv}")

if __name__ == "__main__":
    main()
