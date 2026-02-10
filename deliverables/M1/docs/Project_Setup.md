# Project Setup — KiHealth Diabetes M1

How to run the KiHealth Diabetes data pipeline and exploration locally.

## 1. Environment

- **Python:** 3.10+ recommended.
- **Create and activate a virtual environment:**

  ```bash
  cd /path/to/KiHealth-Project-1
  python3 -m venv .venv
  source .venv/bin/activate   # Windows: .venv\Scripts\activate
  ```

- **Install dependencies:**

  ```bash
  pip install -r requirements.txt
  ```

  Required for M1: `pandas`, `numpy`, `openpyxl` (Excel), and (for NHANES .xpt) `pyreadstat` or pandas’ built-in `read_sas`. If `read_sas` fails on .xpt, install `pyreadstat` and use it to read XPT, or use the loader’s fallback behavior.

## 2. Data paths

- **KiHealth / TL-KiHealth data:**  
  Under project root:  
  `Diabetes-KiHealth/TL-KiHealth/`

  Expected structure:
  - `Frankfurt/diabetes.csv`
  - `DiaBD/DiaBD.csv`
  - `NIHANES/*.xpt` (2017-20 and 2021-23 DEMO, GLU, INS, GHB as used by the loader)

- **Processed/output data:**  
  `data/processed/`, `data/interim/` (gitignored). Create with:

  ```bash
  mkdir -p data/processed data/interim
  ```

- **Do not commit:** Raw data (CSV, XPT, XLSX) under `Diabetes-KiHealth/` or any PHI. Use only de-identified IDs in code and logs.

## 3. Running the data loader

From the project root:

```bash
python -c "
from src.data.load_kihealth import load_frankfurt, load_diabd, load_all_kihealth_tabular
df_f = load_frankfurt()
print('Frankfurt:', df_f.shape)
datasets = load_all_kihealth_tabular()
for name, df in datasets.items():
    print(name, df.shape)
"
```

If NHANES or Frankfurt/DiaBD paths are missing, the loader logs a warning and skips that source.

## 4. HOMA calculations

```bash
python -c "
from src.features.homa_calculations import homa_ir, homa_beta, validate_homa_reference
passed, msg = validate_homa_reference(100.0, 10.0, expected_ir=100*10/405, expected_beta=360*10/37)
print(msg)
"
```

## 5. Data exploration notebook

```bash
jupyter notebook notebooks/01_KiHealth_Data_Exploration.ipynb
# or
jupyter lab notebooks/01_KiHealth_Data_Exploration.ipynb
```

Run all cells to load data, add HOMA columns, view descriptive stats, missing data, and correlations.

## 6. Tests

```bash
# From project root (so that src is importable)
pip install pytest
pytest tests/test_homa_calculations.py -v
```

## 7. Project layout (reference)

- `src/data/load_kihealth.py` — load Frankfurt, DiaBD, NHANES; merge NHANES by SEQN; quality report.
- `src/features/homa_calculations.py` — HOMA-IR, HOMA-beta, unit conversion, validation.
- `docs/KiHealth_Data_Summary.md` — data inventory and usability.
- `docs/HOMA_Calculations.md` — formulas and validation.
- `README.md` — overview and getting started.

## 8. HIPAA

- Never log or print patient names, emails, DOB, or other direct identifiers.
- Use only `patient_id`, `SEQN`, or `sample_id` in code and outputs.
- Keep raw data and any PHI out of version control.
