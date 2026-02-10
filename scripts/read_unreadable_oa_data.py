#!/usr/bin/env python3
"""
Try to read the .sav and .por files that pyreadstat could not read, and export
them so you can view them.

Methods tried (in order):
  1. R + haven – if R is installed with haven, reads .sav/.por and writes CSV.
  2. If R is not available, generates SPSS syntax and instructions so you can
     open and export the files in SPSS.

Usage:
  python scripts/read_unreadable_oa_data.py

Outputs (when R is used):
  data/New-OA-Data/extracted/sav/   – CSV + variable list for each unreadable .sav
  data/New-OA-Data/extracted/por/   – CSV for the CHECK .por (if read)
"""

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA_ROOT = BASE / "data" / "New-OA-Data"
OUT = DATA_ROOT / "extracted"
KLOSA_SPSS = DATA_ROOT / "KLoSa" / "KLoSA 1-9th wave (SPSS)"
CHECK_DIR = DATA_ROOT / "CHECK"

# Files that pyreadstat could not read (relative to DATA_ROOT)
UNREADABLE_SAV = [
    f"KLoSa/KLoSA 1-9th wave (SPSS)/{f}"
    for f in [
        "Lt01_e.sav", "Lt02_e.sav", "Lt03_e.sav", "Lt04_e.sav", "Lt05_e.sav",
        "Lt06_e.sav", "Lt07_e.sav", "Lt08_e.sav",
        "str01_e.sav", "str02_e.sav", "str03_e.sav", "str04_e.sav",
        "str05_e.sav", "str06_e.sav", "str07_e.sav", "str08_e.sav",
        "w01_e.sav", "w02_e.sav", "w03_e.sav", "w04_e.sav", "w05_e.sav",
        "w05_new_e.sav", "w06_e.sav", "w07_e.sav", "w08_e.sav",
    ]
]
UNREADABLE_POR = ["CHECK/CHECK_Radiographic_Scoring_OA_T0T2T5T8T10_DANS_nsinENG_20170726.por"]


def try_r_export():
    """Use R + haven to read .sav/.por and write CSV. Returns True if R worked."""
    r_script = """
list_of_sav <- c(
  "Lt01_e", "Lt02_e", "Lt03_e", "Lt04_e", "Lt05_e", "Lt06_e", "Lt07_e", "Lt08_e",
  "str01_e", "str02_e", "str03_e", "str04_e", "str05_e", "str06_e", "str07_e", "str08_e",
  "w01_e", "w02_e", "w03_e", "w04_e", "w05_e", "w05_new_e", "w06_e", "w07_e", "w08_e"
)
base_dir <- Sys.getenv("DATA_ROOT")
out_sav <- file.path(base_dir, "extracted", "sav_from_r")
out_por <- file.path(base_dir, "extracted", "por_from_r")
dir.create(out_sav, recursive = TRUE, showWarnings = FALSE)
dir.create(out_por, recursive = TRUE, showWarnings = FALSE)
spss_dir <- file.path(base_dir, "KLoSa", "KLoSA 1-9th wave (SPSS)")
if (!requireNamespace("haven", quietly = TRUE)) {
  message("R package 'haven' is not installed. Install with: install.packages('haven')")
  quit(save = "no", status = 1)
}
for (stem in list_of_sav) {
  f <- file.path(spss_dir, paste0(stem, ".sav"))
  if (!file.exists(f)) next
  out_csv <- file.path(out_sav, paste0(stem, ".csv"))
  out_vars <- file.path(out_sav, paste0(stem, "_variables.txt"))
  tryCatch({
    d <- haven::read_sav(f)
    write.csv(d, out_csv, row.names = FALSE)
    writeLines(names(d), out_vars)
    message("OK: ", stem)
  }, error = function(e) message("FAIL ", stem, ": ", conditionMessage(e)))
}
por_file <- file.path(base_dir, "CHECK", "CHECK_Radiographic_Scoring_OA_T0T2T5T8T10_DANS_nsinENG_20170726.por")
if (file.exists(por_file)) {
  tryCatch({
    d <- haven::read_por(por_file)
    out_csv <- file.path(out_por, "CHECK_Radiographic_OA_T0T2T5T8T10.csv")
    write.csv(d, out_csv, row.names = FALSE)
    writeLines(names(d), file.path(out_por, "CHECK_Radiographic_variables.txt"))
    message("OK: CHECK radiographic .por")
  }, error = function(e) message("FAIL .por: ", conditionMessage(e)))
}
message("R export done.")
"""
    env = {**subprocess.os.environ, "DATA_ROOT": str(DATA_ROOT)}
    try:
        r = subprocess.run(
            ["Rscript", "-e", r_script],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(BASE),
            env=env,
        )
        if r.returncode == 0:
            print(r.stdout)
            return True
        print("R script failed:", r.returncode, r.stderr or r.stdout)
        return False
    except FileNotFoundError:
        print("Rscript not found. Install R from https://cran.r-project.org/ and ensure Rscript is on PATH.")
        return False
    except subprocess.TimeoutExpired:
        print("R script timed out.")
        return False


