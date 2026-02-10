# Deploying the KiHealth Pipeline for KiHealth to Review

Three ways to let Clifford (or KiHealth) review the pipeline and UI.

---

## Option 1: You run it and share (fastest)

You run the app on your machine and give them access:

1. **From project root:**
   ```bash
   pip install streamlit pandas
   streamlit run kihealth_ui/app.py
   ```
2. **Share your screen** (Zoom/Teams) and walk through Stages 0–4, or  
3. **Expose your local app with a tunnel** so they can open it in their browser:
   - Install [ngrok](https://ngrok.com) or use `streamlit run kihealth_ui/app.py --server.headless true` and then e.g. `ngrok http 8501`
   - Send them the ngrok URL (e.g. `https://abc123.ngrok.io`). They open it; no install on their side.

**Requirements on your machine:** `data/processed/unified_kihealth.csv` and `Diabetes-KiHealth/Cliff-Modified-Table-1.tsv` (or your copy of the repo with data).

---

## Option 2: KiHealth runs it locally

They clone the repo and run the app on their machine.

1. **Clone the repo** (or download ZIP and unzip).
2. **Ensure data is present:**
   - `data/processed/unified_kihealth.csv` (unified training data)
   - `Diabetes-KiHealth/Cliff-Modified-Table-1.tsv` (patient list)
   If the repo doesn’t include the CSV (e.g. too large for Git), you send it separately and they put it in `data/processed/`.
3. **From project root:**
   ```bash
   pip install -r kihealth_ui/requirements.txt
   streamlit run kihealth_ui/app.py
   ```
4. Browser opens at `http://localhost:8501`. They use Stages 0–4 as in the UI.

**Requirements:** Python 3.9+, and the two files above.

---

## Option 3: Deploy to a host (they get a URL)

Deploy so they can open a link from anywhere, without cloning or running commands.

### Streamlit Community Cloud (free)

1. **Push the project to GitHub** (if not already).
2. **Include what the app needs** in the repo:
   - `kihealth_ui/`, `scripts/`, `src/`, `deliverables/M1_clean/` (or `M1/`), `Diabetes-KiHealth/Cliff-Modified-Table-1.tsv`.
   - **Critical:** `data/processed/unified_kihealth.csv`. If it’s too large for GitHub (e.g. &gt;100 MB), either:
     - Use [Git LFS](https://git-lfs.com) for that file, or  
     - Add a smaller “demo” CSV (e.g. 5k rows) as `unified_kihealth.csv` so the app and pipeline still run (with a note in the UI that it’s a sample).
3. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, **New app**.
4. **Repository:** `your-org/KiHealth-Project-1` (or your repo name).  
   **Branch:** `main`.  
   **Main file path:** `kihealth_ui/app.py`.  
   **Advanced:** Add Python 3.9+ in a `runtime.txt` if needed.
5. Deploy. Streamlit gives you a URL like `https://your-app.streamlit.app`. Share that with KiHealth.

**Note:** The app runs from the repo root; all paths in the app are relative to that. No env vars are required unless you add them later.

### Other hosts (Railway, Heroku, etc.)

Same idea: point the service at the repo, set the start command to:

```bash
pip install -r kihealth_ui/requirements.txt && streamlit run kihealth_ui/app.py --server.port $PORT --server.address 0.0.0.0
```

Use `$PORT` (or the host’s port env) and ensure the repo (or build) contains the same files as above.

---

## What KiHealth can do in the UI

- **Stage 0:** M1 package contents, current dataset stats, doc expanders.  
- **Stage 1:** Transfer learning data overview and sample rows.  
- **Stage 2:** Use Cliff’s file and convert TSV → CSV.  
- **Stage 3:** Run the prediction pipeline (train on unified data, predict for patients).  
- **Stage 4:** View summary, risk tiers, sample table, and **download the full predictions CSV**.

No zip files or command line required for them once the app is running or the URL is shared.
