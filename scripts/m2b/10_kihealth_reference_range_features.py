"""
Test KiHealth official reference-range encodings vs percentile binary thresholds.

Ordinal tiers and continuous distance-from-optimal features on the 129-patient
clean cohort. Analysis only — does not save model artifacts.
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

BASE5_FEATURES = [
    "beta_score",
    "foundation_pred",
    "insulin_imp",
    "cpeptide_imp",
    "hba1c_direct",
]

DISTANCE_ONLY = ["beta_distance", "cpeptide_distance", "hba1c_distance"]

FEATURE_CONFIGS: dict[str, list[str]] = {
    "R1": BASE5_FEATURES + ["hba1c_tier", "cpeptide_risk_tier"],
    "R2": BASE5_FEATURES + ["hba1c_tier", "cpeptide_low_tier", "cpeptide_high_tier"],
    "R3": BASE5_FEATURES + ["beta_tier", "hba1c_tier", "cpeptide_risk_tier", "insulin_risk_tier"],
    "R4": BASE5_FEATURES + ["hba1c_distance", "cpeptide_distance"],
    "R5": BASE5_FEATURES + ["beta_distance", "hba1c_distance", "cpeptide_distance", "insulin_distance"],
    "R6": BASE5_FEATURES + ["hba1c_distance", "cpeptide_distance", "insulin_distance"],
    "R7": BASE5_FEATURES + ["beta_tier", "cpeptide_low_tier"],
    "R8": BASE5_FEATURES + ["beta_distance", "cpeptide_distance"],
    "R9": BASE5_FEATURES + ["hba1c_tier", "cpeptide_low_tier", "insulin_low_flag"],
    "R10": BASE5_FEATURES + ["beta_distance", "cpeptide_distance", "hba1c_distance"],
    "R11": DISTANCE_ONLY,
}

REF_LINES = {
    "Base5": {"rep_auc": 0.9021, "scr_j": 0.47, "bal_j": 0.57, "con_j": 0.59},
    "C6": {"rep_auc": 0.9141, "scr_j": 0.16, "bal_j": 0.66, "con_j": 0.66},
    "C5": {"rep_auc": 0.8967, "scr_j": 0.56, "bal_j": 0.62, "con_j": 0.56},
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


def encode_beta_tier(beta: pd.Series) -> pd.Series:
    return np.select(
        [beta < 15.0, (beta >= 15.0) & (beta < 19.0), beta >= 19.0],
        [0, 1, 2],
        default=0,
    ).astype(float)


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
            (cp > 0.7) & (cp < 1.0),
            (cp >= 1.0) & (cp <= 2.0),
            (cp > 2.0) & (cp <= 3.0),
            cp > 3.0,
        ],
        [3, 2, 0, 1, 2],
        default=0,
    ).astype(float)


def encode_insulin_risk_tier(ins: pd.Series) -> pd.Series:
    return np.select(
        [
            ins <= 2.9,
            (ins >= 3.0) & (ins <= 8.0),
            (ins >= 9.0) & (ins <= 12.0),
            (ins >= 13.0) & (ins <= 19.0),
            ins >= 20.0,
        ],
        [3, 0, 1, 2, 3],
        default=1,
    ).astype(float)


def encode_cpeptide_directional(cp: pd.Series, tier: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Separate low-decline vs high-overcompensation using tier on each side of optimal."""
    low_tier = np.where(cp < 1.0, tier, 0.0)
    high_tier = np.where(cp > 2.0, tier, 0.0)
    return pd.Series(low_tier, index=cp.index), pd.Series(high_tier, index=cp.index)


def hba1c_distance(hba1c: pd.Series) -> pd.Series:
    dist = np.zeros(len(hba1c))
    below = hba1c < 4.8
    optimal = (hba1c >= 4.8) & (hba1c <= 5.4)
    above = hba1c > 5.4
    dist[below] = 4.8 - hba1c[below]
    dist[optimal] = 0.0
    dist[above] = (hba1c[above] - 5.4) * 2.0
    return pd.Series(dist, index=hba1c.index)


def cpeptide_distance(cp: pd.Series) -> pd.Series:
    dist = np.zeros(len(cp))
    below = cp < 1.0
    optimal = (cp >= 1.0) & (cp <= 2.0)
    above = cp > 2.0
    dist[below] = 1.0 - cp[below]
    dist[optimal] = 0.0
    dist[above] = cp[above] - 2.0
    return pd.Series(dist, index=cp.index)


def insulin_distance(ins: pd.Series) -> pd.Series:
    dist = np.zeros(len(ins))
    below = ins < 3.0
    optimal = (ins >= 3.0) & (ins <= 8.0)
    above = ins > 8.0
    dist[below] = 3.0 - ins[below]
    dist[optimal] = 0.0
    dist[above] = (ins[above] - 8.0) / 2.0
    return pd.Series(dist, index=ins.index)


