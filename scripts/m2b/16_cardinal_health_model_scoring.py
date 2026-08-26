"""
External validation: score Cardinal Health 2026 patients on production cascade models.

Does not retrain. Insulin/C-peptide from this batch are non-fasting and are
replaced with training-set medians from the cascade metrics JSON files.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parents[2]
GOOD_ONES = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "Good-Ones-Kihealth"
M2_MODELS = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "M2_Models"
OUTPUTS = BASE / "outputs"

CARDINAL_QC = GOOD_ONES / "cardinal_health_2026_qc.csv"
TRAINING_CSV = GOOD_ONES / "KiHealth_Unified_Clean.csv"


def encode_hba1c_tier(hba1c: pd.Series) -> pd.Series:
    return np.select(
        [
            hba1c < 5.5,
            (hba1c >= 5.5) & (hba1c < 5.7),
            (hba1c >= 5.7) & (hba1c < 6.5),
            hba1c >= 6.5,
        ],
        [0, 1, 2, 3],
        default=0,
    ).astype(float)


def encode_cpeptide_risk_tier(cp: pd.Series) -> pd.Series:
    return np.select(
        [
            cp <= 0.7,
            (cp >= 0.8) & (cp <= 0.9),
            (cp >= 1.0) & (cp <= 2.0),
            (cp >= 2.1) & (cp <= 3.0),
            cp >= 3.1,
        ],
        [3, 2, 0, 1, 2],
        default=2,
    ).astype(float)


def cascade_label(screen_prob: float, confirm_prob: float, screen_t: float, bal_t: float, con_t: float) -> str:
    if screen_prob < screen_t:
        return "Cleared"
    if confirm_prob >= bal_t:
        return "High Confidence"
    if confirm_prob >= con_t:
        return "Moderate"
    return "Low-Moderate"


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


def summarize_dist(series: pd.Series) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return "n=0"
    return (
        f"n={len(s)}  mean={s.mean():.2f}  median={s.median():.2f}  "
        f"range=[{s.min():.2f}, {s.max():.2f}]"
    )


def main() -> None:
    cardinal = pd.read_csv(CARDINAL_QC)
    screen_metrics = json.loads((M2_MODELS / "final_cascade_screening_metrics.json").read_text())
    confirm_metrics = json.loads((M2_MODELS / "final_cascade_confirmation_metrics.json").read_text())

    foundation = joblib.load(M2_MODELS / "foundation_combined.joblib")
    foundation_scaler = joblib.load(M2_MODELS / "foundation_scaler.joblib")
    screen_model = joblib.load(M2_MODELS / "final_cascade_screening_model.joblib")
    confirm_model = joblib.load(M2_MODELS / "final_cascade_confirmation_model.joblib")

    screen_ins = float(screen_metrics["median_insulin"])
    screen_cp = float(screen_metrics["median_cpeptide"])
    screen_age = float(screen_metrics.get("median_age", 43.0))
    screen_bmi = float(screen_metrics.get("median_bmi", 26.6))
    confirm_ins = float(confirm_metrics["median_insulin"])
    confirm_cp = float(confirm_metrics["median_cpeptide"])
    confirm_age = float(confirm_metrics.get("median_age", screen_age))
    confirm_bmi = float(confirm_metrics.get("median_bmi", screen_bmi))

    screen_t = float(screen_metrics["thresholds"]["screening"]["threshold"])
    bal_t = float(confirm_metrics["thresholds"]["balanced"]["threshold"])
    con_t = float(confirm_metrics["thresholds"]["confirmation"]["threshold"])

    print("=== EXTERNAL VALIDATION ON CARDINAL HEALTH 2026 ===")
    print("Insulin/C-peptide: training medians only (non-fasting batch excluded)")
    print(f"  Screening medians:  insulin={screen_ins:.2f}, cpeptide={screen_cp:.2f}")
    print(f"  Confirmation medians: insulin={confirm_ins:.2f}, cpeptide={confirm_cp:.2f}")
    print(f"  Thresholds: screening>={screen_t:.2f}, balanced>={bal_t:.2f}, confirmation>={con_t:.2f}")

    hba1c = pd.to_numeric(cardinal["hba1c_percent"], errors="coerce")
    age = pd.to_numeric(cardinal["age_years"], errors="coerce").fillna(screen_age)
    bmi = pd.to_numeric(cardinal["bmi_kg_m2"], errors="coerce").fillna(screen_bmi)
    beta399 = pd.to_numeric(cardinal["ins_399_pct_unmeth"], errors="coerce")

    foundation_input = pd.DataFrame(
        {
            "hba1c_percent": hba1c.astype(float),
            "age_years": age.astype(float),
            "bmi_kg_m2": bmi.astype(float),
        }
    )
    foundation_pred = foundation.predict_proba(foundation_scaler.transform(foundation_input.values))[:, 1]

    insulin_screen = pd.Series(screen_ins, index=cardinal.index, dtype=float)
    cpeptide_screen = pd.Series(screen_cp, index=cardinal.index, dtype=float)
    insulin_confirm = pd.Series(confirm_ins, index=cardinal.index, dtype=float)
    cpeptide_confirm = pd.Series(confirm_cp, index=cardinal.index, dtype=float)

    X_screen = pd.DataFrame(
        {
            "beta_score": beta399,
            "foundation_pred": foundation_pred,
            "insulin_imp": insulin_screen,
            "cpeptide_imp": cpeptide_screen,
            "hba1c_direct": hba1c,
            "hba1c_tier": encode_hba1c_tier(hba1c),
            "cpeptide_risk_tier": encode_cpeptide_risk_tier(cpeptide_screen),
        }
    )
    X_confirm = pd.DataFrame(
        {
            "beta_score_399": beta399,
            "foundation_pred": foundation_pred,
            "insulin_imp": insulin_confirm,
            "cpeptide_imp": cpeptide_confirm,
            "hba1c_direct": hba1c,
        }
    )

    screening_prob = screen_model.predict_proba(X_screen[screen_metrics["features"]])[:, 1]
    confirmation_prob = confirm_model.predict_proba(X_confirm[confirm_metrics["features"]])[:, 1]
    screening_flag = (screening_prob >= screen_t).astype(int)
    cascade_result = [
        cascade_label(sp, cp, screen_t, bal_t, con_t)
        for sp, cp in zip(screening_prob, confirmation_prob)
    ]

    n = len(cardinal)
    n_screen = int(screening_flag.sum())
    n_high = int(sum(r == "High Confidence" for r in cascade_result))
    print(f"N patients scored: {n}")
    print(f"Screening threshold flags: {n_screen} patients ({100.0 * n_screen / n:.1f}%)")
    print(f"High confidence flags: {n_high} patients ({100.0 * n_high / n:.1f}%)")
    print("Cascade result counts:")
    for label in ["Cleared", "Low-Moderate", "Moderate", "High Confidence"]:
        k = sum(r == label for r in cascade_result)
        print(f"  {label}: {k} ({100.0 * k / n:.1f}%)")

    y_conf = cardinal["at_risk_confident"].astype(int).values
    y_lib = cardinal["at_risk"].astype(int).values
    n_conf = int(y_conf.sum())
    n_neg = int((y_lib == 0).sum())

    tp = int(((y_conf == 1) & (screening_flag == 1)).sum())
    sens = tp / n_conf if n_conf else np.nan
    tn = int(((y_lib == 0) & (screening_flag == 0)).sum())
    spec = tn / n_neg if n_neg else np.nan

    print("")
    print(f"At-risk confident: {n_conf}  |  not at-risk (liberal negative): {n_neg}")
    print(
        f"Among confirmed at-risk patients: "
        f"{tp}/{n_conf} flagged at screening ({100.0 * sens:.1f}%)"
        if n_conf
        else "Among confirmed at-risk patients: n/a"
    )
    print(
        f"Among not at-risk patients: "
        f"{tn}/{n_neg} correctly cleared ({100.0 * spec:.1f}%)"
        if n_neg
        else "Among not at-risk patients: n/a"
    )
    print(
        f"Sensitivity on at-risk patients: {100.0 * sens:.1f}%"
        if n_conf
        else "Sensitivity on at-risk patients: n/a"
    )
    print(
        f"Specificity on not at-risk patients: {100.0 * spec:.1f}%"
        if n_neg
        else "Specificity on not at-risk patients: n/a"
    )

    if n_conf >= 1 and (y_conf == 0).sum() >= 1:
        auc_screen = roc_auc_score(y_conf, screening_prob)
        auc_confirm = roc_auc_score(y_conf, confirmation_prob)
        print(f"AUC (screening_prob vs at_risk_confident): {auc_screen:.3f}")
        print(f"AUC (confirmation_prob vs at_risk_confident): {auc_confirm:.3f}")
    else:
        auc_screen = np.nan
        auc_confirm = np.nan
        print("AUC: not computed (insufficient labeled classes)")

    if (y_lib == 1).sum() >= 1 and (y_lib == 0).sum() >= 1:
        print(f"AUC (screening_prob vs at_risk liberal): {roc_auc_score(y_lib, screening_prob):.3f}")

    scored = pd.DataFrame(
        {
            "donor_id": cardinal["donor_id"].map(fmt_id),
            "age_years": cardinal["age_years"],
            "gender": cardinal["gender"],
            "bmi_kg_m2": cardinal["bmi_kg_m2"],
            "hba1c_percent": cardinal["hba1c_percent"],
            "ins_399_pct_unmeth": cardinal["ins_399_pct_unmeth"],
            "beta_score_average": cardinal["beta_score_average"],
            "pct_cfDNA": cardinal["pct_cfDNA"],
            "at_risk_label": cardinal["at_risk"],
            "at_risk_confident": cardinal["at_risk_confident"],
            "screening_prob": np.round(screening_prob, 6),
            "confirmation_prob": np.round(confirmation_prob, 6),
            "screening_flag": screening_flag,
            "cascade_result": cascade_result,
            "foundation_pred": np.round(foundation_pred, 6),
            "hba1c_tier": X_screen["hba1c_tier"].values,
            "cpeptide_risk_tier": X_screen["cpeptide_risk_tier"].values,
        }
    )
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    scored_path = OUTPUTS / "cardinal_health_2026_scored.csv"
    scored.to_csv(scored_path, index=False)
    print(f"\nSaved: {scored_path}")

    print("\n=== INS 399 DISTRIBUTION: TRAINING vs CARDINAL ===")
    train = pd.read_csv(TRAINING_CSV)
    train = train[train["target"].notna() & train["beta_score"].notna() & train["hba1c"].notna()].copy()
    train["at_risk"] = train["target"].astype(int)
    train_399 = pd.to_numeric(train["beta_score"], errors="coerce")
    card_399 = pd.to_numeric(cardinal["ins_399_pct_unmeth"], errors="coerce")

    print(f"Training at-risk:     {summarize_dist(train_399[train['at_risk'] == 1])}")
    print(f"Training not at-risk: {summarize_dist(train_399[train['at_risk'] == 0])}")
    print(f"Cardinal at-risk:     {summarize_dist(card_399[cardinal['at_risk'] == 1])}")
    print(f"Cardinal not at-risk: {summarize_dist(card_399[cardinal['at_risk'] == 0])}")
    print(f"Training overall:     {summarize_dist(train_399)}")
    print(f"Cardinal overall:     {summarize_dist(card_399)}")

    ks_all = ks_2samp(train_399.dropna(), card_399.dropna())
    ks_ar = ks_2samp(
        train_399[train["at_risk"] == 1].dropna(),
        card_399[cardinal["at_risk"] == 1].dropna(),
    )
    ks_nar = ks_2samp(
        train_399[train["at_risk"] == 0].dropna(),
        card_399[cardinal["at_risk"] == 0].dropna(),
    )
    print(f"KS overall:     D={ks_all.statistic:.3f}, p={ks_all.pvalue:.4f}")
    print(f"KS at-risk:     D={ks_ar.statistic:.3f}, p={ks_ar.pvalue:.4f}")
    print(f"KS not at-risk: D={ks_nar.statistic:.3f}, p={ks_nar.pvalue:.4f}")

    train_ar_mean = float(train_399[train["at_risk"] == 1].mean())
    train_nar_mean = float(train_399[train["at_risk"] == 0].mean())
    card_ar_mean = float(card_399[cardinal["at_risk"] == 1].mean())
    card_nar_mean = float(card_399[cardinal["at_risk"] == 0].mean())
    train_dir = "higher" if train_ar_mean > train_nar_mean else "lower"
    card_dir = "higher" if card_ar_mean > card_nar_mean else "lower"
    print(
        f"Training: at-risk INS 399 is {train_dir} than not-at-risk "
        f"({train_ar_mean:.2f} vs {train_nar_mean:.2f})"
    )
    print(
        f"Cardinal: at-risk INS 399 is {card_dir} than not-at-risk "
        f"({card_ar_mean:.2f} vs {card_nar_mean:.2f})"
    )

    shift = ks_all.pvalue < 0.05 or ks_ar.pvalue < 0.05
    direction_mismatch = (train_ar_mean > train_nar_mean) != (card_ar_mean > card_nar_mean)
    weak_separation = abs(card_ar_mean - card_nar_mean) < 2.0
    print("\nInterpretation:")
    if shift:
        print("  Distribution shift detected vs training INS 399 (KS p<0.05).")
    else:
        print("  No significant KS shift vs training overall (p>=0.05).")
    if direction_mismatch or weak_separation:
        print(
            "  Cardinal methylation does not separate at-risk vs not-at-risk "
            "the way training data does (small/reversed mean gap)."
        )
    if n_conf < 10:
        print(f"  At-risk confident N={n_conf} is small for training an additional confirmation fold.")
    print("  Insulin/C-peptide from this batch remain unusable (non-fasting).")

    print("\n=== RECOMMENDATION ===")
    if direction_mismatch or weak_separation or shift or n_conf < 8:
        if shift or direction_mismatch or weak_separation:
            print(
                "RECOMMENDATION: Use as reference range validation only (distribution "
                "shift detected / insufficient at-risk labels)"
            )
        else:
            print("RECOMMENDATION: Requires clinical label review before any model use")
    elif n_conf >= 8 and not shift and not direction_mismatch:
        print(
            "RECOMMENDATION: Add to confirmation model training (methylation signal "
            f"consistent, at-risk labels reliable, N at-risk patients={n_conf})"
        )
    else:
        print("RECOMMENDATION: Requires clinical label review before any model use")

    print("\nNo training artifacts were updated.")


if __name__ == "__main__":
    main()
