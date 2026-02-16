#!/usr/bin/env python3
"""
KiHealth Pipeline UI — Run the pipeline and see results without zips or command line.

Stages:
  0. M1 Deliverables — What was in the M1 zip (docs, code, data)
  1. M1 Overview — Transfer learning data stats and examples
  2. Data Prep — Cliff's file → CSV
  3. Run Predictions — Execute pipeline
  4. Results — Summary and downloadable predictions
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Project root (parent of kihealth_ui)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

M1_DOCS = PROJECT_ROOT / "deliverables" / "M1_clean" / "docs"
if not M1_DOCS.exists():
    M1_DOCS = PROJECT_ROOT / "deliverables" / "M1" / "docs"
M1_README = PROJECT_ROOT / "deliverables" / "M1_clean" / "README.md"
if not M1_README.exists():
    M1_README = PROJECT_ROOT / "deliverables" / "M1" / "README.md"

UNIFIED_CSV = PROJECT_ROOT / "data" / "processed" / "unified_kihealth.csv"
KIHEALTH_TSV = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "kihealth_patients_raw.tsv"
CLIFF_TSV = PROJECT_ROOT / "Diabetes-KiHealth" / "Cliff-Modified-Table-1.tsv"
KIHEALTH_CSV = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "kihealth_patients.csv"
PREDICTIONS_CSV = PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth" / "kihealth_predictions.csv"


def get_unified_stats():
    """Load unified_kihealth.csv and return live stats, or None if missing."""
    if not UNIFIED_CSV.exists():
        return None
    try:
        df = pd.read_csv(UNIFIED_CSV, low_memory=False)
    except Exception:
        return None
    homa_col = df.get("homa_analysis_eligible", pd.Series(dtype=bool))
    homa_eligible = homa_col.fillna(False)
    invalid = df.get("invalid_homa_flag", pd.Series(dtype=bool)).fillna(True)
    glu = df.get("glucose_mg_dl", pd.Series(dtype=float))
    ins = df.get("insulin_uU_ml", pd.Series(dtype=float))
    train_mask = (
        homa_eligible
        & ~invalid
        & glu.notna()
        & (glu > 0)
        & ins.notna()
        & (ins > 0)
    )
    diabetic = df.get("diabetes_status", pd.Series(dtype=float)).fillna(0) == 1
    by_source = df.get("dataset_source", pd.Series()).value_counts()
    key_vars = ["glucose_mg_dl", "insulin_uU_ml", "hba1c_percent"]
    present = sum(df.get(c, pd.Series()).notna().sum() for c in key_vars)
    total_cells = len(df) * len(key_vars)
    missing_pct = 100.0 * (1 - present / total_cells) if total_cells else 0
    return {
        "total": len(df),
        "homa_eligible": int(homa_eligible.sum()),
        "training_count": int(train_mask.sum()),
        "diabetes_cases": int(diabetic.sum()),
        "n_vars": len(df.columns),
        "by_source": by_source,
        "missing_pct": missing_pct,
    }


st.set_page_config(
    page_title="KiHealth Pipeline",
    page_icon="📊",
    layout="wide",
)

st.title("KiHealth Pipeline")
st.caption("Run the transfer-learning pipeline and view results — no zip files or command line required.")

# Sidebar: stage selector
stage = st.sidebar.radio(
    "Stage",
    ["0. M1 Deliverables", "1. M1 Overview", "2. Data Prep", "3. Run Predictions", "4. Results"],
    index=0,
)

# --- Stage 0: M1 Deliverables (what was in the M1 zip) ---
if stage == "0. M1 Deliverables":
    st.header("M1 Package Contents")
    st.markdown("""
    This is what would be seen in the **M1 zip**: documentation, data overview, code structure, and presentation.
    **Numbers below reflect the current dataset** when the unified CSV is present.
    """)

    stats = get_unified_stats()
    if stats:
        col_head, col_btn = st.columns([5, 1])
        with col_head:
            st.subheader("Current dataset (live)")
        with col_btn:
            if st.button("Refresh data", help="Re-read unified_kihealth.csv and update the numbers below"):
                st.rerun()
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total samples", f"{stats['total']:,}")
        with c2:
            st.metric("HOMA-eligible", f"{stats['homa_eligible']:,}")
        with c3:
            st.metric("Used for training", f"{stats['training_count']:,}")
        with c4:
            st.metric("Diabetes cases", f"{stats['diabetes_cases']:,}")
        with c5:
            pct = 100 * stats["diabetes_cases"] / max(1, stats["total"])
            st.metric("Diabetes %", f"{pct:.1f}%")
        st.caption(f"Variables: {stats['n_vars']} · Key-variable missing: ~{stats['missing_pct']:.1f}%")
        if not stats["by_source"].empty:
            st.markdown("**By source**")
            st.dataframe(
                stats["by_source"].rename("samples").to_frame(),
                use_container_width=True,
                height=min(250, 50 + 30 * len(stats["by_source"])),
            )
    else:
        st.info("Unified dataset not found. Current stats will appear here once `data/processed/unified_kihealth.csv` exists (see Stage 1).")

    with st.expander("Run the pipeline", expanded=False):
        st.markdown("Data Prep → Use Cliff's File & Convert; Run Predictions → Run Pipeline; Results → download CSV.")

    if M1_README.exists():
        with st.expander("M1 README (as delivered)", expanded=False):
            st.caption("Numbers in the README below are from the M1 delivery; for current numbers see **Current dataset (live)** above.")
            st.markdown(M1_README.read_text(encoding="utf-8", errors="replace"))
    else:
        st.info("M1 README not found in deliverables. Using in-repo docs if available.")

    st.subheader("Documentation")
    doc_list = [
        ("KiHealth_Data_Summary.md", "Data overview and schema"),
        ("M1_Data_Quality_Report.md", "Quality analysis"),
        ("PHASE1_ASSESSMENT.md", "Phase 1 completion"),
        ("HOMA_Calculations.md", "HOMA-IR / HOMA-beta formulas"),
        ("CHNS_Transfer_Learning_Assessment.md", "CHNS dataset"),
        ("Project_Setup.md", "Environment setup"),
        ("HIPAA_Deidentification_Protocol.md", "HIPAA – de-identification"),
        ("Access_Control_Policy.md", "HIPAA – access control"),
        ("Data_Retention_Policy.md", "HIPAA – retention"),
        ("Incident_Response_Plan.md", "HIPAA – incident response"),
        ("M1_Presentation_Update_Notes_CHNS.md", "Presentation update notes"),
    ]
    for filename, desc in doc_list:
        path = M1_DOCS / filename
        if path.exists():
            with st.expander(f"**{filename}** — {desc}"):
                st.markdown(path.read_text(encoding="utf-8", errors="replace"))
        else:
            st.caption(f"*{filename}* — not found")

    st.subheader("Other M1 contents")
    st.markdown("""
    - **Data:** `unified_kihealth.csv` — see **Current dataset (live)** above and Stage 1 for a sample.
    - **Code:** `load_kihealth.py`, `homa_calculations.py`, scripts (merge CHNS, download DIQ, validate).
    - **Presentation:** M1_Presentation.pptx (in deliverables folder; open locally).
    """)

# --- Stage 1: M1 Overview ---
elif stage == "1. M1 Overview":
    st.header("Stage 1: M1 Transfer Learning Data")
    stats = get_unified_stats()
    if stats:
        st.markdown(f"""
        Foundation dataset: **{stats['total']:,} samples** from NHANES (USA) and CHNS (China) teach the model 
        universal metabolic patterns. **{stats['training_count']:,}** are used for training (HOMA-eligible, valid glucose/insulin).
        This size prevents overfitting when we apply the model to KiHealth's cohort.

        **NHANES** + **CHNS** (and optionally C-Pep NHANES) provide fasting glucose, insulin, HbA1c, 
        and derived HOMA indices.
        """)
    else:
        st.markdown("""
        Foundation dataset from NHANES (USA) and CHNS (China) provides fasting glucose, insulin, HbA1c, 
        and derived HOMA indices. Load the unified CSV to see current counts.
        """)

    if UNIFIED_CSV.exists():
        df = pd.read_csv(UNIFIED_CSV, low_memory=False)
        homa_eligible = df.get("homa_analysis_eligible", pd.Series(dtype=bool)).fillna(False)
        diabetic = df.get("diabetes_status", pd.Series(dtype=float)).fillna(0) == 1

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total rows", f"{len(df):,}")
        with c2:
            st.metric("HOMA-eligible", f"{homa_eligible.sum():,}")
        with c3:
            st.metric("Diabetes cases", f"{diabetic.sum():,}")
        with c4:
            pct = 100 * diabetic.sum() / max(1, len(df))
            st.metric("Diabetes %", f"{pct:.1f}%")

        st.subheader("Example rows (first 5)")
        cols = [c for c in df.columns if c in ["age_years", "sex", "bmi_kg_m2", "glucose_mg_dl", "insulin_uU_ml", "hba1c_percent", "homa_ir", "homa_beta", "diabetes_status", "dataset_source"]]
        display_df = df[cols] if cols else df
        st.dataframe(display_df.head(), use_container_width=True)
    else:
        st.warning(f"Unified dataset not found at `{UNIFIED_CSV}`. Run data preparation first.")

# --- Stage 2: Data Prep ---
elif stage == "2. Data Prep":
    st.header("Stage 2: Patient Data Preparation")
    st.markdown("""
    Convert Cliff-Modified-Table-1.tsv to CSV for the prediction pipeline.
    """)

    if CLIFF_TSV.exists():
        st.success(f"Found `{CLIFF_TSV.name}` (160 patients)")
        df = pd.read_csv(CLIFF_TSV, sep="\t", dtype=str)
        st.metric("Patients", len(df))
        st.subheader("Preview (first 10 rows, key columns)")
        key_cols = [c for c in df.columns if c in ["Donor ID", "A1c", "Insulin", "C-peptide", "BMI", "Glucose (mg/dL)", "Age (as of Aug 2025)"]]
        st.dataframe(df[key_cols].head(10) if key_cols else df.head(10), use_container_width=True)
        if st.button("Use Cliff's File & Convert"):
            shutil.copy(CLIFF_TSV, KIHEALTH_TSV)
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "tsv_to_csv_kihealth.py")],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                st.success("Cliff's file loaded and converted. Run predictions in Stage 3.")
            else:
                st.error(result.stderr or result.stdout)
    else:
        st.warning(f"`{CLIFF_TSV.name}` not found in Diabetes-KiHealth/.")

# --- Stage 3: Run Predictions ---
elif stage == "3. Run Predictions":
    st.header("Stage 3: Run Predictions")
    stats = get_unified_stats()
    train_n = f"{stats['training_count']:,}" if stats else "the foundation dataset"
    st.markdown(f"""
    **Transfer learning:** Model learns from **{train_n} HOMA-eligible samples**, then applies this 
    knowledge to predict diabetes risk for your patients based on their C-Peptide, HbA1c, and 
    Insulin levels.

    Execute the pipeline below.
    """)

    if not UNIFIED_CSV.exists():
        st.error("Unified dataset not found. Cannot run predictions.")
    elif not KIHEALTH_CSV.exists():
        st.error("KiHealth patient CSV not found. Run Data Prep first.")
    else:
        if st.button("Run Pipeline"):
            with st.spinner("Running pipeline (may take 10–30 seconds)..."):
                result = subprocess.run(
                    [sys.executable, str(PROJECT_ROOT / "scripts" / "kihealth_diabetes_prediction.py")],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            if result.returncode == 0:
                st.success("Pipeline completed successfully.")
                st.code(result.stdout, language="text")
            else:
                st.error("Pipeline failed.")
                st.code(result.stderr or result.stdout, language="text")
        else:
            st.info("Click 'Run Pipeline' to execute the prediction script.")

# --- Stage 4: Results ---
elif stage == "4. Results":
    st.header("Stage 4: Results")
    st.markdown("View prediction summary and download the full results.")

    if PREDICTIONS_CSV.exists():
        df = pd.read_csv(PREDICTIONS_CSV)

        st.subheader("Summary")
        if "predicted_diabetes_label" in df.columns:
            counts = df["predicted_diabetes_label"].value_counts()
            c1, c2, c3 = st.columns(3)
            for i, (label, n) in enumerate(counts.items()):
                with [c1, c2, c3][i % 3]:
                    st.metric(label, int(n))

        if "risk_tier" in df.columns:
            st.subheader("Risk Tier Distribution")
            st.bar_chart(df["risk_tier"].value_counts())

            st.subheader("Risk Tier Recommendations")
            tier_counts = df["risk_tier"].value_counts()
            if "High risk" in tier_counts.index:
                n = int(tier_counts["High risk"])
                st.markdown(f"- **High risk** ({n} patient{'s' if n != 1 else ''}): Immediate intervention, lifestyle counseling")
            if "Moderate risk" in tier_counts.index:
                n = int(tier_counts["Moderate risk"])
                st.markdown(f"- **Moderate risk** ({n} patient{'s' if n != 1 else ''}): Monitor closely, preventive measures")
            if "Low risk" in tier_counts.index:
                n = int(tier_counts["Low risk"])
                st.markdown(f"- **Low risk** ({n} patient{'s' if n != 1 else ''}): Standard care, annual checkup")
            if "Elevated (model)" in tier_counts.index:
                n = int(tier_counts["Elevated (model)"])
                st.markdown(f"- **Elevated (model)** ({n} patient{'s' if n != 1 else ''}): Consider follow-up screening")

        st.subheader("Sample results (first 15)")
        result_cols = [c for c in df.columns if c in ["Donor ID", "A1c", "Insulin", "BMI", "predicted_diabetes_label", "risk_tier", "kihealth_at_risk_flags", "predicted_diabetes_risk_pct"]]
        st.dataframe(df[result_cols].head(15) if result_cols else df.head(15), use_container_width=True)
        st.caption("Risk %: Diabetic = 99.9; Prediabetic = — (ADA criteria, not model); Non-diabetic = model’s P(diabetes) on 0–100 scale.")

        st.download_button(
            "Download full predictions (CSV)",
            df.to_csv(index=False),
            file_name="kihealth_predictions.csv",
            mime="text/csv",
        )
    else:
        st.warning("No predictions yet. Run the pipeline in Stage 3 first.")