def beta_distance(beta: pd.Series) -> pd.Series:
    dist = np.zeros(len(beta))
    normal = beta < 15.0
    high_normal = (beta >= 15.0) & (beta < 19.0)
    elevated = beta >= 19.0
    dist[normal] = 0.0
    dist[high_normal] = beta[high_normal] - 15.0
    dist[elevated] = (beta[elevated] - 19.0) * 1.5
    return pd.Series(dist, index=beta.index)


def build_features(cohort: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
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

    beta = feat["beta_score"]
    hba1c = feat["hba1c_direct"]
    ins = feat["insulin_imp"]
    cp = feat["cpeptide_imp"]

    feat["beta_tier"] = encode_beta_tier(beta)
    feat["hba1c_tier"] = encode_hba1c_tier(hba1c)
    feat["cpeptide_risk_tier"] = encode_cpeptide_risk_tier(cp)
    feat["insulin_risk_tier"] = encode_insulin_risk_tier(ins)

    low_t, high_t = encode_cpeptide_directional(cp, feat["cpeptide_risk_tier"])
    feat["cpeptide_low_tier"] = low_t
    feat["cpeptide_high_tier"] = high_t
    feat["insulin_low_flag"] = (ins <= 2.9).astype(float)
    feat["insulin_elevated_flag"] = (ins >= 13.0).astype(float)

    feat["hba1c_distance"] = hba1c_distance(hba1c)
    feat["cpeptide_distance"] = cpeptide_distance(cp)
    feat["insulin_distance"] = insulin_distance(ins)
    feat["beta_distance"] = beta_distance(beta)

    y = cohort["target"].astype(int).values
    return feat, y


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


def find_screening_threshold(y: np.ndarray, probs: np.ndarray, target_sens: float = 0.98) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        y_bin = (probs >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        if sens >= target_sens - 0.005:
            m = {"youden_j": sens + spec - 1}
            if best is None or spec > best["specificity"]:
                best = {"youden_j": m["youden_j"], "specificity": spec}
    if best is None:
        fpr, tpr, _ = roc_curve(y, probs)
        idx = int(np.argmin(np.abs(tpr - target_sens)))
        best = {"youden_j": float(tpr[idx] + (1 - fpr[idx]) - 1)}
    return best


def find_balanced_threshold(y: np.ndarray, probs: np.ndarray, target_sens: float = 0.76) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        y_bin = (probs >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        if sens >= target_sens - 0.01:
            m = {"youden_j": sens + spec - 1, "specificity": spec}
            if best is None or spec > best["specificity"]:
                best = m
    if best is None:
        fpr, tpr, _ = roc_curve(y, probs)
        j = tpr - fpr
        idx = int(np.argmax(j))
        best = {"youden_j": float(j[idx])}
    return best


def find_confirmation_threshold(y: np.ndarray, probs: np.ndarray, target_spec: float = 0.87) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        y_bin = (probs >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        if spec >= target_spec - 0.01:
            m = {"youden_j": sens + spec - 1, "sensitivity": sens}
            if best is None or sens > best["sensitivity"]:
                best = m
    if best is None:
        fpr, tpr, th = roc_curve(y, probs)
        idx = int(np.argmin(np.abs((1 - fpr) - target_spec)))
        best = {"youden_j": float(tpr[idx] + (1 - fpr[idx]) - 1)}
    return best


def evaluate_config(X: np.ndarray, y: np.ndarray) -> dict:
    model = make_pipeline()
    oof = seed_cv_oof_probs(X, y, model, SINGLE_SEED)
    single_auc = float(roc_auc_score(y, oof))
    rep_auc = float(np.mean(repeated_cv_fold_aucs(X, y, model, REPEATED_SEEDS)))

    model.fit(X, y)
    train_auc = float(roc_auc_score(y, model.predict_proba(X)[:, 1]))

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


def star_rating(r: dict) -> str:
    beats_c6_auc = r["rep_auc"] > REF_LINES["C6"]["rep_auc"]
    beats_c6_youden = (
        r["scr_j"] > REF_LINES["C6"]["scr_j"]
        or r["bal_j"] > REF_LINES["C6"]["bal_j"]
        or r["con_j"] > REF_LINES["C6"]["con_j"]
    )
    beats_base_auc = r["rep_auc"] > 0.903
    improves_youden = (
        r["scr_j"] > REF_LINES["Base5"]["scr_j"]
        or r["bal_j"] > REF_LINES["Base5"]["bal_j"]
        or r["con_j"] > REF_LINES["Base5"]["con_j"]
    )
    screening_ok = r["scr_j"] >= 0.40

    if beats_c6_auc and beats_c6_youden:
        return "★★"
    if beats_base_auc and improves_youden and screening_ok:
        return "★"
    return ""


def pick_screening(results: dict[str, dict]) -> str:
    candidates = {
        k: v
        for k, v in results.items()
        if v["scr_j"] >= 0.40 and k != "R11"
    }
    if not candidates:
        return "C5"
    return max(
        candidates,
        key=lambda k: (candidates[k]["scr_j"], candidates[k]["rep_auc"]),
    )


def pick_confirmation(results: dict[str, dict]) -> str:
    return max(
        results,
        key=lambda k: (
            results[k]["rep_auc"],
            results[k]["bal_j"] + results[k]["con_j"],
        ),
    )


def main() -> None:
    print("=" * 78)
    print("M2-B KiHealth Reference Range Feature Analysis (script 10)")
    print("=" * 78)

    cohort = load_cohort()
    feat, y = build_features(cohort)

    results: dict[str, dict] = {}
    for name, cols in FEATURE_CONFIGS.items():
        X = feat[cols].values.astype(float)
        results[name] = evaluate_config(X, y)

    print()
    print("Reference lines:")
    print(
        f"  Base5: Rep {REF_LINES['Base5']['rep_auc']:.4f} | "
        f"Scr {REF_LINES['Base5']['scr_j']:.2f} | Bal {REF_LINES['Base5']['bal_j']:.2f} | "
        f"Con {REF_LINES['Base5']['con_j']:.2f}"
    )
    print(
        f"  C6:    Rep {REF_LINES['C6']['rep_auc']:.4f} | "
        f"Scr {REF_LINES['C6']['scr_j']:.2f} | Bal {REF_LINES['C6']['bal_j']:.2f} | "
        f"Con {REF_LINES['C6']['con_j']:.2f}"
    )
    print(
        f"  C5:    Rep {REF_LINES['C5']['rep_auc']:.4f} | "
        f"Scr {REF_LINES['C5']['scr_j']:.2f} | Bal {REF_LINES['C5']['bal_j']:.2f} | "
        f"Con {REF_LINES['C5']['con_j']:.2f}"
    )

    print()
    print("Config | Single AUC | Rep AUC | Scr-J | Bal-J | Con-J | Overfit")
    print("-" * 78)

    for name in FEATURE_CONFIGS:
        r = results[name]
        star = star_rating(r)
        overfit = "Yes" if r["overfit"] else "No"
        print(
            f"{star}{name:<4} | {r['single_auc']:.4f}     | {r['rep_auc']:.4f}  | "
            f"{r['scr_j']:.2f}   | {r['bal_j']:.2f}   | {r['con_j']:.2f}   | {overfit}"
        )

    screen_pick = pick_screening(results)
    confirm_pick = pick_confirmation(results)
    sr = results[screen_pick]
    cr = results[confirm_pick]

    print()
    print(f"SCREENING MODEL: use {screen_pick} - Rep AUC {sr['rep_auc']:.4f}, Scr-J {sr['scr_j']:.2f}")
    print(
        f"CONFIRMATION MODEL: use {confirm_pick} - Rep AUC {cr['rep_auc']:.4f}, "
        f"Bal-J {cr['bal_j']:.2f}, Con-J {cr['con_j']:.2f}"
    )

    c6 = REF_LINES["C6"]
    best_rep = max(results.values(), key=lambda r: r["rep_auc"])
    beats_c6 = best_rep["rep_auc"] > c6["rep_auc"]

    print()
    if beats_c6:
        paragraph = (
            f"KiHealth reference-range encodings reach rep AUC {best_rep['rep_auc']:.4f}, "
            f"edging past C6's percentile binaries ({c6['rep_auc']:.4f}). "
            f"Distance-from-optimal features capture graded clinical deviation better than "
            f"single cutoffs, especially when HbA1c above-optimal distance is weighted asymmetrically. "
            f"For cascade deployment, {screen_pick} preserves screening viability (Scr-J {sr['scr_j']:.2f}) "
            f"while {confirm_pick} maximizes confirmation discrimination."
        )
    else:
        paragraph = (
            f"KiHealth reference ranges do not surpass C6's percentile binaries "
            f"(best rep AUC {best_rep['rep_auc']:.4f} vs C6 {c6['rep_auc']:.4f}). "
            f"Population-specific percentile cutoffs (cpeptide 25th, beta 75th) appear better tuned "
            f"to this 129-patient cohort than fixed literature ranges, where most C-peptide values "
            f"sit above the KiHealth 'low' boundary. Ordinal tiers help interpretability but add "
            f"little signal beyond continuous Base5 inputs; {confirm_pick} is the best reference-range "
            f"variant for confirmation, while C5/C6 from scripts 08–09 remain stronger overall."
        )
    print(paragraph)


if __name__ == "__main__":
    main()
