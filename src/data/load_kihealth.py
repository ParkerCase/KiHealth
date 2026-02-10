"""
KiHealth data loader — load and merge diabetes/HOMA-relevant data sources.

Unified schema: TIER 1 + TIER 2 variables with standardized column names.
HIPAA: Never log or print patient identifiers (names, emails, DOB).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.features.homa_calculations import add_homa_columns, homa_ir, homa_beta

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DIABETES_BASE = _PROJECT_ROOT / "Diabetes-KiHealth" / "TL-KiHealth"

# Unified schema: TIER 1 + TIER 2 (standardized names)
UNIFIED_SCHEMA = [
    "patient_id",
    "age_years",
    "sex",  # 0=Female, 1=Male
    "bmi_kg_m2",
    "glucose_mg_dl",
    "insulin_uU_ml",
    "homa_ir",
    "homa_beta",
    "diabetes_status",  # 0=No, 1=Yes
    "invalid_homa_flag",  # True if glucose<=0 or insulin<=0
    "homa_analysis_eligible",  # True = NHANES only; False = Frankfurt/DiaBD excluded from HOMA modeling
    # TIER 2
    "race_ethnicity",
    "education_level",
    "pir",
    "hba1c_percent",
    "bp_systolic_mmHg",
    "bp_diastolic_mmHg",
    "pregnancies_count",
    "diabetes_pedigree_function",
    "survey_weight",
    "survey_year",
    "dataset_source",
    # DIQ (Diabetes Questionnaire) - NHANES only; NA for other sources
    "diq_diabetes",       # Doctor told you have diabetes (1=Yes, 2=No)
    "diq_prediabetes",    # Doctor told you prediabetes (1=Yes, 2=No)
    "insulin_use",        # Now taking insulin (1=Yes, 2=No)
    "diabetes_pills",     # Now taking diabetic pills (1=Yes, 2=No)
    # C-peptide (NHANES C-Pep cycles 1999-2004 only)
    "c_peptide_ng_ml",    # Serum C-peptide, ng/mL (from LBXCPSI nmol/L * 3.02)
    "ins_cpep_ratio",     # Insulin/C-peptide ratio (μU/mL / ng/mL)
]

# NHANES RIDRETH3: 1=Mexican American, 2=Other Hispanic, 3=Non-Hispanic White, 4=Non-Hispanic Black, 5=Other, 6=Non-Hispanic Asian, 7=Other
RIDRETH3_LABELS = {
    1.0: "Mexican American",
    2.0: "Other Hispanic",
    3.0: "Non-Hispanic White",
    4.0: "Non-Hispanic Black",
    5.0: "Other/Multi-Racial",
    6.0: "Non-Hispanic Asian",
    7.0: "Other",
}

# NHANES DMDEDUC2 (adults)
DMDEDUC2_LABELS = {
    1.0: "Less than 9th grade",
    2.0: "9-11th grade",
    3.0: "High school grad/GED",
    4.0: "Some college or AA",
    5.0: "College graduate or above",
    7.0: "Refused",
    9.0: "Don't know",
}


def _empty_unified_row(dataset_source: str) -> dict[str, Any]:
    """One row of NaNs/defaults for unified schema."""
    return {c: pd.NA for c in UNIFIED_SCHEMA} | {"dataset_source": dataset_source, "invalid_homa_flag": False, "homa_analysis_eligible": False}


def load_frankfurt(base: Path | str | None = None) -> pd.DataFrame:
    """
    Load raw Frankfurt diabetes CSV (Pima Indians Diabetes Dataset).

    CRITICAL: This dataset contains 2-hour OGTT insulin, NOT fasting insulin.
    HOMA-IR/HOMA-beta are invalid for this source; all Frankfurt rows are
    flagged invalid_homa_flag=True in the unified output.
    Reference: Smith et al. (1988), UCI ML Repository; insulin = "2-Hour serum insulin (mu U/ml)".
    """
    root = Path(base) if base else _DIABETES_BASE
    path = root / "Frankfurt" / "diabetes.csv"
    if not path.exists():
        raise FileNotFoundError(f"Frankfurt data not found: {path}")
    df = pd.read_csv(path)
    logger.info("Loaded Frankfurt: %d rows", len(df))
    return df


def load_diabd(base: Path | str | None = None) -> pd.DataFrame:
    """Load raw DiaBD CSV."""
    root = Path(base) if base else _DIABETES_BASE
    path = root / "DiaBD" / "DiaBD.csv"
    if not path.exists():
        raise FileNotFoundError(f"DiaBD data not found: {path}")
    df = pd.read_csv(path)
    logger.info("Loaded DiaBD: %d rows", len(df))
    return df


def load_chns(base: Path | str | None = None) -> pd.DataFrame:
    """
    Load CHNS 2009 (China Health and Nutrition Survey) merged data.

    **Dataset:** China Health and Nutrition Survey, 2009 wave
    **Source:** UNC/NIH China Health and Nutrition Survey
    **URL:** https://www.cpc.unc.edu/projects/china

    **Measurement Protocol:**
    - Fasting blood samples (documented 8–12 hour fasting protocol)
    - 26 fasting blood measures collected
    - Participants: Adults and children age 7+
    - Certified laboratories, standardized protocols

    **Sample:** 9,549 participants from 2009 wave
    **Valid HOMA:** ~9,479 samples (99.3%)

    **Transfer Learning Value:**
    - Chinese population (different from NHANES USA)
    - Different dietary patterns and metabolic profiles
    - Tests model generalization across populations
    - Validates cross-ethnic robustness

    **Variables:** Fasting glucose (mg/dL), fasting insulin (μU/mL), HbA1c (%),
    age, sex, BMI, blood pressure.

    **Note:** CHNS data merged from biomarker_09, mast_pub_12, pexam_00
    by scripts/merge_chns_2009.py. Expects data/raw/chns/chns_2009_merged.csv.
    """
    if base is not None:
        root = Path(base)
    else:
        root = _PROJECT_ROOT / "data" / "raw"
    filepath = root / "chns" / "chns_2009_merged.csv"
    if not filepath.exists():
        raise FileNotFoundError(
            f"CHNS merged file not found: {filepath}\n"
            "Run: python scripts/merge_chns_2009.py"
        )
    df = pd.read_csv(filepath)
    df = add_homa_columns(df, "glucose_mg_dl", "insulin_uU_ml", homa_ir_col="homa_ir", homa_beta_col="homa_beta")
    invalid = (
        (df["glucose_mg_dl"].isna()) | (df["glucose_mg_dl"] <= 0)
        | (df["insulin_uU_ml"].isna()) | (df["insulin_uU_ml"] <= 0)
    )
    df["invalid_homa_flag"] = invalid
    df.loc[df["invalid_homa_flag"], ["homa_ir", "homa_beta"]] = np.nan
    df["homa_analysis_eligible"] = True
    # Diabetes: HbA1c >= 6.5% OR fasting glucose >= 126 mg/dL
    df["diabetes_status"] = (
        ((df["hba1c_percent"] >= 6.5) & df["hba1c_percent"].notna())
        | ((df["glucose_mg_dl"] >= 126) & df["glucose_mg_dl"].notna())
    ).astype(int)
    # Ensure all UNIFIED_SCHEMA columns present (merge script may use different names)
    for col in UNIFIED_SCHEMA:
        if col not in df.columns:
            df[col] = pd.NA
    logger.info("Loaded CHNS 2009: %d rows", len(df))
    return df[UNIFIED_SCHEMA]


# NHANES cycle config: folder (within TL-KiHealth) + file map. All paths relative to TL-KiHealth.
# 2013-14-NHANES, 2015-16-NHANES, NIHANES are specific folders within TL-KiHealth.
NHANES_CYCLE_CONFIG: dict[str, dict[str, Any]] = {
    "2013-14": {
        "folder": "2013-14-NHANES",
        "files": {"DEMO": "DEMO_H.xpt", "GHB": "GHB_H.xpt", "GLU": "GLU_H.xpt", "INS": "INS_H.xpt", "BMX": "BMX_H.xpt"},
        "diq": ["DIQ_H.xpt"],
    },
    "2015-16": {
        "folder": "2015-16-NHANES",
        "files": {"DEMO": "DEMO_I.xpt", "GHB": "GHB_I.xpt", "GLU": "GLU_I.xpt", "INS": "INS_I.xpt", "BMX": "BMX_I.xpt"},
        "diq": ["DIQ_I.xpt"],
    },
    "2017-20": {
        "folder": "NIHANES",
        "files": {"DEMO": "2017-20P_DEMO.xpt", "GHB": "2017-20P_GHB.xpt", "GLU": "2017-20P_GLU.xpt", "INS": "2017-20P_INS.xpt", "BMX": "2017-20P_BMX.xpt"},
        "diq": ["DIQ_J.xpt", "DIQ_K.xpt", "17-19DIQ_L.xpt"],
    },
    "2021-23": {
        "folder": "NIHANES",
        "files": {"DEMO": "2021-23DEMO_L.xpt", "GHB": "2021-23GHB_L.xpt", "GLU": "2021-23GLU_L.xpt", "INS": "2021-23INS_L (1).xpt", "BMX": "2021-23BMX_L.xpt"},
        "diq": ["DIQ_L.xpt", "21-23P_DIQ.xpt"],
    },
}

# C-Pep NHANES cycles (1999-2004): Plasma Fasting Glucose, Serum C-peptide & Insulin
# Folder: NIHANES/C-Pep/NHANES-XX-XX/; files: XX-XXDEMO*.xpt, XX-XXNHANES.xpt, XX-XXDIQ*.xpt
# No separate GHB or BMX in C-Pep folder; hba1c and bmi will be NA
NHANES_CPEP_CONFIG: dict[str, dict[str, Any]] = {
    "1999-2000": {"folder": "NIHANES/C-Pep/NHANES-99-00", "demo": "99-00DEMO.xpt", "lab": "99-00NHANES.xpt", "diq": "99-00DIQ.xpt"},
    "2001-2002": {"folder": "NIHANES/C-Pep/NHANES-01-02", "demo": "01-02DEMO_B.xpt", "lab": "01-02NHANES.xpt", "diq": "01-02DIQ_B.xpt"},
    "2003-2004": {"folder": "NIHANES/C-Pep/NHANES-03-04", "demo": "03-04DEMO_C.xpt", "lab": "03-04NHANES.xpt", "diq": "03-04DIQ_C.xpt"},
}

# C-peptide: nmol/L to ng/mL (MW ~3020 g/mol)
CPEP_NMOL_TO_NGML = 3.02


def load_nhanes_cpep_cycle(cycle: str, base: Path | str | None = None) -> pd.DataFrame:
    """
    Load NHANES C-Pep cycle (1999-2000, 2001-2002, 2003-2004).
    Merges DEMO + lab (glucose, insulin, C-peptide) + DIQ. No GHB or BMX in C-Pep folder.
    Lab file has LBXGLU, LBXIN (or LBDINSI), LBXCPSI (nmol/L).
    """
    root = Path(base) if base else _DIABETES_BASE
    cfg = NHANES_CPEP_CONFIG.get(cycle)
    if not cfg:
        raise ValueError("cycle must be '1999-2000', '2001-2002', or '2003-2004'")
    cpep_dir = root / cfg["folder"]
    if not cpep_dir.exists():
        raise FileNotFoundError(f"C-Pep directory not found: {cpep_dir}")

    demo = pd.read_sas(cpep_dir / cfg["demo"])
    lab = pd.read_sas(cpep_dir / cfg["lab"])
    out = demo.merge(lab, on="SEQN", how="inner")
    diq_path = cpep_dir / cfg["diq"]
    if diq_path.exists():
        diq = pd.read_sas(diq_path)
        if "SEQN" in diq.columns:
            out = out.merge(diq, on="SEQN", how="left", suffixes=("", "_DIQ"))
    logger.info("Loaded NHANES C-Pep %s: %d rows", cycle, len(out))
    return out


def _nhanes_cpep_to_unified(df: pd.DataFrame, cycle: str, base_source: str) -> pd.DataFrame:
    """Map NHANES C-Pep merged data to unified schema. Insulin: LBXIN or LBDINSI."""
    df = df.copy()
    ins_col = "LBXIN" if "LBXIN" in df.columns else "LBDINSI"
    df = add_homa_columns(df, "LBXGLU", ins_col, homa_ir_col="homa_ir", homa_beta_col="homa_beta")
    invalid = (df["LBXGLU"] <= 0) | (df[ins_col] <= 0)
    # C-peptide: LBXCPSI nmol/L -> ng/mL
    cpep_ng = df["LBXCPSI"] * CPEP_NMOL_TO_NGML if "LBXCPSI" in df.columns else pd.Series([np.nan] * len(df), index=df.index)
    ins_cpep_ratio = df[ins_col] / cpep_ng.replace(0, np.nan) if cpep_ng.notna().any() else pd.Series([np.nan] * len(df), index=df.index)

    wt_col = next((c for c in df.columns if "WTSAF" in c), None)
    n = len(df)
    rows = []
    for i in range(n):
        row = df.iloc[i]
        r = dict(_empty_unified_row(base_source))
        seqn = row.get("SEQN", i)
        r["patient_id"] = f"{base_source}_{int(seqn)}"
        r["age_years"] = row.get("RIDAGEYR", pd.NA)
        riagendr = row.get("RIAGENDR", pd.NA)
        r["sex"] = (1 if float(riagendr) == 1 else 0) if pd.notna(riagendr) else pd.NA
        r["bmi_kg_m2"] = row.get("BMXBMI", pd.NA)  # usually NA for C-Pep
        r["glucose_mg_dl"] = row.get("LBXGLU", pd.NA)
        r["insulin_uU_ml"] = row.get(ins_col, pd.NA)
        r["homa_ir"] = df["homa_ir"].iloc[i]
        r["homa_beta"] = df["homa_beta"].iloc[i]
        r["c_peptide_ng_ml"] = cpep_ng.iloc[i] if pd.notna(cpep_ng.iloc[i]) else pd.NA
        r["ins_cpep_ratio"] = ins_cpep_ratio.iloc[i] if pd.notna(ins_cpep_ratio.iloc[i]) else pd.NA
        r["diabetes_status"] = 1 if (pd.notna(row.get("LBXGLU")) and float(row["LBXGLU"]) >= 126) else 0
        r["invalid_homa_flag"] = bool(invalid.iloc[i])
        r["homa_analysis_eligible"] = True
        r["hba1c_percent"] = pd.NA
        r["bp_systolic_mmHg"] = pd.NA
        r["bp_diastolic_mmHg"] = pd.NA
        r["pregnancies_count"] = pd.NA
        r["diabetes_pedigree_function"] = pd.NA
        r["survey_weight"] = row.get(wt_col, pd.NA) if wt_col else pd.NA
        r["survey_year"] = row.get("SDDSRVYR", pd.NA)
        reth = row.get("RIDRETH3", row.get("RIDRETH1", pd.NA))
        r["race_ethnicity"] = RIDRETH3_LABELS.get(float(reth), reth) if pd.notna(reth) else pd.NA
        educ = row.get("DMDEDUC2", pd.NA)
        r["education_level"] = DMDEDUC2_LABELS.get(float(educ), educ) if pd.notna(educ) else pd.NA
        r["pir"] = row.get("INDFMPIR", pd.NA)
        r["diq_diabetes"] = _map_diq_value(row.get("DIQ010", pd.NA))
        r["diq_prediabetes"] = _map_diq_value(row.get("DIQ160", pd.NA))
        r["insulin_use"] = _map_diq_value(row.get("DIQ050", pd.NA))
        r["diabetes_pills"] = _map_diq_value(row.get("DIQ070", pd.NA))
        rows.append(r)
    out_df = pd.DataFrame(rows, columns=UNIFIED_SCHEMA)
    return out_df


def _load_nhanes_diq(cycle: str, root: Path) -> pd.DataFrame | None:
    """Load NHANES Diabetes Questionnaire (DIQ) if present. Merge key: SEQN."""
    cfg = NHANES_CYCLE_CONFIG.get(cycle)
    if not cfg:
        return None
    folders_to_try: list[str] = [cfg["folder"]]
    if cfg["folder"] != "NHANES-Diabetes":
        folders_to_try.append("NHANES-Diabetes")
    for folder in folders_to_try:
        diq_dir = root / folder
        if not diq_dir.exists():
            continue
        fnames = cfg.get("diq", [])
        dfs: list[pd.DataFrame] = []
        for fname in fnames:
            path = diq_dir / fname
            if not path.exists():
                continue
            try:
                df = pd.read_sas(path)
                if "SEQN" in df.columns and len(df) > 0:
                    dfs.append(df)
                    logger.info("Loaded NHANES DIQ %s from %s: %d rows", cycle, path.name, len(df))
            except Exception as e:
                logger.warning("Failed to read DIQ %s: %s", path, e)
        if dfs:
            out = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["SEQN"], keep="first")
            return out
    return None


def load_nhanes_cycle(
    cycle: str,
    components: tuple[str, ...] = ("DEMO", "GLU", "INS", "GHB", "BMX"),
    base: Path | str | None = None,
    include_diq: bool = True,
) -> pd.DataFrame:
    """
    Load and merge one NHANES cycle (2013-14, 2015-16, 2017-20, or 2021-23).
    Each cycle uses a specific folder within TL-KiHealth: 2013-14-NHANES, 2015-16-NHANES, NIHANES.
    components: DEMO, GLU, INS, GHB, BMX. Merge key: SEQN.
    BMX supplies BMXBMI (BMI kg/m²); merged with left join to keep all fasting subsample.
    If include_diq=True, merges Diabetes Questionnaire (DIQ) when present.
    """
    root = Path(base) if base else _DIABETES_BASE
    cfg = NHANES_CYCLE_CONFIG.get(cycle)
    if not cfg:
        raise ValueError("cycle must be '2013-14', '2015-16', '2017-20', or '2021-23'")
    nhanes_dir = root / cfg["folder"]
    if not nhanes_dir.exists():
        raise FileNotFoundError(f"NHANES directory not found: {nhanes_dir} (TL-KiHealth/{cfg['folder']})")

    file_map = cfg["files"]
    dfs: list[tuple[str, pd.DataFrame]] = []
    for comp in components:
        fname = file_map.get(comp)
        if not fname:
            continue
        path = nhanes_dir / fname
        if not path.exists():
            logger.warning("NHANES file not found: %s", path)
            continue
        try:
            df = pd.read_sas(path)
        except Exception as e:
            logger.warning("Failed to read %s: %s", path, e)
            continue
        dfs.append((comp, df))

    if not dfs:
        return pd.DataFrame()

    out = dfs[0][1].copy()
    for comp, df in dfs[1:]:
        # BMX: left join so we keep all fasting subsample; BMXBMI may be NaN if not measured
        how = "left" if comp == "BMX" else "inner"
        out = out.merge(df, on="SEQN", how=how, suffixes=("", f"_{comp}"))

    if include_diq:
        diq_df = _load_nhanes_diq(cycle, root)
        if diq_df is not None and "SEQN" in diq_df.columns:
            out = out.merge(diq_df, on="SEQN", how="left", suffixes=("", "_DIQ"))

    logger.info("Loaded NHANES %s: %d rows", cycle, len(out))
    return out


def _frankfurt_to_unified(df: pd.DataFrame, base_source: str = "frankfurt") -> pd.DataFrame:
    """
    Map Frankfurt raw data to unified schema.

    Frankfurt = Pima Indians Diabetes Dataset: insulin is 2-hour OGTT, NOT fasting.
    HOMA formulas require fasting glucose and insulin; 2-hour insulin is invalid.
    All Frankfurt rows get invalid_homa_flag=True and homa_ir/homa_beta=NaN.
    Valid uses: diabetes outcome, glucose, demographics. Not HOMA-IR/beta.
    """
    df = df.copy()
    n = len(df)
    rows = []
    for i in range(n):
        r = dict(_empty_unified_row(base_source))
        r["patient_id"] = f"{base_source}_{i}"
        r["age_years"] = df["Age"].iloc[i]
        r["sex"] = 0  # Frankfurt: female only (Pima Indians)
        r["bmi_kg_m2"] = df["BMI"].iloc[i]
        r["glucose_mg_dl"] = df["Glucose"].iloc[i]
        r["insulin_uU_ml"] = df["Insulin"].iloc[i]
        # HOMA invalid for Frankfurt: 2-hour OGTT insulin, not fasting
        r["homa_ir"] = pd.NA
        r["homa_beta"] = pd.NA
        r["diabetes_status"] = int(df["Outcome"].iloc[i])
        r["invalid_homa_flag"] = True  # ALL Frankfurt: 2-hour insulin
        r["homa_analysis_eligible"] = False  # EXCLUDED from HOMA modeling (2-hour OGTT)
        r["bp_diastolic_mmHg"] = df["BloodPressure"].iloc[i]
        r["bp_systolic_mmHg"] = pd.NA
        r["pregnancies_count"] = df["Pregnancies"].iloc[i]
        r["diabetes_pedigree_function"] = df["DiabetesPedigreeFunction"].iloc[i]
        r["survey_weight"] = pd.NA
        r["survey_year"] = pd.NA
        rows.append(r)
    return pd.DataFrame(rows, columns=UNIFIED_SCHEMA)


def _diabd_to_unified(df: pd.DataFrame, base_source: str = "diabd") -> pd.DataFrame:
    """Map DiaBD raw data to unified schema. Sex not in DiaBD -> set NaN (or infer later)."""
    df = df.copy()
    df = add_homa_columns(df, "Glucose", "Insulin", homa_ir_col="homa_ir", homa_beta_col="homa_beta")
    invalid = (df["Glucose"] <= 0) | (df["Insulin"] <= 0)
    n = len(df)
    rows = []
    for i in range(n):
        r = dict(_empty_unified_row(base_source))
        r["patient_id"] = f"{base_source}_{i}"
        r["age_years"] = df["Age"].iloc[i]
        r["sex"] = pd.NA  # DiaBD does not have sex
        r["bmi_kg_m2"] = df["BMI"].iloc[i]
        r["glucose_mg_dl"] = float(df["Glucose"].iloc[i])
        r["insulin_uU_ml"] = float(df["Insulin"].iloc[i])
        r["homa_ir"] = df["homa_ir"].iloc[i]
        r["homa_beta"] = df["homa_beta"].iloc[i]
        r["diabetes_status"] = int(df["Type-2 Diabetic"].iloc[i])
        r["invalid_homa_flag"] = bool(invalid.iloc[i])
        r["homa_analysis_eligible"] = False  # EXCLUDED from HOMA modeling (data quality concerns)
        r["bp_systolic_mmHg"] = df["BP(Systolic)"].iloc[i] if pd.notna(df["BP(Systolic)"].iloc[i]) else pd.NA
        r["bp_diastolic_mmHg"] = df["BP(Diastolic)"].iloc[i] if pd.notna(df["BP(Diastolic)"].iloc[i]) else pd.NA
        r["pregnancies_count"] = df["No. of Pregnancy"].iloc[i]
        r["diabetes_pedigree_function"] = df["DiabetesPedigreeFunction"].iloc[i]
        r["survey_weight"] = pd.NA
        r["survey_year"] = pd.NA
        rows.append(r)
    return pd.DataFrame(rows, columns=UNIFIED_SCHEMA)


def _map_diq_value(v: Any) -> Any:
    """Map NHANES DIQ 1=Yes, 2=No; 7/9=Refused/Don't know -> NA."""
    if pd.isna(v):
        return pd.NA
    vf = float(v)
    if vf in (7, 9):
        return pd.NA
    return 1 if vf == 1 else (0 if vf == 2 else pd.NA)


