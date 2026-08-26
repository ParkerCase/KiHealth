"""
Reanalyze Cardinal Health 2026 without treating questionnaire 'No' as healthy.

Product intent: find people who may have (or be developing) diabetes from
unmethylated DNA + A1c, including people who do not know they have it.

Insulin/C-peptide remain unused (non-fasting). Cascade scores are loaded from
script 16 if present; otherwise models are scored here with training medians.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, mannwhitneyu

BASE = Path(__file__).resolve().parents[2]
GOOD_ONES = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "Good-Ones-Kihealth"
M2_MODELS = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "M2_Models"
OUTPUTS = BASE / "outputs"

QC_PATH = GOOD_ONES / "cardinal_health_2026_qc.csv"
SCORED_PATH = OUTPUTS / "cardinal_health_2026_scored.csv"
TRAINING_CSV = GOOD_ONES / "KiHealth_Unified_Clean.csv"

ELEVATED_399 = 15.0
HIGH_399 = 19.0


def fmt_id(val) -> str:
    if pd.isna(val):
        return ""
    try:
        num = float(val)
        if num.is_integer():
            return str(int(num))
    except (TypeError, ValueError):
        pass
    return str(val).strip()


def a1c_stratum(x: float) -> str:
    if pd.isna(x):
        return "missing"
    if x >= 6.5:
        return "diabetic (>=6.5)"
    if x >= 5.7:
        return "prediabetic (5.7-6.49)"
    if x >= 5.5:
        return "high-normal (5.5-5.69)"
    return "normal (<5.5)"


def meth_stratum(x: float) -> str:
    if pd.isna(x):
        return "missing"
    if x >= HIGH_399:
        return f"high (>={HIGH_399:.0f})"
    if x >= ELEVATED_399:
        return f"elevated ({ELEVATED_399:.0f}-{HIGH_399:.0f})"
    return f"low (<{ELEVATED_399:.0f})"


def summarize(series: pd.Series) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return "n=0"
    return f"n={len(s)} mean={s.mean():.2f} median={s.median():.2f} range=[{s.min():.2f},{s.max():.2f}]"


def main() -> None:
    qc = pd.read_csv(QC_PATH)
    qc["donor_id"] = qc["donor_id"].map(fmt_id)
    if SCORED_PATH.exists():
        scored = pd.read_csv(SCORED_PATH)
        scored["donor_id"] = scored["donor_id"].map(fmt_id)
        drop_overlap = [c for c in scored.columns if c in qc.columns and c != "donor_id"]
        df = qc.merge(scored.drop(columns=drop_overlap), on="donor_id", how="left")
    else:
        df = qc.copy()
        df["screening_flag"] = np.nan
        df["cascade_result"] = np.nan
        df["screening_prob"] = np.nan
        df["confirmation_prob"] = np.nan

    diagnosed = df["diabetes_diagnosed"].eq("Yes")
    a1c = pd.to_numeric(df["hba1c_percent"], errors="coerce")
    beta399 = pd.to_numeric(df["ins_399_pct_unmeth"], errors="coerce")
    avg3 = pd.to_numeric(df["beta_score_average"], errors="coerce")

    df["a1c_stratum"] = a1c.map(a1c_stratum)
    df["meth_stratum"] = beta399.map(meth_stratum)

    # Ascertained positives: diagnosis or diabetic-range A1c (person has/had diabetes signal)
    df["ascertained_diabetes"] = (diagnosed | (a1c >= 6.5)).astype(int)
    # Lab dysglycemia: A1c in prediabetes or diabetes range, whether they know or not
    df["lab_dysglycemia"] = (a1c >= 5.7).astype(int)
    # Unascertained: said No AND A1c still < 5.7 — NOT a true negative
    df["unascertained"] = ((~diagnosed) & (a1c < 5.7)).astype(int)
    df["undiagnosed_dysglycemia"] = ((~diagnosed) & (a1c >= 5.7)).astype(int)
    df["follow_up"] = ((df["unascertained"] == 1) & (beta399 >= ELEVATED_399)).astype(int)

    n = len(df)
    n_dx = int(diagnosed.sum())
    n_asc = int(df["ascertained_diabetes"].sum())
    n_lab = int(df["lab_dysglycemia"].sum())
    n_undx = int(df["undiagnosed_dysglycemia"].sum())
    n_unasc = int(df["unascertained"].sum())
    n_fu = int(df["follow_up"].sum())

    lines: list[str] = []

    def out(msg: str = "") -> None:
        print(msg)
        lines.append(msg)

    out("=== CARDINAL HEALTH 2026 RELABEL (questionnaire No is NOT healthy) ===")
    out(f"N QC-passing patients: {n}")
    out("Fasting-independent inputs used: INS 399, 3-site average, HbA1c, age, BMI.")
    out("Excluded from model use: insulin, C-peptide (non-fasting).")
    out("")
    out("Label strata (new):")
    out(f"  Self-reported diagnosed Yes:              {n_dx}")
    out(f"  Ascertained diabetes (Yes or A1c>=6.5):   {n_asc}")
    out(f"  Lab dysglycemia (A1c>=5.7):               {n_lab}")
    out(f"  Undiagnosed dysglycemia (No + A1c>=5.7):  {n_undx}  <- product catch")
    out(f"  Unascertained (No + A1c<5.7):             {n_unasc}  <- NOT true negatives")
    out(f"  Follow-up (unascertained + INS399>={ELEVATED_399:.0f}): {n_fu}")
    out("")
    out("Do not compute specificity against unascertained patients.")
    out("")

    out("=== A1c vs self-report ===")
    out(pd.crosstab(df["diabetes_diagnosed"], df["a1c_stratum"], margins=True).to_string())
    out("")
    out("Undiagnosed dysglycemia (said No, A1c already high):")
    undx = df[df["undiagnosed_dysglycemia"] == 1][
        ["donor_id", "hba1c_percent", "ins_399_pct_unmeth", "beta_score_average", "cascade_result"]
    ]
    out(undx.to_string(index=False) if len(undx) else "  (none)")
    out("")

    out("=== Methylation by A1c (label-free, fasting-independent) ===")
    out("INS 399:")
    out(df.groupby("a1c_stratum")["ins_399_pct_unmeth"].agg(["count", "mean", "median"]).round(2).to_string())
    out("3-site average:")
    out(df.groupby("a1c_stratum")["beta_score_average"].agg(["count", "mean", "median"]).round(2).to_string())
    out("")

    out("=== Methylation vs ascertained diabetes (Yes or A1c>=6.5) ===")
    pos = df[df["ascertained_diabetes"] == 1]
    unasc = df[df["unascertained"] == 1]
    out(f"Ascertained diabetes INS 399: {summarize(pos['ins_399_pct_unmeth'])}")
    out(f"Unascertained INS 399:        {summarize(unasc['ins_399_pct_unmeth'])}")
    x = pos["ins_399_pct_unmeth"].dropna()
    y = unasc["ins_399_pct_unmeth"].dropna()
    if len(x) and len(y):
        u, p = mannwhitneyu(x, y, alternative="two-sided")
        out(f"Mann-Whitney ascertained vs unascertained: U={u:.1f}, p={p:.4f}")
        out("  (Unascertained is mixed: true low-risk + possible early signal. A non-significant p is expected.)")
    out("")

    if "screening_flag" in df.columns and df["screening_flag"].notna().any():
        out("=== Cascade vs ascertained positives only (no false-negative gold standard) ===")
        flags = df["screening_flag"].fillna(0).astype(int)
        if n_asc:
            caught = int(((df["ascertained_diabetes"] == 1) & (flags == 1)).sum())
            out(f"Screening flag among ascertained diabetes: {caught}/{n_asc} ({100.0 * caught / n_asc:.1f}%)")
        if n_lab:
            caught_lab = int(((df["lab_dysglycemia"] == 1) & (flags == 1)).sum())
            out(f"Screening flag among lab dysglycemia A1c>=5.7: {caught_lab}/{n_lab} ({100.0 * caught_lab / n_lab:.1f}%)")
        if n_undx:
            caught_undx = int(((df["undiagnosed_dysglycemia"] == 1) & (flags == 1)).sum())
            out(
                f"Screening flag among undiagnosed dysglycemia: {caught_undx}/{n_undx} "
                f"({100.0 * caught_undx / n_undx:.1f}%)  <- did we find people who didn't know?"
            )
        out("Cascade among unascertained (No + A1c<5.7) — interpretation = follow-up mix, not FP rate:")
        out(df.loc[df["unascertained"] == 1, "cascade_result"].value_counts().to_string())
        out("")
        out("Cascade by A1c stratum:")
        out(pd.crosstab(df["a1c_stratum"], df["cascade_result"], margins=True).to_string())
        out("")

    out(f"=== FOLLOW-UP LIST: unascertained + INS 399 >= {ELEVATED_399:.0f} ===")
    out("These people said they do not have diabetes and A1c is still <5.7.")
    out("High unmethylated DNA is the reason to retest A1c / clinically review — not to score as false positives.")
    fu = df[df["follow_up"] == 1][
        [
            "donor_id",
            "age_years",
            "gender",
            "bmi_kg_m2",
            "hba1c_percent",
            "ins_399_pct_unmeth",
            "beta_score_average",
            "cascade_result",
            "hbp",
        ]
    ].sort_values("ins_399_pct_unmeth", ascending=False)
    out(fu.to_string(index=False) if len(fu) else "  (none)")
    out("")

    out("=== TRAINING vs CARDINAL INS 399 (context, not a reason to discard methylation) ===")
    train = pd.read_csv(TRAINING_CSV)
    train = train[train["target"].notna() & train["beta_score"].notna() & train["hba1c"].notna()].copy()
    train_399 = pd.to_numeric(train["beta_score"], errors="coerce")
    out(f"Training overall: {summarize(train_399)}")
    out(f"Cardinal overall: {summarize(beta399)}")
    ks = ks_2samp(train_399.dropna(), beta399.dropna())
    out(f"KS overall D={ks.statistic:.3f} p={ks.pvalue:.4f}")
    out("Cardinal booth samples sit higher than the 129 training set (more like training at-risk).")
    out("That can be mix (older conference attendees) rather than assay failure.")
    out("Training used a curated clinical cohort; this is a walk-up booth. Different priors.")
    out("")

    out("=== WHAT TO USE GOING FORWARD ===")
    out("Keep using (fasting-independent): unmethylated CpGs, A1c, age, BMI.")
    out("Do not use on this batch: insulin, C-peptide, HOMA.")
    out("Future optional fasting-independent adds: random glucose, glycated albumin, T1D autoantibodies.")
    out("")
    out("=== RECOMMENDATION ===")
    out("1. Do NOT add this batch to confirmation training as negatives.")
    out(f"2. Treat {n_unasc} questionnaire-No / A1c<5.7 rows as UNASCERTAINED.")
    out(f"3. Prioritize follow-up of {n_fu} high-INS399 unascertained patients.")
    out(f"4. Count {n_undx} undiagnosed high-A1c cases as evidence the booth screen can catch unknown disease.")
    out("5. Recompute any 'specificity' only after follow-up A1c or clinical adjudication of the follow-up list.")
    out("6. Production walk-up mode should be methylation + A1c + age/BMI, with insulin/C-peptide optional IF fasting.")

    summary_path = OUTPUTS / "cardinal_health_2026_relabel_summary.txt"
    out_path = GOOD_ONES / "cardinal_health_2026_relabel.csv"
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    summary_path.write_text("\n".join(lines) + "\n")
    print(f"\nSaved: {out_path}")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()
