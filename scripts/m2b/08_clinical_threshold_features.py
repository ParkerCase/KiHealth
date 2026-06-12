"""
Test ADA clinical threshold boundaries as explicit binary features (analysis only).

Compares Base5 (script 07 reference) against clinical-threshold feature combinations
using repeated CV and single-seed evaluation. Does not save model artifacts.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
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
OVERFIT_GAP = 0.05
AUC_WIN_MARGIN = 0.003

BASE5_FEATURES = [
    "beta_score",
    "foundation_pred",
    "insulin_imp",
    "cpeptide_imp",
    "hba1c_direct",
]

FEATURE_CONFIGS: dict[str, list[str]] = {
    "Base5": BASE5_FEATURES,
    "C1": BASE5_FEATURES + ["hba1c_prediabetic"],
    "C2": BASE5_FEATURES + ["hba1c_prediabetic", "cpeptide_low"],
    "C3": BASE5_FEATURES + ["hba1c_prediabetic", "hba1c_diabetic_range"],
    "C4": BASE5_FEATURES + ["hba1c_prediabetic", "cpeptide_low", "hba1c_diabetic_range"],
    "C5": BASE5_FEATURES + ["cpeptide_low"],
    "C6": BASE5_FEATURES + ["beta_high", "cpeptide_low"],
    "C7": BASE5_FEATURES + ["hba1c_borderline_normal"],
    "C8": BASE5_FEATURES + ["hba1c_prediabetic", "cpeptide_low", "beta_high"],
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


def load_cohort() -> pd.DataFrame:
    df = pd.read_csv(GOOD_ONES / "KiHealth_Unified_Clean.csv")
    mask = df["target"].notna() & df["beta_score"].notna() & df["hba1c"].notna()
    cohort = df.loc[mask].copy()
    print(f"n patients after filter: {len(cohort)}, at-risk: {int(cohort['target'].sum())}")
    return cohort


def build_features(cohort: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, dict[str, float]]:
    foundation_model = joblib.load(M2_MODELS / "foundation_combined.joblib")
    foundation_scaler = joblib.load(M2_MODELS / "foundation_scaler.joblib")

    med_insulin = cohort["insulin"].median()
    med_cpeptide = cohort["cpeptide"].median()
    med_age = cohort["age"].median()
    med_bmi = cohort["bmi"].median()

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

    hba1c = feat["hba1c_direct"]
    feat["hba1c_prediabetic"] = ((hba1c >= 5.7) & (hba1c < 6.5)).astype(int)
    feat["hba1c_diabetic_range"] = (hba1c >= 6.5).astype(int)
    feat["hba1c_borderline_normal"] = ((hba1c >= 5.5) & (hba1c < 5.7)).astype(int)

    cp_25th = float(np.percentile(feat["cpeptide_imp"], 25))
    beta_75th = float(np.percentile(feat["beta_score"], 75))
    feat["cpeptide_low"] = (feat["cpeptide_imp"] <= cp_25th).astype(int)
    feat["beta_high"] = (feat["beta_score"] >= beta_75th).astype(int)

    thresholds = {"cp_25th": cp_25th, "beta_75th": beta_75th}
    y = cohort["target"].astype(int).values
    return feat, y, thresholds


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


def metrics_at_threshold(y: np.ndarray, probs: np.ndarray, thresh: float) -> dict:
    y_bin = (probs >= thresh).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    return {
        "sensitivity": float(sens),
        "specificity": float(spec),
        "youden_j": float(sens + spec - 1),
    }


def find_screening_threshold(y: np.ndarray, probs: np.ndarray, target_sens: float = 0.98) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        m = metrics_at_threshold(y, probs, float(thresh))
        if m["sensitivity"] >= target_sens - 0.005:
            if best is None or m["specificity"] > best["specificity"]:
                best = m
    if best is None:
        fpr, tpr, th = roc_curve(y, probs)
        idx = int(np.argmin(np.abs(tpr - target_sens)))
        t = float(th[idx]) if idx < len(th) else 0.5
        best = metrics_at_threshold(y, probs, t)
    return best


def find_balanced_threshold(y: np.ndarray, probs: np.ndarray, target_sens: float = 0.76) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        m = metrics_at_threshold(y, probs, float(thresh))
        if m["sensitivity"] >= target_sens - 0.01:
            if best is None or m["specificity"] > best["specificity"]:
                best = m
    if best is None:
        fpr, tpr, th = roc_curve(y, probs)
        j = tpr - fpr
        idx = int(np.argmax(j))
        t = float(th[idx]) if idx < len(th) else 0.5
        best = metrics_at_threshold(y, probs, t)
    return best


def find_confirmation_threshold(y: np.ndarray, probs: np.ndarray, target_spec: float = 0.87) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        m = metrics_at_threshold(y, probs, float(thresh))
        if m["specificity"] >= target_spec - 0.01:
            if best is None or m["sensitivity"] > best["sensitivity"]:
                best = m
    if best is None:
        best = metrics_at_threshold(y, probs, 0.58)
    return best


def evaluate_config(X: np.ndarray, y: np.ndarray) -> dict[str, float | bool]:
    model = make_pipeline()
    oof = seed_cv_oof_probs(X, y, model, SINGLE_SEED)
    single_auc = roc_auc_score(y, oof)
    rep_auc = float(np.mean(repeated_cv_fold_aucs(X, y, model, REPEATED_SEEDS)))

    model.fit(X, y)
    train_auc = roc_auc_score(y, model.predict_proba(X)[:, 1])

    screen = find_screening_threshold(y, oof, 0.98)
    balanced = find_balanced_threshold(y, oof, 0.76)
    confirm = find_confirmation_threshold(y, oof, 0.87)

    return {
        "single_auc": single_auc,
        "rep_auc": rep_auc,
        "scr_j": screen["youden_j"],
        "bal_j": balanced["youden_j"],
        "con_j": confirm["youden_j"],
        "overfit": train_auc - single_auc > OVERFIT_GAP,
    }


def main() -> None:
    print("=" * 72)
    print("M2-B Clinical Threshold Feature Analysis (script 08)")
    print("=" * 72)

    cohort = load_cohort()
    feat, y, clinical_thresholds = build_features(cohort)

    print(f"C-peptide low threshold: {clinical_thresholds['cp_25th']:.2f} (25th percentile)")
    print(f"Beta score high threshold: {clinical_thresholds['beta_75th']:.2f} (75th percentile)")

    results: dict[str, dict] = {}
    for name, cols in FEATURE_CONFIGS.items():
        X = feat[cols].values.astype(float)
        results[name] = evaluate_config(X, y)

    base = results["Base5"]
    print()
    print("Config | Single AUC | Rep AUC | Scr-J | Bal-J | Con-J | Overfit")
    print("-" * 72)

    clear_winners: list[str] = []
    for name in FEATURE_CONFIGS:
        r = results[name]
        beats_auc = r["rep_auc"] > base["rep_auc"] + AUC_WIN_MARGIN
        beats_youden = (
            r["scr_j"] > base["scr_j"]
            or r["bal_j"] > base["bal_j"]
            or r["con_j"] > base["con_j"]
        )
        star = "★" if beats_auc and beats_youden else ""
        if star:
            clear_winners.append(name)

        overfit = "Yes" if r["overfit"] else "No"
        print(
            f"{star}{name:<5} | {r['single_auc']:.4f}     | {r['rep_auc']:.4f}  | "
            f"{r['scr_j']:.2f}   | {r['bal_j']:.2f}   | {r['con_j']:.2f}   | {overfit}"
        )

    if clear_winners:
        best_name = max(clear_winners, key=lambda n: results[n]["rep_auc"])
        winner = results[best_name]
        reason = (
            f"{best_name} lifts repeated CV AUC by {winner['rep_auc'] - base['rep_auc']:.4f} "
            f"over Base5 and improves at least one clinical-mode Youden J, suggesting explicit "
            f"threshold flags help the linear model separate borderline phenotypes."
        )
        print(f"\nRECOMMENDATION: {best_name}")
    else:
        best_name = "Base5"
        top_alt = max(
            (n for n in FEATURE_CONFIGS if n != "Base5"),
            key=lambda n: results[n]["rep_auc"],
        )
        alt = results[top_alt]
        reason = (
            f"No config clears both the +{AUC_WIN_MARGIN:.3f} repeated-CV margin and a Youden "
            f"improvement; continuous HbA1c/C-peptide already capture most signal "
            f"(best alt {top_alt}: rep AUC {alt['rep_auc']:.4f} vs Base5 {base['rep_auc']:.4f})."
        )
        print("\nRECOMMENDATION: Base5 if no clear winner")

    print(reason)


if __name__ == "__main__":
    main()