def write_spss_syntax():
    """Write SPSS .sps file so user can open unreadable files in SPSS and save as CSV."""
    sps_path = DATA_ROOT / "EXPORT_UNREADABLE_FILES.sps"
    out_csv_dir = OUT / "sav_from_spss"
    out_por_dir = OUT / "por_from_spss"
    lines = [
        "* SPSS syntax to export the .sav and .por files that Python could not read.",
        "* Run this in SPSS: File -> Open -> Syntax, open this file, then Run -> All.",
        "* CSV files are written to: extracted/sav_from_spss/ and extracted/por_from_spss/",
        "* Edit the paths below if you need different output locations.",
        "",
        "SET UNICODE ON.",
        ""
    ]
    out_csv_dir.mkdir(parents=True, exist_ok=True)
    out_por_dir.mkdir(parents=True, exist_ok=True)
    for rel in UNREADABLE_SAV:
        full = DATA_ROOT / rel
        if not full.exists():
            continue
        stem = full.stem
        csv_path = out_csv_dir / f"{stem}.csv"
        lines.append(f"* {rel}")
        lines.append(f"GET FILE='{full.as_posix()}'.")
        lines.append(f"SAVE TRANSLATE OUTFILE='{csv_path.as_posix()}' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES /REPLACE.")
        lines.append("")
    lines.append("* CHECK radiographic .por")
    por_full = DATA_ROOT / UNREADABLE_POR[0]
    if por_full.exists():
        csv_por = out_por_dir / "CHECK_Radiographic_OA_T0T2T5T8T10.csv"
        lines.append(f"GET FILE='{por_full.as_posix()}'.")
        lines.append(f"SAVE TRANSLATE OUTFILE='{csv_por.as_posix()}' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES /REPLACE.")
    sps_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote SPSS syntax: {sps_path}")
    return sps_path


def write_readme():
    """Write README for unreadable files."""
    readme_path = DATA_ROOT / "README_UNREADABLE_FILES.md"
    content = """# Viewing the Unreadable .sav and .por Files

These files could not be read by the Python script (pyreadstat):

- **25 KLoSA .sav files** (Lt01–Lt08, str01–str08, w01–w08, w05_new_e)
- **1 CHECK .por file** (radiographic scoring)

## Option 1: Use R (recommended if you have R)

1. Install R from https://cran.r-project.org/
2. In R, install the `haven` package: `install.packages("haven")`
3. From the **project root** (DOC), run:

   ```bash
   export DATA_ROOT="$(pwd)/data/New-OA-Data"
   Rscript scripts/run_r_export_unreadable.R
   ```

   Or run the Python helper (it will call R if available):

   ```bash
   python scripts/read_unreadable_oa_data.py
   ```

   If R + haven succeed, CSVs and variable lists appear in:
   - `data/New-OA-Data/extracted/sav_from_r/` (KLoSA .sav)
   - `data/New-OA-Data/extracted/por_from_r/` (CHECK .por)

## Option 2: Use SPSS

1. Open **SPSS**.
2. File → Open → Syntax.
3. Open `data/New-OA-Data/EXPORT_UNREADABLE_FILES.sps`.
4. Run → All.

The syntax opens each unreadable .sav and the .por file and exports them as CSV to:
- `data/New-OA-Data/extracted/sav_from_spss/` (KLoSA .sav)
- `data/New-OA-Data/extracted/por_from_spss/` (CHECK .por)

On Windows, you may need to edit the .sps file and change the paths to use backslashes.

## Option 3: Open manually in SPSS

- **KLoSA .sav:** `data/New-OA-Data/KLoSa/KLoSA 1-9th wave (SPSS)/`  
  Open any of: Lt01_e.sav … Lt08_e.sav, str01_e.sav … str08_e.sav, w01_e.sav … w08_e.sav, w05_new_e.sav.
- **CHECK .por:** `data/New-OA-Data/CHECK/CHECK_Radiographic_Scoring_OA_T0T2T5T8T10_DANS_nsinENG_20170726.por`  
  In SPSS: File → Open → Data, choose file type “SPSS Portable (*.por)” and select this file. Then File → Save As → CSV.
"""
    readme_path.write_text(content, encoding="utf-8")
    print(f"Wrote: {readme_path}")
    return readme_path


def main():
    print("Attempting to read unreadable .sav and .por files...")
    print()

    # 1. Try R + haven
    if try_r_export():
        print("\nR export completed. Check extracted/sav_from_r/ and extracted/por_from_r/.")
        return

    # 2. Generate SPSS syntax and README
    print("\nR not available or export failed. Generating SPSS syntax and README.")
    write_spss_syntax()
    write_readme()
    print("\nNext steps:")
    print("  1. Install R and haven, then run this script again; or")
    print("  2. Open EXPORT_UNREADABLE_FILES.sps in SPSS and Run All; or")
    print("  3. Open each file manually in SPSS and export as CSV.")
    print("  See README_UNREADABLE_FILES.md for details.")


if __name__ == "__main__":
    main()
