"""
Train and save two purpose-built cascade models on the 129-patient clean cohort.

MODEL 1 (C5): Screening — Base5 + cpeptide_low, optimized for ~98% sensitivity.
MODEL 2 (C6): Confirmation — Base5 + beta_high + cpeptide_low, balanced + confirmation only.
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

SINGLE_SEED = 42
REPEATED_SEEDS = list(range(10))
N_FOLDS = 5
N_BOOT = 1000
OVERFIT_GAP = 0.05

BASE5_FEATURES = [
    "beta_score",
    "foundation_pred",
    "insulin_imp",
    "cpeptide_imp",
    "hba1c_direct",
]
C5_FEATURES = BASE5_FEATURES + ["cpeptide_low"]
C6_FEATURES = BASE5_FEATURES + ["beta_high", "cpeptide_low"]


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


def load_cohort() -> pd.DataFrame:
    df = pd.read_csv(GOOD_ONES / "KiHealth_Unified_Clean.csv")
    mask = df["target"].notna() & df["beta_score"].notna() & df["hba1c"].notna()
    cohort = df.loc[mask].copy()
    print(f"n patients after filter: {len(cohort)}, at-risk: {int(cohort['target'].sum())}")
    return cohort


def build_features(cohort: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, dict]:
    foundation_model = joblib.load(M2_MODELS / "foundation_combined.joblib")
    foundation_scaler = joblib.load(M2_MODELS / "foundation_scaler.joblib")

    med_insulin = float(cohort["insulin"].median())
    med_cpeptide = float(cohort["cpeptide"].median())
    med_age = float(cohort["age"].median())
    med_bmi = float(cohort["bmi"].median())

    feat = pd.DataFrame(index=cohort.index)
    feat["beta_score"] = cohort["beta_score"].astype(float)
    feat["hba1c_direct"] = cohort["hba1c"].astype(float)
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

    cp_25th = float(np.percentile(feat["cpeptide_imp"], 25))
    beta_75th = float(np.percentile(feat["beta_score"], 75))
    feat["cpeptide_low"] = (feat["cpeptide_imp"] <= cp_25th).astype(int)
    feat["beta_high"] = (feat["beta_score"] >= beta_75th).astype(int)

    meta = {
        "median_insulin": med_insulin,
        "median_cpeptide": med_cpeptide,
        "median_age": med_age,
        "median_bmi": med_bmi,
        "cp_25th": cp_25th,
        "beta_75th": beta_75th,
    }
    y = cohort["target"].astype(int).values
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
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
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


def train_cascade_model(
    name: str,
    feature_cols: list[str],
    X: np.ndarray,
    y: np.ndarray,
    meta: dict,
    *,
    compute_screening: bool,
    compute_balanced: bool,
    compute_confirmation: bool,
) -> tuple[CalibratedClassifierCV, dict, dict]:
    base_model = make_pipeline()
    fold_aucs = repeated_cv_fold_aucs(X, y, base_model, REPEATED_SEEDS)
    rep_mean = float(np.mean(fold_aucs))
    rep_std = float(np.std(fold_aucs))

    oof = seed_cv_oof_probs(X, y, base_model, SINGLE_SEED)
    single_auc = float(roc_auc_score(y, oof))
    ci_lo, ci_hi = bootstrap_auc_ci(y, oof)

    base_model.fit(X, y)
    train_auc = float(roc_auc_score(y, base_model.predict_proba(X)[:, 1]))
    overfit_gap = train_auc - single_auc

    calibrated = CalibratedClassifierCV(base_model, method="isotonic", cv=3)
    calibrated.fit(X, y)
    cal_probs = calibrated.predict_proba(X)[:, 1]

    screen_m = find_screening_threshold(y, oof, 0.98)
    bal_m = find_balanced_threshold(y, oof, 0.76)
    con_m = find_confirmation_threshold(y, oof, 0.87)

    thresholds: dict[str, dict] = {}
    if compute_screening:
        thresholds["screening"] = screen_m
    if compute_balanced:
        thresholds["balanced"] = bal_m
    if compute_confirmation:
        thresholds["confirmation"] = con_m

    youden_j = {
        "screening": screen_m["youden_j"] if compute_screening else None,
        "balanced": bal_m["youden_j"],
        "confirmation": con_m["youden_j"],
    }

    metrics = {
        "model_type": name,
        "features": feature_cols,
        "kihealth_patients": int(len(y)),
        "kihealth_at_risk": int(y.sum()),
        "cv_auc_single_seed": single_auc,
        "cv_auc_repeated_mean": rep_mean,
        "cv_auc_repeated_std": rep_std,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "train_auc": train_auc,
        "overfit_gap": float(overfit_gap),
        "overfit_flag": overfit_gap > OVERFIT_GAP,
        "thresholds": thresholds,
        "youden_j": youden_j,
        **meta,
    }

    summary = {
        "rep_auc": rep_mean,
        "rep_std": rep_std,
        "scr_j": youden_j["screening"],
        "bal_j": youden_j["balanced"],
        "con_j": youden_j["confirmation"],
        "overfit": overfit_gap > OVERFIT_GAP,
        "oof_probs": oof,
        "cal_probs": cal_probs,
        "thresholds": thresholds,
    }
    return calibrated, metrics, summary


def compute_cascade_funnel(
    y: np.ndarray,
    screen_probs: np.ndarray,
    confirm_probs: np.ndarray,
    screen_thresh: float,
    bal_thresh: float,
    con_thresh: float,
) -> dict[str, float]:
    n = len(y)
    screen_pos = screen_probs >= screen_thresh
    bal_pos = confirm_probs >= bal_thresh
    con_pos = confirm_probs >= con_thresh

    stage1_pct = 100.0 * screen_pos.sum() / n
    screened_n = int(screen_pos.sum())
    bal_of_screened = 100.0 * (screen_pos & bal_pos).sum() / screened_n if screened_n else 0.0
    con_of_screened = 100.0 * (screen_pos & con_pos).sum() / screened_n if screened_n else 0.0

    con_reached = screen_pos & con_pos
    fp_at_con = (con_reached & (y == 0)).sum()
    fp_rate_all = 100.0 * fp_at_con / n

    return {
        "stage1_pct": stage1_pct,
        "bal_of_screened_pct": bal_of_screened,
        "con_of_screened_pct": con_of_screened,
        "fp_rate_reaching_confirmation_pct": fp_rate_all,
    }


def main() -> None:
    print("=" * 72)
    print("M2-B Cascade Model Training (script 09)")
    print("=" * 72)

    cohort = load_cohort()
    feat, y, meta = build_features(cohort)

    X_screen = feat[C5_FEATURES].values.astype(float)
    X_confirm = feat[C6_FEATURES].values.astype(float)

    print(f"C-peptide low threshold: {meta['cp_25th']:.2f} (25th percentile)")
    print(f"Beta score high threshold: {meta['beta_75th']:.2f} (75th percentile)")

    screen_model, screen_metrics, screen_summary = train_cascade_model(
        "Cascade_Screening_C5",
        C5_FEATURES,
        X_screen,
        y,
        meta,
        compute_screening=True,
        compute_balanced=False,
        compute_confirmation=False,
    )

    confirm_model, confirm_metrics, confirm_summary = train_cascade_model(
        "Cascade_Confirmation_C6",
        C6_FEATURES,
        X_confirm,
        y,
        meta,
        compute_screening=False,
        compute_balanced=True,
        compute_confirmation=True,
    )

    M2_MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(screen_model, M2_MODELS / "cascade_screening_model.joblib")
    joblib.dump(confirm_model, M2_MODELS / "cascade_confirmation_model.joblib")

    with open(M2_MODELS / "cascade_screening_metrics.json", "w") as f:
        json.dump(screen_metrics, f, indent=2)
    with open(M2_MODELS / "cascade_confirmation_metrics.json", "w") as f:
        json.dump(confirm_metrics, f, indent=2)

    print("\nSaved:")
    print(f"  {M2_MODELS / 'cascade_screening_model.joblib'}")
    print(f"  {M2_MODELS / 'cascade_screening_metrics.json'}")
    print(f"  {M2_MODELS / 'cascade_confirmation_model.joblib'}")
    print(f"  {M2_MODELS / 'cascade_confirmation_metrics.json'}")

    print()
    print("Model | Rep CV AUC | Scr-J | Bal-J | Con-J | Overfit")
    print("-" * 60)

    for label, summary, scr_na in [
        ("Screening (C5)", screen_summary, False),
        ("Confirmation (C6)", confirm_summary, True),
    ]:
        scr = "N/A" if scr_na or summary["scr_j"] is None else f"{summary['scr_j']:.2f}"
        bal = f"{summary['bal_j']:.2f}" if summary["bal_j"] is not None else "N/A"
        con = f"{summary['con_j']:.2f}" if summary["con_j"] is not None else "N/A"
        overfit = "Yes" if summary["overfit"] else "No"
        print(
            f"{label:<20} | {summary['rep_auc']:.4f}±{summary['rep_std']:.3f} | "
            f"{scr:>5} | {bal:>5} | {con:>5} | {overfit}"
        )

    funnel = compute_cascade_funnel(
        y,
        screen_summary["cal_probs"],
        confirm_summary["cal_probs"],
        screen_summary["thresholds"]["screening"]["threshold"],
        confirm_summary["thresholds"]["balanced"]["threshold"],
        confirm_summary["thresholds"]["confirmation"]["threshold"],
    )

    print()
    print("CASCADE FUNNEL (on training data):")
    print(f" Stage 1 Screening: flags {funnel['stage1_pct']:.1f}% of all patients")
    print(
        f" Of those, Stage 2 Balanced catches {funnel['bal_of_screened_pct']:.1f}% "
        f"as high confidence"
    )
    print(
        f" Of those, Stage 2 Confirmation catches {funnel['con_of_screened_pct']:.1f}% "
        f"as definitive"
    )
    print(
        f" Estimated false positive rate reaching confirmation: "
        f"{funnel['fp_rate_reaching_confirmation_pct']:.1f}%"
    )


if __name__ == "__main__":
    main()