def _nhanes_diabetes_status(row: pd.Series) -> int:
    """Derive binary diabetes: fasting glucose >= 126 OR HbA1c >= 6.5%."""
    glu = row.get("LBXGLU")
    hba1c = row.get("LBXGH")
    if pd.isna(glu) and pd.isna(hba1c):
        return 0
    if pd.notna(glu) and float(glu) >= 126:
        return 1
    if pd.notna(hba1c) and float(hba1c) >= 6.5:
        return 1
    return 0


def _nhanes_to_unified(df: pd.DataFrame, cycle: str, base_source: str) -> pd.DataFrame:
    """Map NHANES merged (DEMO+GLU+INS+GHB) to unified schema. Sex: 1=Male,2=Female -> 0=Female,1=Male."""
    df = df.copy()
    df = add_homa_columns(df, "LBXGLU", "LBXIN", homa_ir_col="homa_ir", homa_beta_col="homa_beta")
    invalid = (df["LBXGLU"] <= 0) | (df["LBXIN"] <= 0)
    n = len(df)
    # Survey weight: 2017-20 WTSAFPRP (from GLU), 2021-23 WTSAF2YR
    wt_col = "WTSAFPRP" if cycle == "2017-20" else "WTSAF2YR"
    if wt_col not in df.columns:
        wt_candidates = [c for c in df.columns if "WTSAF" in c or c == "WTMECPRP" or c == "WTINT2YR"]
        wt_col = wt_candidates[0] if wt_candidates else None
    survey_yr = df["SDDSRVYR"].iloc[0] if "SDDSRVYR" in df.columns and len(df) else pd.NA
    rows = []
    for i in range(n):
        row = df.iloc[i]
        r = dict(_empty_unified_row(base_source))
        seqn = row.get("SEQN", i)
        r["patient_id"] = f"{base_source}_{int(seqn)}"
        r["age_years"] = row.get("RIDAGEYR", pd.NA)
        # RIAGENDR 1=Male 2=Female -> 0=Female 1=Male
        riagendr = row.get("RIAGENDR", pd.NA)
        if pd.notna(riagendr):
            r["sex"] = 1 if float(riagendr) == 1 else 0
        else:
            r["sex"] = pd.NA
        r["bmi_kg_m2"] = row.get("BMXBMI", pd.NA)  # from BMX (kg/m²)
        r["glucose_mg_dl"] = row.get("LBXGLU", pd.NA)
        r["insulin_uU_ml"] = row.get("LBXIN", pd.NA)
        r["homa_ir"] = df["homa_ir"].iloc[i]
        r["homa_beta"] = df["homa_beta"].iloc[i]
        r["diabetes_status"] = _nhanes_diabetes_status(row)
        r["invalid_homa_flag"] = bool(invalid.iloc[i])
        r["homa_analysis_eligible"] = True  # NHANES: gold standard fasting data
        r["hba1c_percent"] = row.get("LBXGH", pd.NA)
        r["bp_systolic_mmHg"] = pd.NA
        r["bp_diastolic_mmHg"] = pd.NA
        r["pregnancies_count"] = pd.NA
        r["diabetes_pedigree_function"] = pd.NA
        r["survey_weight"] = row.get(wt_col, pd.NA) if wt_col else pd.NA
        r["survey_year"] = survey_yr
        reth = row.get("RIDRETH3", pd.NA)
        r["race_ethnicity"] = RIDRETH3_LABELS.get(float(reth), reth) if pd.notna(reth) else pd.NA
        educ = row.get("DMDEDUC2", pd.NA)
        r["education_level"] = DMDEDUC2_LABELS.get(float(educ), educ) if pd.notna(educ) else pd.NA
        r["pir"] = row.get("INDFMPIR", pd.NA)
        r["diq_diabetes"] = _map_diq_value(row.get("DIQ010", pd.NA))
        r["diq_prediabetes"] = _map_diq_value(row.get("DIQ160", pd.NA))
        r["insulin_use"] = _map_diq_value(row.get("DIQ050", pd.NA))
        r["diabetes_pills"] = _map_diq_value(row.get("DIQ070", pd.NA))
        rows.append(r)
    return pd.DataFrame(rows, columns=UNIFIED_SCHEMA)


