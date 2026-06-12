"""
Test KiHealth reference-range distance weighting on 162-patient INS 399 cohort.

Final comparison vs script 13 CONFIG B (Base5, rep AUC 0.9150).
Analysis only — does not save model artifacts.
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
V2_STEM = "V2_Reference_Range_Samples_with_Demographics_01JUN2026"

SINGLE_SEED = 42
REPEATED_SEEDS = list(range(10))
N_FOLDS = 5
OVERFIT_GAP = 0.05

BASE5 = [
    "beta_score_399",
    "foundation_pred",
    "insulin_imp",
    "cpeptide_imp",
    "hba1c_direct",
]

B_BASE_REF = {"rep_auc": 0.9150, "bal_j": 0.67, "con_j": 0.64, "scr_j": 0.51}

CONFIGS: dict[str, list[str]] = {
    "B_base": BASE5,
    "W1": BASE5 + ["hba1c_distance_weighted", "cpeptide_distance"],
    "W2": BASE5 + ["hba1c_distance_weighted", "cpeptide_distance", "insulin_distance"],
    "W3": BASE5 + ["beta_distance", "cpeptide_distance"],
    "W4": BASE5 + ["hba1c_distance_weighted", "cpeptide_distance", "insulin_distance", "beta_distance"],
    "W5": BASE5 + ["beta_distance", "cpeptide_distance", "hba1c_distance_weighted"],
    "W6": BASE5 + ["cpeptide_distance"],
    "W7": BASE5 + ["beta_distance"],
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
        ["beta_score_399", "hba1c", "insulin", "cpeptide", "age", "bmi", "at_risk"]
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


def hba1c_distance_weighted(hba1c: pd.Series) -> pd.Series:
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
    dist[above] = (cp[above] - 2.0) * 0.5
    return pd.Series(dist, index=cp.index)


def insulin_distance(ins: pd.Series) -> pd.Series:
    dist = np.zeros(len(ins))
    below = ins < 3.0
    optimal = (ins >= 3.0) & (ins <= 8.0)
    above = ins > 8.0
    dist[below] = 3.0 - ins[below]
    dist[optimal] = 0.0
    dist[above] = (ins[above] - 8.0) * 0.5
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

    feat["hba1c_distance_weighted"] = hba1c_distance_weighted(feat["hba1c_direct"])
    feat["cpeptide_distance"] = cpeptide_distance(feat["cpeptide_imp"])
    feat["insulin_distance"] = insulin_distance(feat["insulin_imp"])
    feat["beta_distance"] = beta_distance(feat["beta_score_399"])

    y = cohort["at_risk"].astype(int).values
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
    best_thresh = 0.5
    for thresh in np.arange(0.05, 0.96, 0.005):
        y_bin = (probs >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        if sens >= target_sens - 0.005:
            m = {"threshold": round(float(thresh), 2), "sensitivity": sens, "specificity": spec, "youden_j": sens + spec - 1}
            if best is None or spec > best["specificity"]:
                best = m
                best_thresh = float(thresh)
    if best is None:
        fpr, tpr, th = roc_curve(y, probs)
        idx = int(np.argmin(np.abs(tpr - target_sens)))
        best_thresh = float(th[idx]) if idx < len(th) else 0.5
        y_bin = (probs >= best_thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        best = {
            "threshold": round(best_thresh, 2),
            "sensitivity": tp / (tp + fn),
            "specificity": tn / (tn + fp),
            "youden_j": tp / (tp + fn) + tn / (tn + fp) - 1,
        }
    return best


def find_balanced_threshold(y: np.ndarray, probs: np.ndarray, target_sens: float = 0.76) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        y_bin = (probs >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        if sens >= target_sens - 0.01:
            m = {"threshold": round(float(thresh), 2), "sensitivity": sens, "specificity": spec, "youden_j": sens + spec - 1}
            if best is None or spec > best["specificity"]:
                best = m
    if best is None:
        fpr, tpr, th = roc_curve(y, probs)
        j = tpr - fpr
        idx = int(np.argmax(j))
        t = float(th[idx]) if idx < len(th) else 0.5
        y_bin = (probs >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        best = {
            "threshold": round(t, 2),
            "sensitivity": tp / (tp + fn),
            "specificity": tn / (tn + fp),
            "youden_j": tp / (tp + fn) + tn / (tn + fp) - 1,
        }
    return best


def find_confirmation_threshold(y: np.ndarray, probs: np.ndarray, target_spec: float = 0.87) -> dict:
    best = None
    for thresh in np.arange(0.05, 0.96, 0.005):
        y_bin = (probs >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        if spec >= target_spec - 0.01:
            m = {"threshold": round(float(thresh), 2), "sensitivity": sens, "specificity": spec, "youden_j": sens + spec - 1}
            if best is None or sens > best["sensitivity"]:
                best = m
    if best is None:
        y_bin = (probs >= 0.58).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_bin).ravel()
        best = {
            "threshold": 0.58,
            "sensitivity": tp / (tp + fn),
            "specificity": tn / (tn + fp),
            "youden_j": tp / (tp + fn) + tn / (tn + fp) - 1,
        }
    return best


def evaluate_config(feat: pd.DataFrame, y: np.ndarray, feature_cols: list[str]) -> dict:
    X = feat[feature_cols].values.astype(float)
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
        "oof": oof,
        "thresholds": {"screening": screen, "balanced": balanced, "confirmation": confirm},
    }


def star_rating(r: dict, base: dict) -> str:
    beats_double = r["rep_auc"] > base["rep_auc"] and (r["bal_j"] >= 0.67 or r["con_j"] >= 0.67)
    improves_youden = (
        r["scr_j"] >= base["scr_j"] + 0.01
        or r["bal_j"] >= base["bal_j"] + 0.01
        or r["con_j"] >= base["con_j"] + 0.01
    )
    if beats_double:
        return "★★"
    if r["rep_auc"] > 0.910 and improves_youden:
        return "★"
    return ""


def main() -> None:
    print("=" * 78)
    print("M2-B Reference Range Distance Weighting — 162 INS 399 Cohort (script 14)")
    print("=" * 78)

    original = load_original_cohort()
    v2 = load_v2_cohort()
    combined = pd.concat([original, v2], ignore_index=True)

    print(f"Combined cohort: {len(combined)} patients, {int(combined['at_risk'].sum())} at-risk")
    print(
        f"Reference: CONFIG B (script 13) — Rep AUC {B_BASE_REF['rep_auc']:.4f}, "
        f"Bal-J {B_BASE_REF['bal_j']:.2f}, Con-J {B_BASE_REF['con_j']:.2f}"
    )

    feat, y = build_features(combined)
    results: dict[str, dict] = {}
    for name, cols in CONFIGS.items():
        results[name] = evaluate_config(feat, y, cols)

    base = results["B_base"]
    starred: list[str] = []

    print()
    print("Config | Single AUC | Rep AUC | Scr-J | Bal-J | Con-J | Overfit")
    print("-" * 78)
    for name in CONFIGS:
        r = results[name]
        star = star_rating(r, B_BASE_REF)
        if star:
            starred.append(name)
        overfit = "Yes" if r["overfit"] else "No"
        print(
            f"{star}{name:<7} | {r['single_auc']:.4f}     | {r['rep_auc']:.4f}  | "
            f"{r['scr_j']:.2f}   | {r['bal_j']:.2f}   | {r['con_j']:.2f}   | {overfit}"
        )

    if starred:
        print()
        for name in starred:
            r = results[name]
            print(f"--- Threshold analysis: {name} ---")
            for mode in ("screening", "balanced", "confirmation"):
                t = r["thresholds"][mode]
                print(
                    f"  {mode.capitalize():14s} thresh={t['threshold']:.2f}  "
                    f"sens={t['sensitivity']:.1%}  spec={t['specificity']:.1%}  "
                    f"Youden J={t['youden_j']:.2f}"
                )

    best_name = max(CONFIGS, key=lambda k: (results[k]["rep_auc"], results[k]["bal_j"] + results[k]["con_j"]))
    best = results[best_name]
    improves = best["rep_auc"] > B_BASE_REF["rep_auc"] + 0.001 or (
        best["bal_j"] > B_BASE_REF["bal_j"] + 0.01 or best["con_j"] > B_BASE_REF["con_j"] + 0.01
    )

    print()
    print("FINAL RECOMMENDATION:")
    print(f"Does reference range distance weighting improve CONFIG B? {'YES' if improves and best_name != 'B_base' else 'NO'}")
    print(f"Best config: {best_name} Rep AUC {best['rep_auc']:.4f}, Bal-J {best['bal_j']:.2f}, Con-J {best['con_j']:.2f}")

    print()
    if improves and best_name != "B_base":
        print(
            f"KiHealth distance weighting adds marginal signal on the 162-patient INS 399 cohort: "
            f"{best_name} edges CONFIG B (rep AUC {best['rep_auc']:.4f} vs {B_BASE_REF['rep_auc']:.4f}). "
            f"For the clinical team, the continuous distance features encode how far each biomarker sits "
            f"from KiHealth optimal ranges, but the gain is small because Base5 already supplies raw "
            f"HbA1c, C-peptide, insulin, and INS 399 values that a linear model can scale directly."
        )
    else:
        print(
            f"Reference range distance weighting does not improve on CONFIG B (best rep AUC "
            f"{best['rep_auc']:.4f} vs B_base {base['rep_auc']:.4f}). Clifford's sliding-scale intuition "
            f"is clinically interpretable but redundant once INS 399 site-specific values and V2 patients "
            f"are in the model — the breakthrough came from using INS 399 instead of the three-site average, "
            f"not from re-encoding the same biomarkers as distance-from-optimal. Declare CONFIG B "
            f"(script 13 final_cascade_confirmation_model) complete for production."
        )


if __name__ == "__main__":
    main()
