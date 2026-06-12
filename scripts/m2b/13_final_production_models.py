"""
Train and save final production cascade models.

MODEL 1: R1 screening on 129 original patients (hba1c_tier + cpeptide_risk_tier).
MODEL 2: CONFIG B confirmation on 162 patients (Base5 + INS 399).
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parents[2]
GOOD_ONES = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "Good-Ones-Kihealth"
M2_MODELS = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "M2_Models"
V2_STEM = "V2_Reference_Range_Samples_with_Demographics_01JUN2026"

SINGLE_SEED = 42
REPEATED_SEEDS = list(range(10))
N_FOLDS = 5
N_BOOT = 1000
OVERFIT_GAP = 0.05

SCREEN_FEATURES = [
    "beta_score",
    "foundation_pred",
    "insulin_imp",
    "cpeptide_imp",
    "hba1c_direct",
    "hba1c_tier",
    "cpeptide_risk_tier",
]

CONFIRM_FEATURES = [
    "beta_score_399",
    "foundation_pred",
    "insulin_imp",
    "cpeptide_imp",
    "hba1c_direct",
]

ORIGINAL_M2 = {
    "rep_auc": 0.896,
    "ci_lower": 0.85,
    "ci_upper": 0.95,
    "scr_j": 0.57,
    "bal_j": 0.59,
    "con_j": 0.59,
    "n": 129,
}


def make_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    C=5.0,
                    penalty="l2",
                    solver="lbfgs",
                    max_iter=1000,
                    random_state=SINGLE_SEED,
                ),
            ),
        ]
    )


def find_v2_file() -> Path:
    candidates = [
        GOOD_ONES / f"{V2_STEM}.xlsx",
        BASE / "deliverables" / "M1_clean" / "data" / f"{V2_STEM}.xlsx",
        BASE / "deliverables" / "M1_clean" / "data" / f"{V2_STEM}.csv",
        GOOD_ONES / f"{V2_STEM}.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"V2 file not found (tried {V2_STEM}.xlsx/.csv)")


def load_v2_raw() -> pd.DataFrame:
    path = find_v2_file()
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path)
    return pd.read_csv(path)


def pick_column(df: pd.DataFrame, needles: tuple[str, ...]) -> str:
    for col in df.columns:
        norm = col.lower().replace(" ", "")
        if all(n.lower().replace(" ", "") in norm for n in needles):
            return col
    raise KeyError(f"No column matching {needles}")


def load_original_cohort() -> pd.DataFrame:
    df = pd.read_csv(GOOD_ONES / "KiHealth_Unified_Clean.csv")
    mask = df["target"].notna() & df["beta_score"].notna() & df["hba1c"].notna()
    cohort = df.loc[mask].copy()
    cohort["beta_score_399"] = cohort["beta_score"].astype(float)
    cohort["at_risk"] = cohort["target"].astype(int)
    return cohort[
        ["beta_score", "beta_score_399", "hba1c", "insulin", "cpeptide", "age", "bmi", "at_risk"]
    ].rename(columns={"hba1c": "hba1c_direct"})


def load_v2_cohort() -> pd.DataFrame:
    raw = load_v2_raw()
    col_399 = pick_column(raw, ("%", "399"))
    col_cf = pick_column(raw, ("%cfd",))
    col_conc = pick_column(raw, ("concentration",))

    qc_mask = (pd.to_numeric(raw[col_cf], errors="coerce") >= 70) & (
        pd.to_numeric(raw[col_conc], errors="coerce") >= 80
    )
    qc = raw.loc[qc_mask].copy()
    ins399 = pd.to_numeric(qc[col_399], errors="coerce")

    v2 = pd.DataFrame(
        {
            "beta_score": ins399,
            "beta_score_399": ins399,
            "hba1c_direct": pd.to_numeric(qc["A1c"], errors="coerce"),
            "insulin": pd.to_numeric(qc["Insulin"], errors="coerce"),
            "cpeptide": pd.to_numeric(qc["C-peptide"], errors="coerce"),
            "age": pd.to_numeric(qc["Age"], errors="coerce"),
            "bmi": pd.to_numeric(qc["BMI"], errors="coerce"),
            "at_risk": qc["Risk"].astype(str).str.strip().str.lower().eq("yes").astype(int),
        },
        index=qc.index,
    )
    return v2[v2["beta_score_399"].notna() & v2["hba1c_direct"].notna()].copy()


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


def build_features(cohort: pd.DataFrame, *, cohort_medians: dict | None = None) -> tuple[pd.DataFrame, np.ndarray, dict]:
    foundation_model = joblib.load(M2_MODELS / "foundation_combined.joblib")
    foundation_scaler = joblib.load(M2_MODELS / "foundation_scaler.joblib")

    if cohort_medians is None:
        med_insulin = float(cohort["insulin"].median())
        med_cpeptide = float(cohort["cpeptide"].median())
        med_age = float(cohort["age"].median())
        med_bmi = float(cohort["bmi"].median())
    else:
        med_insulin = cohort_medians["median_insulin"]
        med_cpeptide = cohort_medians["median_cpeptide"]
        med_age = cohort_medians["median_age"]
        med_bmi = cohort_medians["median_bmi"]

    feat = pd.DataFrame(index=cohort.index)
    feat["beta_score"] = cohort["beta_score_399"].astype(float)
    feat["beta_score_399"] = cohort["beta_score_399"].astype(float)
    feat["hba1c_direct"] = cohort["hba1c_direct"].astype(float)
    feat["insulin_imp"] = cohort["insulin"].fillna(med_insulin).astype(float)
    feat["cpeptide_imp"] = cohort["cpeptide"].fillna(med_cpeptide).astype(float)

    foundation_input = pd.DataFrame(
        {
            "hba1c_percent": feat["hba1c_direct"],
            "age_years": cohort["age"].fillna(med_age).astype(float),
            "bmi_kg_m2": cohort["bmi"].fillna(med_bmi).astype(float),
        }
    )
    foundation_scaled = foundation_scaler.transform(foundation_input.values)
    feat["foundation_pred"] = foundation_model.predict_proba(foundation_scaled)[:, 1]

    feat["hba1c_tier"] = encode_hba1c_tier(feat["hba1c_direct"])
    feat["cpeptide_risk_tier"] = encode_cpeptide_risk_tier(feat["cpeptide_imp"])

    y = cohort["at_risk"].astype(int).values
    meta = {
        "median_insulin": med_insulin,
        "median_cpeptide": med_cpeptide,
        "median_age": med_age,
        "median_bmi": med_bmi,
        "n": len(cohort),
        "at_risk": int(y.sum()),
    }
    return feat, y, meta


def repeated_cv_fold_aucs(X: np.ndarray, y: np.ndarray, model: Pipeline, seeds: list[int]) -> list[float]:
    aucs: list[float] = []
    for seed in seeds:
        cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        for train_idx, val_idx in cv.split(X, y):
            m = clone(model)
            m.fit(X[train_idx], y[train_idx])
            aucs.append(roc_auc_score(y[val_idx], m.predict_proba(X[val_idx])[:, 1]))
    return aucs


def seed_cv_oof_probs(X: np.ndarray, y: np.ndarray, model: Pipeline, seed: int) -> np.ndarray:
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    return cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]


def bootstrap_auc_ci(y_true: np.ndarray, y_prob: np.ndarray, n_boot: int = N_BOOT, seed: int = SINGLE_SEED) -> tuple[float, float]:
    rng = np.random.RandomState(seed)
    aucs: list[float] = []
    for _ in range(n_boot):
        idx = rng.randint(0, len(y_true), len(y_true))
        if len(np.unique(y_true[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y_true[idx], y_prob[idx]))
    return float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def metrics_at_threshold(y: np.ndarray, probs: np.ndarray, thresh: float) -> dict:
    y_bin = (probs >= thresh).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
    sens = tp / (tp + fn) if (tp + fn) else 0.0
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "threshold": round(float(thresh), 2),
        "sensitivity": float(sens),
        "specificity": float(spec),
        "youden_j": float(sens + spec - 1),
    }


def find_screening_threshold(y: np.ndarray, probs: np.ndarray, target_sens: float = 0.98) -> dict:
    best = None
    best_thresh = 0.5
    for thresh in np.arange(0.05, 0.96, 0.005):
        m = metrics_at_threshold(y, probs, float(thresh))
        if m["sensitivity"] >= target_sens - 0.005:
            if best is None or m["specificity"] > best["specificity"]:
                best = m
                best_thresh = float(thresh)
    if best is None:
        fpr, tpr, th = roc_curve(y, probs)
        idx = int(np.argmin(np.abs(tpr - target_sens)))
        best_thresh = float(th[idx]) if idx < len(th) else 0.5
        best = metrics_at_threshold(y, probs, best_thresh)
    best["threshold"] = round(best_thresh, 2)
    return best


def find_balanced_threshold(y: np.ndarray, probs: np.ndarray, target_sens: float = 0.76) -> dict:
    best = None
    best_thresh = 0.5
    for thresh in np.arange(0.05, 0.96, 0.005):
        m = metrics_at_threshold(y, probs, float(thresh))
        if m["sensitivity"] >= target_sens - 0.01:
            if best is None or m["specificity"] > best["specificity"]:
                best = m
                best_thresh = float(thresh)
    if best is None:
        fpr, tpr, th = roc_curve(y, probs)
        j = tpr - fpr
        idx = int(np.argmax(j))
        best_thresh = float(th[idx]) if idx < len(th) else 0.5
        best = metrics_at_threshold(y, probs, best_thresh)
    best["threshold"] = round(best_thresh, 2)
    return best


def find_confirmation_threshold(y: np.ndarray, probs: np.ndarray, target_spec: float = 0.87) -> dict:
    best = None
    best_thresh = 0.58
    for thresh in np.arange(0.05, 0.96, 0.005):
        m = metrics_at_threshold(y, probs, float(thresh))
        if m["specificity"] >= target_spec - 0.01:
            if best is None or m["sensitivity"] > best["sensitivity"]:
                best = m
                best_thresh = float(thresh)
    if best is None:
        best = metrics_at_threshold(y, probs, best_thresh)
    best["threshold"] = round(best_thresh, 2)
    return best


def train_model(
    name: str,
    feature_cols: list[str],
    X: np.ndarray,
    y: np.ndarray,
    meta: dict,
    *,
    save_screening_thresh: bool,
    save_balanced_thresh: bool,
    save_confirm_thresh: bool,
) -> tuple[CalibratedClassifierCV, dict, dict]:
    base = make_pipeline()
    fold_aucs = repeated_cv_fold_aucs(X, y, base, REPEATED_SEEDS)
    rep_mean = float(np.mean(fold_aucs))
    rep_std = float(np.std(fold_aucs))

    oof = seed_cv_oof_probs(X, y, base, SINGLE_SEED)
    single_auc = float(roc_auc_score(y, oof))
    ci_lo, ci_hi = bootstrap_auc_ci(y, oof)

    base.fit(X, y)
    train_auc = float(roc_auc_score(y, base.predict_proba(X)[:, 1]))
    overfit_gap = train_auc - single_auc

    calibrated = CalibratedClassifierCV(base, method="isotonic", cv=3)
    calibrated.fit(X, y)
    cal_probs = calibrated.predict_proba(X)[:, 1]

    screen_m = find_screening_threshold(y, oof, 0.98)
    bal_m = find_balanced_threshold(y, oof, 0.76)
    con_m = find_confirmation_threshold(y, oof, 0.87)

    thresholds: dict[str, dict] = {}
    if save_screening_thresh:
        thresholds["screening"] = screen_m
    if save_balanced_thresh:
        thresholds["balanced"] = bal_m
    if save_confirm_thresh:
        thresholds["confirmation"] = con_m

    metrics = {
        "model_type": name,
        "features": feature_cols,
        "kihealth_patients": meta["n"],
        "kihealth_at_risk": meta["at_risk"],
        "cv_auc_single_seed": single_auc,
        "cv_auc_repeated_mean": rep_mean,
        "cv_auc_repeated_std": rep_std,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "train_auc": train_auc,
        "overfit_gap": float(overfit_gap),
        "overfit_flag": overfit_gap > OVERFIT_GAP,
        "thresholds": thresholds,
        "youden_j": {
            "screening": screen_m["youden_j"],
            "balanced": bal_m["youden_j"],
            "confirmation": con_m["youden_j"],
        },
        **{k: v for k, v in meta.items() if k.startswith("median_")},
    }

    summary = {
        "rep_auc": rep_mean,
        "ci": (ci_lo, ci_hi),
        "scr_j": screen_m["youden_j"],
        "bal_j": bal_m["youden_j"],
        "con_j": con_m["youden_j"],
        "overfit": overfit_gap > OVERFIT_GAP,
        "n": meta["n"],
        "cal_probs": cal_probs,
        "thresholds": thresholds,
    }
    return calibrated, metrics, summary


def compute_funnel(
    y: np.ndarray,
    screen_probs: np.ndarray,
    confirm_probs: np.ndarray,
    screen_thresh: float,
    confirm_thresh: float,
) -> dict[str, float]:
    n = len(y)
    screen_pos = screen_probs >= screen_thresh
    confirm_pos = confirm_probs >= confirm_thresh

    stage1_pct = 100.0 * screen_pos.sum() / n
    screened_n = int(screen_pos.sum())
    confirm_of_screened = 100.0 * (screen_pos & confirm_pos).sum() / screened_n if screened_n else 0.0
    fp_rate = 100.0 * (screen_pos & confirm_pos & (y == 0)).sum() / n

    return {
        "stage1_pct": stage1_pct,
        "confirm_of_screened_pct": confirm_of_screened,
        "fp_rate_pct": fp_rate,
    }


def fmt_ci(lo: float, hi: float) -> str:
    return f"[{lo:.2f},{hi:.2f}]"


def main() -> None:
    print("=" * 78)
    print("M2-B Final Production Cascade Models (script 13)")
    print("=" * 78)

    original = load_original_cohort()
    v2 = load_v2_cohort()
    combined = pd.concat([original, v2], ignore_index=True)

    print(f"Original cohort: {len(original)} patients, {int(original['at_risk'].sum())} at-risk")
    print(f"V2 after QC + INS 399 valid: {len(v2)} patients, {int(v2['at_risk'].sum())} at-risk")
    print(f"Combined confirmation cohort: {len(combined)} patients")

    _, _, meta_orig = build_features(original)
    feat_orig, y_orig, _ = build_features(original, cohort_medians=meta_orig)
    feat_comb, y_comb, meta_comb = build_features(combined)

    X_screen = feat_orig[SCREEN_FEATURES].values.astype(float)
    X_confirm = feat_comb[CONFIRM_FEATURES].values.astype(float)

    screen_model, screen_metrics, screen_summary = train_model(
        "Final_Cascade_Screening_R1",
        SCREEN_FEATURES,
        X_screen,
        y_orig,
        meta_orig,
        save_screening_thresh=True,
        save_balanced_thresh=False,
        save_confirm_thresh=False,
    )

    confirm_model, confirm_metrics, confirm_summary = train_model(
        "Final_Cascade_Confirmation_ConfigB",
        CONFIRM_FEATURES,
        X_confirm,
        y_comb,
        meta_comb,
        save_screening_thresh=False,
        save_balanced_thresh=True,
        save_confirm_thresh=True,
    )

    M2_MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(screen_model, M2_MODELS / "final_cascade_screening_model.joblib")
    joblib.dump(confirm_model, M2_MODELS / "final_cascade_confirmation_model.joblib")

    with open(M2_MODELS / "final_cascade_screening_metrics.json", "w") as f:
        json.dump(screen_metrics, f, indent=2)
    with open(M2_MODELS / "final_cascade_confirmation_metrics.json", "w") as f:
        json.dump(confirm_metrics, f, indent=2)

    print("\nSaved:")
    print(f"  {M2_MODELS / 'final_cascade_screening_model.joblib'}")
    print(f"  {M2_MODELS / 'final_cascade_screening_metrics.json'}")
    print(f"  {M2_MODELS / 'final_cascade_confirmation_model.joblib'}")
    print(f"  {M2_MODELS / 'final_cascade_confirmation_metrics.json'}")

    funnel = compute_funnel(
        y_comb,
        screen_model.predict_proba(feat_comb[SCREEN_FEATURES].values.astype(float))[:, 1],
        confirm_summary["cal_probs"],
        screen_summary["thresholds"]["screening"]["threshold"],
        confirm_summary["thresholds"]["confirmation"]["threshold"],
    )

    print()
    print("CASCADE FUNNEL (combined training data, calibrated probs):")
    print(f" Stage 1 Screening: flags {funnel['stage1_pct']:.1f}% of all patients")
    print(
        f" Of those, Stage 2 Confirmation catches {funnel['confirm_of_screened_pct']:.1f}% "
        f"as definitive"
    )
    print(f" Estimated false positive rate reaching confirmation: {funnel['fp_rate_pct']:.1f}%")

    def row(label: str, rep: float, ci: tuple[float, float], scr, bal, con, overfit: bool, n: int) -> None:
        scr_s = f"{scr:.2f}" if scr is not None else "N/A"
        bal_s = f"{bal:.2f}" if bal is not None else "N/A"
        con_s = f"{con:.2f}" if con is not None else "N/A"
        print(
            f"{label:<28} | {rep:.3f}       | {fmt_ci(*ci):<23} | "
            f"{scr_s:<19} | {bal_s:<19} | {con_s:<19} | "
            f"{'Yes' if overfit else 'No':<7} | {n}"
        )

    print()
    print(
        f"{'Metric':<28} | {'Rep AUC':<13} | {'95% CI':<23} | "
        f"{'Screening Youden':<19} | {'Balanced Youden':<19} | {'Confirm Youden':<19} | "
        f"{'Overfit':<7} | Training patients"
    )
    print("-" * 130)
    row(
        "Original M2",
        ORIGINAL_M2["rep_auc"],
        (ORIGINAL_M2["ci_lower"], ORIGINAL_M2["ci_upper"]),
        ORIGINAL_M2["scr_j"],
        ORIGINAL_M2["bal_j"],
        ORIGINAL_M2["con_j"],
        False,
        ORIGINAL_M2["n"],
    )
    row(
        "Final Cascade Screening",
        screen_summary["rep_auc"],
        screen_summary["ci"],
        screen_summary["scr_j"],
        screen_summary["bal_j"],
        screen_summary["con_j"],
        screen_summary["overfit"],
        screen_summary["n"],
    )
    row(
        "Final Cascade Confirmation",
        confirm_summary["rep_auc"],
        confirm_summary["ci"],
        None,
        confirm_summary["bal_j"],
        confirm_summary["con_j"],
        confirm_summary["overfit"],
        confirm_summary["n"],
    )

    bal_delta = confirm_summary["bal_j"] - ORIGINAL_M2["bal_j"]
    con_delta = confirm_summary["con_j"] - ORIGINAL_M2["con_j"]
    auc_delta = confirm_summary["rep_auc"] - ORIGINAL_M2["rep_auc"]

    print()
    print("Improvement summary:")
    print(f"  Balanced Youden: 0.59 → {confirm_summary['bal_j']:.2f} ({bal_delta:+.2f})")
    print(f"  Confirmation Youden: 0.59 → {confirm_summary['con_j']:.2f} ({con_delta:+.2f})")
    print(f"  Confirmation AUC: 0.896 → {confirm_summary['rep_auc']:.3f} ({auc_delta:+.3f})")
    print(f"  Training patients: 129 → {confirm_summary['n']} (confirmation model)")


if __name__ == "__main__":
    main()
