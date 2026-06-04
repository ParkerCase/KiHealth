# Deploy the KiHealth UI so KiHealth can use it

Two ways to give KiHealth a link they can open. Pick one.

---

## Option A: You run it + share a link (no data in GitHub)

**Best if:** You’re okay leaving the app running (or starting it for demos) and your machine has the data.

1. **On your machine** (with the full project and `data/processed/unified_kihealth.csv`):
   ```bash
   cd /path/to/KiHealth-Project-1   # or clone of KiHealth repo + add the CSV
   pip install streamlit pandas xgboost
   streamlit run kihealth_ui/app.py
   ```
2. **Expose it with a tunnel** so they can open it in a browser:
   - Install [ngrok](https://ngrok.com/download) (or `brew install ngrok`).
   - In another terminal: `ngrok http 8501`
   - Copy the HTTPS URL ngrok shows (e.g. `https://abc123.ngrok-free.app`).
3. **Send that URL to KiHealth.** They open it; no install for them.  
   The link works as long as your Streamlit app and ngrok are running.

**Pros:** Uses your real data; no need to put CSV in GitHub.  
**Cons:** They can only use it when you (or someone) has the app + ngrok running.

---

## Option B: Deploy to Streamlit Community Cloud (always-on URL)

**Best if:** You want a permanent link (e.g. `https://yourapp.streamlit.app`) that works without your laptop.

The app needs **`data/processed/unified_kihealth.csv`** in the repo for “Current dataset”, Stage 1, and Run Predictions to work. The KiHealth repo doesn’t have it yet (folder is gitignored). Add it once, then deploy:

### 1. Add the unified CSV to the KiHealth repo (one-time)

From your **KiHealth-Project-1** folder (or a clone of the KiHealth repo that has the CSV locally):

```bash
# Create the directory in the repo (if needed)
mkdir -p data/processed

# Copy the unified CSV into it (use your actual path to the file)
cp /path/to/unified_kihealth.csv data/processed/

# Force-add (data/ is usually gitignored)
git add -f data/processed/unified_kihealth.csv
git commit -m "Add unified_kihealth.csv for Streamlit Cloud deployment"
git push kihealth main
```

If your repo is the one that already has the file at `data/processed/unified_kihealth.csv`, you only need to force-add and push:

```bash
git add -f data/processed/unified_kihealth.csv
git commit -m "Add unified_kihealth.csv for Streamlit Cloud deployment"
git push kihealth main
```

### 2. Deploy on Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
2. Click **“New app”**.
3. Set:
   - **Repository:** `ParkerCase/KiHealth`
   - **Branch:** `main`
   - **Main file path:** `kihealth_ui/app.py`
4. Click **“Deploy”**. Wait a few minutes.
5. You’ll get a URL like `https://yourapp-name-xxxx.streamlit.app`. Send that to KiHealth.

**Root requirements:** So the app (and the pipeline when they click “Run Pipeline”) can run, the repo should have a **root** `requirements.txt` that includes everything the app and scripts need. Create one if it doesn’t exist:

```txt
streamlit>=1.28.0
pandas>=1.5.0
xgboost>=1.6.0
```

Save as `requirements.txt` in the **root** of the KiHealth repo, commit, and push. Streamlit Cloud uses the repo root as the working directory.

**Pros:** Always-on URL; KiHealth can use it anytime.  
**Cons:** You have to add the CSV to the repo once (and optionally a root `requirements.txt`).

---

## What KiHealth can do in the UI

- **Stage 0:** M1 package contents, live dataset stats (if CSV is present), doc expanders, “Run the pipeline” steps.
- **Stage 1:** Transfer learning data overview and sample rows (if CSV is present).
- **Stage 2:** Use Cliff’s file and convert TSV → CSV.
- **Stage 3:** Run the prediction pipeline (needs unified CSV + KiHealth CSV from Stage 2).
- **Stage 4:** View summary, risk tiers, sample table, and download the full predictions CSV.

Without `unified_kihealth.csv` in the repo (Option A without the CSV, or Option B before adding it), Stages 0 and 1 show a “dataset not found” message and Stage 3 can’t run; Stage 2 and the doc expanders still work.
