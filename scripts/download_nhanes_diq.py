#!/usr/bin/env python3
"""
Download NHANES Diabetes Questionnaire (DIQ) files from CDC for DIQ merge.

Creates Diabetes-KiHealth/TL-KiHealth/NHANES-Diabetes/ and downloads:
- DIQ_H.xpt (2013-2014)
- DIQ_I.xpt (2015-2016)
- DIQ_J.xpt (2017-2018)
- DIQ_L.xpt (2021-2022)
Note: DIQ_K (2019-Mar2020) is not publicly available from CDC.

Run: python scripts/download_nhanes_diq.py
"""

from pathlib import Path
import urllib.request

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIQ_DIR = _PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "NHANES-Diabetes"

# DIQ files per cycle. Place in NHANES-Diabetes/ or in cycle folder (2013-14-NHANES, 2015-16-NHANES, NIHANES).
# DIQ_K (2019-Mar2020) is not publicly available.
CDC_URLS = [
    ("DIQ_H.xpt", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/DIQ_H.xpt"),
    ("DIQ_I.xpt", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/DIQ_I.xpt"),
    ("DIQ_J.xpt", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DIQ_J.xpt"),
    ("DIQ_L.xpt", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DIQ_L.xpt"),
]


def main() -> None:
    DIQ_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading NHANES DIQ files to {DIQ_DIR}\n")
    for fname, url in CDC_URLS:
        path = DIQ_DIR / fname
        try:
            urllib.request.urlretrieve(url, path)
            print(f"  ✓ {fname}")
        except Exception as e:
            print(f"  ✗ {fname}: {e}")
    print("\nDone. Re-run build_unified_kihealth() to enrich NHANES with DIQ data.")


if __name__ == "__main__":
    main()
