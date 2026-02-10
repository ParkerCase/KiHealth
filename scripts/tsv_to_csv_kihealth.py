#!/usr/bin/env python3
"""
Convert KiHealth TSV to CSV and save as kihealth_patients.csv.
Reads from Diabetes-KiHealth/TL-KiHealth/kihealth_patients_raw.tsv
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TSV_PATH = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "kihealth_patients_raw.tsv"
CSV_PATH = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "kihealth_patients.csv"


def main() -> None:
    # Read with padding: short rows get right-padded so left columns align with header
    with open(TSV_PATH) as f:
        lines = f.readlines()
    if not lines:
        return
    header = lines[0].rstrip().split("\t")
    n_cols = len(header)
    rows = []
    for line in lines[1:]:
        parts = line.rstrip().split("\t")
        if len(parts) < n_cols:
            parts = parts + [""] * (n_cols - len(parts))
        elif len(parts) > n_cols:
            parts = parts[:n_cols]
        rows.append(parts)
    df = pd.DataFrame(rows, columns=header)
    df.to_csv(CSV_PATH, index=False)
    print(f"Converted {len(df)} rows to {CSV_PATH}")


if __name__ == "__main__":
    main()
