"""
Ingest Cardinal Health 2026 conference batch (38 patients).

Raw Excel contains hidden ddPCR instrument rows (~976). Only rows with a
3-site % Unmethylated average are real patients. Almost all were non-fasting,
so insulin and C-peptide from this batch must not be used in model training.
Methylation is fasting-independent and remains valid.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

BASE = Path(__file__).resolve().parents[2]
RAW_XLSX = BASE / "data" / "raw" / "Cardinal_Health_Data_and_Metadata_08_18_2026.xlsx"
SHEET = "Cardinal Health 2026"
GOOD_ONES = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "Good-Ones-Kihealth"
OUTPUTS = BASE / "outputs"

UNMETH_AVG_COL = "% Unmethylated Average (3 CpG Sites)"

YES_NO_EXACT = {"yes": "Yes", "y": "Yes", "no": "No", "n": "No"}

YES_NO_COLUMNS = [
    "Have you been diagnosed with Diabetes?",
    "Have you been diagnosed with High Blood Pressure?",
    "Do you feel tired often, even after a good night's sleep?",
    "Do you usually have mood swings or do you feel easily irritable?",
    "Do you feel hungry shortly after eating a meal?",
    "Do you crave sweets?",
    "Do you have multiple skin tags (more than one small, soft flesh-colored or darker growths that hang off the skin)?",
    "Have you been diagnosed with PCOS (Polycystic Ovary Syndrome)?",
    "Have you been diagnosed more than one time in the past year with a Urinary Tract Infection or Skin Infections?",
    "Were you prescribed by a physician to take any blood thinners?",
    "Have you been diagnosed with Type 1 Diabetes, and if yes, what was your Date of Diagnosis?",
    "Have you been diagnosed with Type 2 Diabetes, and if yes, what was your Date of Diagnosis?",
]

NUMERIC_CLEAN = [
    "age_years",
    "bmi_kg_m2",
    "hba1c_percent",
    "insulin",
    "cpeptide",
    "pct_cfDNA",
    "dna_concentration_pg_ul",
    "ins_399_pct_unmeth",
    "ins_135_pct_unmeth",
    "ins_233_pct_unmeth",
    "beta_score_average",
    "weight_lb",
    "sample_volume_ml",
]


def _norm_col(name: str) -> str:
    return " ".join(str(name).replace("\xa0", " ").split())


def find_col(columns, *needles: str) -> str:
    """Match a column by normalized substring (handles extra spaces / nbsp)."""
    needles_n = [_norm_col(n).lower() for n in needles]
    for c in columns:
        cn = _norm_col(c).lower()
        if all(n in cn for n in needles_n):
            return c
    raise KeyError(f"Column not found for needles={needles}")


def standardize_yes_no(val):
    if pd.isna(val):
        return np.nan
    text = str(val).strip()
    if text == "" or text.lower() in {"nan", "none", "nat"}:
        return np.nan
    mapped = YES_NO_EXACT.get(text.lower())
    if mapped is not None:
        return mapped
    return text


def is_blank_or_no_na(val) -> bool:
    if pd.isna(val):
        return True
    text = str(val).strip()
    if text == "":
        return True
    low = text.lower()
    return low in {"no", "n", "na", "n/a", "nan", "none", "nat"}


def mean_fmt(series: pd.Series) -> str:
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().sum() == 0:
        return "NA"
    return f"{s.mean():.2f}"


def main() -> None:
    log = io.StringIO()

    def out(msg: str = "") -> None:
        print(msg)
        log.write(msg + "\n")

    if not RAW_XLSX.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_XLSX}")

    # ------------------------------------------------------------------
    # STEP 1: Load and isolate real patient rows
    # ------------------------------------------------------------------
    raw = pd.read_excel(RAW_XLSX, sheet_name=SHEET)
    raw.columns = [_norm_col(c) for c in raw.columns]
    unmeth_avg = find_col(raw.columns, "Unmethylated Average", "3 CpG")
    patients = raw.loc[raw[unmeth_avg].notna()].copy()
    out(f"Real patient rows found: {len(patients)}")

    # ------------------------------------------------------------------
    # STEP 2: Standardize Yes/No (and fasting) to title case
    # ------------------------------------------------------------------
    fasting_src = find_col(raw.columns, "fasting")
    yes_no_src = []
    for needle in YES_NO_COLUMNS:
        try:
            yes_no_src.append(find_col(raw.columns, needle[:40] if len(needle) > 50 else needle))
        except KeyError:
            # fall back to unique start of the prompt
            yes_no_src.append(find_col(raw.columns, needle.split(",")[0][:35]))
    yes_no_src = list(dict.fromkeys(yes_no_src + [fasting_src]))

    for col in yes_no_src:
        patients[col] = patients[col].map(standardize_yes_no)

    # ------------------------------------------------------------------
    # STEP 3: Clean and rename
    # ------------------------------------------------------------------
    colmap_src = {
        "donor_id": find_col(raw.columns, "UIN"),
        "collection_date": find_col(raw.columns, "Collection Date"),
        "gender": find_col(raw.columns, "Gender"),
        "race": find_col(raw.columns, "Race") if any(_norm_col(c).lower() == "race" for c in raw.columns) else None,
        "age_years": find_col(raw.columns, "Age (Years)"),
        "height_ft_in": find_col(raw.columns, "Height"),
        "weight_lb": find_col(raw.columns, "Weight"),
        "bmi_kg_m2": find_col(raw.columns, "BMI"),
        "hba1c_percent": find_col(raw.columns, "A1c"),
        "insulin": find_col(raw.columns, "Insulin"),
        "cpeptide": find_col(raw.columns, "C-peptide"),
        "pct_cfDNA": find_col(raw.columns, "%cfDNA"),
        "dna_concentration_pg_ul": find_col(raw.columns, "Concentration [pg"),
        "ins_399_pct_unmeth": find_col(raw.columns, "% Unmethylated", "+399"),
        "ins_135_pct_unmeth": find_col(raw.columns, "% Unmethylated", "-135"),
        "ins_233_pct_unmeth": find_col(raw.columns, "% Unmethylated", "-233"),
        "beta_score_average": unmeth_avg,
        "fasting_status": fasting_src,
        "diabetes_diagnosed": find_col(raw.columns, "Have you been diagnosed with Diabetes?"),
        "hbp": find_col(raw.columns, "Have you been diagnosed with High Blood Pressure?"),
        "q_tired": find_col(raw.columns, "feel tired often"),
        "q_mood": find_col(raw.columns, "mood swings"),
        "q_hungry": find_col(raw.columns, "hungry shortly"),
        "q_sweets": find_col(raw.columns, "crave sweets"),
        "q_skin_tags": find_col(raw.columns, "skin tags"),
        "q_pcos": find_col(raw.columns, "PCOS"),
        "q_uti": find_col(raw.columns, "Urinary Tract Infection"),
        "q_blood_thinners": find_col(raw.columns, "blood thinners"),
        "q_t1d_date": find_col(raw.columns, "Type 1 Diabetes"),
        "q_t2d_date": find_col(raw.columns, "Type 2 Diabetes"),
        "q_medications": find_col(raw.columns, "prescription medications"),
        "q_supplements": find_col(raw.columns, "supplements or vitamins"),
        "q_prediabetes_date": find_col(raw.columns, "Prediabetes"),
        "sample_type": find_col(raw.columns, "Sample Type"),
        "tube_type": find_col(raw.columns, "Tube type"),
        "sample_volume_ml": find_col(raw.columns, "Sample Volume"),
        "ddpcr_method": find_col(raw.columns, "ddPCR method"),
        "ddpcr_plate_id": find_col(raw.columns, "ddPCR plate ID"),
    }

    clean = pd.DataFrame()
    for dest, src in colmap_src.items():
        if src is None:
            clean[dest] = np.nan
        else:
            clean[dest] = patients[src].values

    for col in NUMERIC_CLEAN:
        if col in clean.columns:
            clean[col] = pd.to_numeric(clean[col], errors="coerce")

    clean["donor_id"] = clean["donor_id"].astype(str).str.strip()
    clean["collection_date"] = pd.to_datetime(clean["collection_date"], errors="coerce")

    # ------------------------------------------------------------------
    # STEP 4: At-risk labels
    # ------------------------------------------------------------------
    diagnosed = clean["diabetes_diagnosed"].eq("Yes")
    t2d_positive = ~clean["q_t2d_date"].map(is_blank_or_no_na)
    a1c_diabetic = clean["hba1c_percent"] >= 6.5
    a1c_prediabetic = clean["hba1c_percent"] >= 5.7
    a1c_missing = clean["hba1c_percent"].isna()

    at_risk_confident = (diagnosed | t2d_positive | a1c_diabetic).astype(int)
    at_risk_liberal = (diagnosed | t2d_positive | a1c_diabetic | a1c_prediabetic).astype(int)
    at_risk = at_risk_liberal.copy()

    # Questionnaire "No" is NOT a true negative for a screening product.
    ascertained_diabetes = (diagnosed | a1c_diabetic).astype(int)
    lab_dysglycemia = (a1c_prediabetic | a1c_diabetic).astype(int)
    unascertained = ((~diagnosed) & (clean["hba1c_percent"] < 5.7)).astype(int)
    undiagnosed_dysglycemia = ((~diagnosed) & (clean["hba1c_percent"] >= 5.7)).astype(int)

    unknown = (
        (~diagnosed)
        & (~t2d_positive)
        & a1c_missing
        & ~clean["diabetes_diagnosed"].eq("No")
    )
    n_unknown = int(unknown.sum())
    n_confident = int(at_risk_confident.sum())
    n_liberal = int(at_risk.sum())
    n_not = int((at_risk == 0).sum())

    clean["at_risk"] = at_risk
    clean["at_risk_confident"] = at_risk_confident
    clean["at_risk_liberal"] = at_risk_liberal
    clean["unclassified"] = unknown.astype(int)
    clean["ascertained_diabetes"] = ascertained_diabetes
    clean["lab_dysglycemia"] = lab_dysglycemia
    clean["unascertained"] = unascertained
    clean["undiagnosed_dysglycemia"] = undiagnosed_dysglycemia

    out(f"At-risk (confident / dx or A1c>=6.5 or T2D date): {n_confident}")
    out(f"Lab dysglycemia (A1c>=5.7 or known dx):           {n_liberal}")
    out(f"Unascertained (said No AND A1c<5.7):              {int(unascertained.sum())}  [NOT true negatives]")
    out(f"Undiagnosed dysglycemia (said No AND A1c>=5.7):   {int(undiagnosed_dysglycemia.sum())}")
    out(f"Legacy 'not at-risk' count (do not use as TN):    {n_not}")
    out(f"Unknown/unclassified: {n_unknown}")

    # ------------------------------------------------------------------
    # STEP 5: QC filtering
    # ------------------------------------------------------------------
    n_total = len(clean)
    clean["qc_pass"] = (clean["pct_cfDNA"] >= 70) & (clean["dna_concentration_pg_ul"] >= 80)
    n_pass = int(clean["qc_pass"].sum())
    n_fail = n_total - n_pass
    out("Total samples: 38" if n_total == 38 else f"Total samples: {n_total}")
    out(f"Pass QC: {n_pass}")
    out(f"Fail QC: {n_fail} (excluded)")

    qc = clean.loc[clean["qc_pass"]].copy()

    # ------------------------------------------------------------------
    # STEP 6: Non-fasting impact (QC-passing)
    # ------------------------------------------------------------------
    qc["non_fasting"] = qc["fasting_status"].eq("No").astype(int)
    qc["insulin_usable"] = qc["fasting_status"].eq("Yes")
    qc["cpeptide_usable"] = qc["fasting_status"].eq("Yes")
    clean["non_fasting"] = clean["fasting_status"].eq("No").astype(int)
    clean["insulin_usable"] = clean["fasting_status"].eq("Yes")
    clean["cpeptide_usable"] = clean["fasting_status"].eq("Yes")

    fasting = qc[qc["fasting_status"].eq("Yes")]
    nonfast = qc[qc["fasting_status"].eq("No")]
    out(f"Fasting patients: {len(fasting)} (insulin/C-peptide valid)")
    out(f"Non-fasting patients: {len(nonfast)} (insulin/C-peptide EXCLUDED from model use)")
    out(
        "Insulin mean - fasting: "
        f"{mean_fmt(fasting['insulin'])}, non-fasting: {mean_fmt(nonfast['insulin'])}"
    )
    out(
        "C-peptide mean - fasting: "
        f"{mean_fmt(fasting['cpeptide'])}, non-fasting: {mean_fmt(nonfast['cpeptide'])}"
    )
    out("NOTE: Do not use insulin/C-peptide from this batch in model training")

    # ------------------------------------------------------------------
    # STEP 7: Descriptive statistics (QC-passing)
    # ------------------------------------------------------------------
    ar = qc[qc["at_risk"] == 1]
    nar = qc[qc["at_risk"] == 0]
    n_all, n_ar, n_nar = len(qc), len(ar), len(nar)

    rows = [
        ("INS 399 mean", "ins_399_pct_unmeth"),
        ("3-site average mean", "beta_score_average"),
        ("A1c mean", "hba1c_percent"),
        ("BMI mean", "bmi_kg_m2"),
        ("Age mean", "age_years"),
        ("cfDNA mean", "pct_cfDNA"),
    ]
    out("")
    out(
        f"{'Metric':<22} | {'All (N=' + str(n_all) + ')':<14} | "
        f"{'At-risk (N=' + str(n_ar) + ')':<16} | "
        f"{'Not at-risk (N=' + str(n_nar) + ')'}"
    )
    out("-" * 78)
    for label, col in rows:
        out(
            f"{label:<22} | {mean_fmt(qc[col]):<14} | "
            f"{mean_fmt(ar[col]):<16} | {mean_fmt(nar[col])}"
        )

    x = pd.to_numeric(ar["ins_399_pct_unmeth"], errors="coerce").dropna()
    y = pd.to_numeric(nar["ins_399_pct_unmeth"], errors="coerce").dropna()
    out("")
    if len(x) >= 1 and len(y) >= 1:
        stat, pval = mannwhitneyu(x, y, alternative="two-sided")
        direction = (
            "higher in at-risk"
            if x.mean() > y.mean()
            else "higher in not-at-risk"
            if x.mean() < y.mean()
            else "no mean difference"
        )
        out(
            f"Mann-Whitney U (INS 399, at-risk vs not at-risk): "
            f"U={stat:.1f}, p={pval:.4f}, {direction} "
            f"(at-risk mean={x.mean():.2f}, not-at-risk mean={y.mean():.2f})"
        )
    else:
        out("Mann-Whitney U (INS 399): skipped (one group empty)")

    # ------------------------------------------------------------------
    # STEP 8: Save
    # ------------------------------------------------------------------
    GOOD_ONES.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    clean_path = GOOD_ONES / "cardinal_health_2026_clean.csv"
    qc_path = GOOD_ONES / "cardinal_health_2026_qc.csv"
    summary_path = OUTPUTS / "cardinal_health_2026_summary.txt"

    clean.to_csv(clean_path, index=False)
    qc.to_csv(qc_path, index=False)
    summary_path.write_text(log.getvalue())

    out(f"Saved: {clean_path}")
    out(f"Saved: {qc_path}")
    out(f"Saved: {summary_path}")
    out("Done. Review cardinal_health_2026_summary.txt before proceeding.")

    # rewrite summary with full log including save lines
    summary_path.write_text(log.getvalue())


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
