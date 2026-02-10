# KiHealth Pipeline UI

A simple web UI to run the KiHealth transfer-learning pipeline and view results — no zip files or command line required.

## What it does

1. **Stage 1: M1 Overview** — View transfer learning dataset stats (38k+ rows, HOMA-eligible, diabetes cases) and sample rows
2. **Stage 2: Data Prep** — Use existing patient TSV or upload new; convert TSV → CSV
3. **Stage 3: Run Predictions** — Execute the pipeline (train on 33k samples, predict for each patient)
4. **Stage 4: Results** — Summary counts, risk tier distribution, sample table, download full CSV

## Quick start

From the **project root** (KiHealth-Project-1):

```bash
# Install dependencies (if needed)
pip install streamlit pandas

# Run the UI
streamlit run kihealth_ui/app.py
```

Or use the start script (runs on port 8502 to avoid conflicting with other apps):

```bash
chmod +x kihealth_ui/START.sh
./kihealth_ui/START.sh
```

The app opens in your browser at `http://localhost:8501` (or 8502).

## Requirements

- Python 3.9+
- `data/processed/unified_kihealth.csv` must exist (from M1 data prep)
- `Diabetes-KiHealth/TL-KiHealth/kihealth_patients_raw.tsv` for existing patients (or upload via UI)

## Deploying for Clifford

**Option A: Local** — Clifford runs `streamlit run kihealth_ui/app.py` on his machine after pulling the repo.

**Option B: Deploy (remote access)** — Deploy to Streamlit Cloud, Railway, or Heroku so Clifford can access from **anywhere** (different state, home, office) via a URL. No need to pull the repo or run commands on his machine.

- **Streamlit Cloud:** Connect repo to [share.streamlit.io](https://share.streamlit.io), set app path to `kihealth_ui/app.py` → he gets a public URL
- **Railway / Heroku:** Similar idea — deploy the app, get a URL
- **Caveat:** The deployed app needs the `unified_kihealth.csv` and KiHealth data bundled or accessible (e.g. from a cloud storage bucket). For a full remote deployment, you'd need to include the data in the deploy or point to a remote data source.

**Option C: Single executable** — Package with PyInstaller for a double-click .exe (more setup).