def build_unified_kihealth(
    base: Path | str | None = None,
    save_path: Path | str | None = None,
    include_nhanes_cpep: bool = True,
    include_nhanes_2013: bool = True,
    include_nhanes_2015: bool = True,
    include_nhanes_2017: bool = True,
    include_nhanes_2021: bool = True,
    include_chns: bool = True,
) -> pd.DataFrame:
    """
    Build unified KiHealth dataset with TIER 1 + TIER 2 variables and standardized column names.

    Sources (order): NHANES C-Pep (1999-2004), 2013-14, 2015-16, 2017-20, 2021-23, CHNS 2009, Frankfurt, DiaBD.
    NHANES C-Pep: Plasma Fasting Glucose, Serum C-peptide & Insulin (NIHANES/C-Pep/).
    HOMA-eligible: NHANES + CHNS.
    """
    root = Path(base) if base else _DIABETES_BASE
    pieces: list[pd.DataFrame] = []

    if include_nhanes_cpep:
        for cycle in ("1999-2000", "2001-2002", "2003-2004"):
            try:
                raw = load_nhanes_cpep_cycle(cycle, base=root)
                if not raw.empty:
                    u = _nhanes_cpep_to_unified(raw, cycle, f"nhanes_cpep_{cycle.replace('-', '_')}")
                    pieces.append(u)
            except Exception as e:
                logger.warning("Skip NHANES C-Pep %s: %s", cycle, e)

    if include_nhanes_2013:
        try:
            raw = load_nhanes_cycle("2013-14", components=("DEMO", "GLU", "INS", "GHB", "BMX"), base=root)
            if not raw.empty:
                u = _nhanes_to_unified(raw, "2013-14", "nhanes_2013_2014")
                pieces.append(u)
        except Exception as e:
            logger.warning("Skip NHANES 2013-14: %s", e)

    if include_nhanes_2015:
        try:
            raw = load_nhanes_cycle("2015-16", components=("DEMO", "GLU", "INS", "GHB", "BMX"), base=root)
            if not raw.empty:
                u = _nhanes_to_unified(raw, "2015-16", "nhanes_2015_2016")
                pieces.append(u)
        except Exception as e:
            logger.warning("Skip NHANES 2015-16: %s", e)

    if include_nhanes_2017:
        try:
            raw = load_nhanes_cycle("2017-20", components=("DEMO", "GLU", "INS", "GHB", "BMX"), base=root)
            if not raw.empty:
                u = _nhanes_to_unified(raw, "2017-20", "nhanes_2017_2020")
                pieces.append(u)
        except Exception as e:
            logger.warning("Skip NHANES 2017-20: %s", e)

    if include_nhanes_2021:
        try:
            raw = load_nhanes_cycle("2021-23", components=("DEMO", "GLU", "INS", "GHB", "BMX"), base=root)
            if not raw.empty:
                u = _nhanes_to_unified(raw, "2021-23", "nhanes_2021_2023")
                pieces.append(u)
        except Exception as e:
            logger.warning("Skip NHANES 2021-23: %s", e)

    if include_chns:
        try:
            u = load_chns(base=None)
            if not u.empty:
                pieces.append(u)
        except FileNotFoundError as e:
            logger.warning("Skip CHNS: %s", e)
        except Exception as e:
            logger.warning("Skip CHNS: %s", e)

    try:
        raw = load_frankfurt(base=root)
        u = _frankfurt_to_unified(raw, "frankfurt")
        pieces.append(u)
    except FileNotFoundError as e:
        logger.warning("Skip Frankfurt: %s", e)

    try:
        raw = load_diabd(base=root)
        u = _diabd_to_unified(raw, "diabd")
        pieces.append(u)
    except FileNotFoundError as e:
        logger.warning("Skip DiaBD: %s", e)

    if not pieces:
        logger.warning("No data loaded; returning empty unified DataFrame")
        return pd.DataFrame(columns=UNIFIED_SCHEMA)

    unified = pd.concat(pieces, ignore_index=True)
    logger.info("Unified dataset: %d rows", len(unified))

    if save_path is not None:
        out = Path(save_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        unified.to_csv(out, index=False)
        logger.info("Saved unified data to %s", out)

    return unified


def load_all_kihealth_tabular(
    include_nhanes_2017: bool = True,
    include_nhanes_2021: bool = True,
    base: Path | str | None = None,
) -> dict[str, pd.DataFrame]:
    """Load all raw tabular sources (no unified schema). Keys: frankfurt, diabd, nhanes_2017_20, nhanes_2021_23."""
    root = Path(base) if base else _DIABETES_BASE
    result: dict[str, pd.DataFrame] = {}
    try:
        result["frankfurt"] = load_frankfurt(base=root)
    except FileNotFoundError:
        pass
    try:
        result["diabd"] = load_diabd(base=root)
    except FileNotFoundError:
        pass
    if include_nhanes_2017:
        try:
            result["nhanes_2017_20"] = load_nhanes_cycle("2017-20", base=root)
        except Exception:
            pass
    if include_nhanes_2021:
        try:
            result["nhanes_2021_23"] = load_nhanes_cycle("2021-23", base=root)
        except Exception:
            pass
    return result


def generate_data_quality_report(
    datasets: dict[str, pd.DataFrame] | None = None,
    base: Path | str | None = None,
) -> pd.DataFrame:
    """Per-dataset, per-column quality summary (non-unified)."""
    if datasets is None:
        datasets = load_all_kihealth_tabular(base=base)
    rows: list[dict[str, Any]] = []
    for name, df in datasets.items():
        for col in df.columns:
            s = df[col]
            n = len(df)
            null_pct = round(100.0 * s.isna().sum() / n, 1) if n else 0
            rows.append({
                "source": name,
                "column": col,
                "dtype": str(s.dtype),
                "non_null": int(s.notna().sum()),
                "null_pct": null_pct,
                "n_unique": int(s.nunique()),
            })
    return pd.DataFrame(rows)
