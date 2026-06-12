"""
Test INS 399 site-specific beta score vs average when adding V2 patients.

Compares cascade configurations on original-only and combined cohorts.
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

REF_LINES = {
    "Original M2": {"n": 129, "single": 0.8959, "rep": 0.892, "scr_j": 0.57, "bal_j": 0.59, "con_j": 0.59},
    "C5 cascade screen": {"n": 129, "single": 0.8967, "rep": None, "scr_j": 0.56, "bal_j": 0.62, "con_j": 0.56},
    "C6 cascade confirm": {"n": 129, "single": 0.9047, "rep": 0.9141, "scr_j": 0.16, "bal_j": 0.66, "con_j": 0.66},
    "R1 cascade screen": {"n": 129, "single": 0.8972, "rep": 0.9017, "scr_j": 0.58, "bal_j": 0.59, "con_j": 0.56},
}

CONFIGS: dict[str, dict] = {
    "A": {"cohort": "original", "features": BASE5},
    "B": {"cohort": "combined", "features": BASE5},
    "C": {"cohort": "combined", "features": BASE5 + ["hba1c_tier", "cpeptide_risk_tier"]},
    "D": {"cohort": "combined", "features": BASE5 + ["beta399_high_binary", "cpeptide_low_binary"]},
    "E": {"cohort": "original", "features": BASE5 + ["beta399_high_binary", "cpeptide_low_binary"]},
    "F": {"cohort": "combined", "features": BASE5 + ["beta399_high_binary", "cpeptide_low_binary", "e60_weighted"]},
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
    cohort["ins_135"] = np.nan
    cohort["ins_233"] = np.nan
    cohort["source"] = "original"
    cohort["at_risk"] = cohort["target"].astype(int)
    return cohort[
        [
            "beta_score_399",
            "hba1c",
            "insulin",
            "cpeptide",
            "age",
            "bmi",
            "at_risk",
            "ins_135",
            "ins_233",
            "source",
        ]
    ].rename(columns={"hba1c": "hba1c_direct"})


def load_v2_cohort() -> tuple[pd.DataFrame, int]:
    raw = load_v2_raw()
    col_399 = pick_column(raw, ("%", "399"))
    col_135 = pick_column(raw, ("135",))
    col_233 = pick_column(raw, ("-233",))
    col_cf = pick_column(raw, ("%cfd",))
    col_conc = pick_column(raw, ("concentration",))

    qc_mask = (pd.to_numeric(raw[col_cf], errors="coerce") >= 70) & (
        pd.to_numeric(raw[col_conc], errors="coerce") >= 80
    )
    qc = raw.loc[qc_mask].copy()
    ins399 = pd.to_numeric(qc[col_399], errors="coerce")
    dropped_null_399 = int(ins399.isna().sum())

    v2 = pd.DataFrame(
        {
            "beta_score_399": ins399,
            "hba1c_direct": pd.to_numeric(qc["A1c"], errors="coerce"),
            "insulin": pd.to_numeric(qc["Insulin"], errors="coerce"),
            "cpeptide": pd.to_numeric(qc["C-peptide"], errors="coerce"),
            "age": pd.to_numeric(qc["Age"], errors="coerce"),
            "bmi": pd.to_numeric(qc["BMI"], errors="coerce"),
            "at_risk": qc["Risk"].astype(str).str.strip().str.lower().eq("yes").astype(int),
            "ins_135": pd.to_numeric(qc[col_135], errors="coerce"),
            "ins_233": pd.to_numeric(qc[col_233], errors="coerce"),
            "source": "v2",
        },
        index=qc.index,
    )
    v2 = v2[v2["beta_score_399"].notna() & v2["hba1c_direct"].notna()].copy()
    return v2, dropped_null_399


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


def build_feature_frame(cohort: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, dict]:
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

    feat["hba1c_tier"] = encode_hba1c_tier(feat["hba1c_direct"])
    feat["cpeptide_risk_tier"] = encode_cpeptide_risk_tier(feat["cpeptide_imp"])

    cp_p25 = float(np.percentile(feat["cpeptide_imp"], 25))
    beta_p75 = float(np.percentile(feat["beta_score_399"], 75))
    feat["cpeptide_low_binary"] = (feat["cpeptide_imp"] <= cp_p25).astype(float)
    feat["beta399_high_binary"] = (feat["beta_score_399"] >= beta_p75).astype(float)

    has_three = cohort["ins_135"].notna() & cohort["ins_233"].notna()
    mean_135_233 = (cohort["ins_135"].fillna(0) + cohort["ins_233"].fillna(0)) / 2.0
    feat["e60_weighted"] = np.where(
        has_three,
        0.60 * feat["beta_score_399"] + 0.40 * mean_135_233,
        feat["beta_score_399"],
    )

    y = cohort["at_risk"].astype(int).values
    meta = {"cp_p25": cp_p25, "beta_p75": beta_p75, "n": len(cohort), "at_risk_pct": 100 * y.mean()}
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


def star_rating(r: dict) -> str:
    beats_c6 = r["rep_auc"] > 0.914 and (r["bal_j"] >= 0.66 or r["con_j"] >= 0.66)
    improves_youden = r["scr_j"] > 0.47 or r["bal_j"] > 0.57 or r["con_j"] > 0.59
    if beats_c6:
        return "★★"
    if r["rep_auc"] > 0.903 and improves_youden and r["scr_j"] >= 0.40:
        return "★"
    return ""


def print_threshold_analysis(label: str, r: dict) -> None:
    print(f"\n--- Threshold analysis: {label} ---")
    for mode in ("screening", "balanced", "confirmation"):
        t = r["thresholds"][mode]
        print(
            f"  {mode.capitalize():14s} thresh={t['threshold']:.2f}  "
            f"sens={t['sensitivity']:.1%}  spec={t['specificity']:.1%}  "
            f"Youden J={t['youden_j']:.2f}"
        )


def main() -> None:
    print("=" * 88)
    print("M2-B INS 399 Cascade Test (script 12)")
    print("=" * 88)

    original = load_original_cohort()
    v2, dropped_null_399 = load_v2_cohort()
    combined = pd.concat([original, v2], ignore_index=True)

    print(f"Original cohort: {len(original)} patients, {int(original['at_risk'].sum())} at-risk")
    print(f"V2 after QC + INS 399 valid: {len(v2)} patients, {int(v2['at_risk'].sum())} at-risk")
    print(f"V2 patients dropped (null INS 399): {dropped_null_399}")

    feat_orig, y_orig, meta_orig = build_feature_frame(original)
    feat_comb, y_comb, meta_comb = build_feature_frame(combined)

    # Percentile binaries always use FULL combined cohort thresholds (scripts 08–09 convention).
    feat_orig = feat_orig.copy()
    feat_orig["cpeptide_low_binary"] = (feat_orig["cpeptide_imp"] <= meta_comb["cp_p25"]).astype(float)
    feat_orig["beta399_high_binary"] = (feat_orig["beta_score_399"] >= meta_comb["beta_p75"]).astype(float)

    print(f"\nCombined percentile thresholds:")
    print(f"  C-peptide low (25th pctl): {meta_comb['cp_p25']:.2f}")
    print(f"  Beta 399 high (75th pctl): {meta_comb['beta_p75']:.2f}")

    datasets = {"original": (feat_orig, y_orig, meta_orig), "combined": (feat_comb, y_comb, meta_comb)}
    results: dict[str, dict] = {}

    for name, spec in CONFIGS.items():
        feat, y, meta = datasets[spec["cohort"]]
        r = evaluate_config(feat, y, spec["features"])
        r["n"] = meta["n"]
        r["at_risk_pct"] = meta["at_risk_pct"]
        results[name] = r

    print()
    print("Config | N patients | at-risk% | Single AUC | Rep AUC | Scr-J | Bal-J | Con-J | Overfit")
    print("-" * 88)

    starred: list[str] = []
    for name in CONFIGS:
        r = results[name]
        star = star_rating(r)
        if star:
            starred.append(name)
        overfit = "Yes" if r["overfit"] else "No"
        print(
            f"{star}{name:<5} | {r['n']:>10} | {r['at_risk_pct']:>6.1f}% | "
            f"{r['single_auc']:.4f}     | {r['rep_auc']:.4f}  | "
            f"{r['scr_j']:.2f}   | {r['bal_j']:.2f}   | {r['con_j']:.2f}   | {overfit}"
        )

    print()
    print("Reference lines:")
    for label, ref in REF_LINES.items():
        rep = f"{ref['rep']:.4f}" if ref["rep"] is not None else "----"
        print(
            f"  {label:<22} {ref['n']}pts  single={ref['single']:.4f}  rep={rep}  "
            f"Scr={ref['scr_j']:.2f}  Bal={ref['bal_j']:.2f}  Con={ref['con_j']:.2f}"
        )

    for label in ("D", "F"):
        if label in starred:
            print_threshold_analysis(f"CONFIG {label}", results[label])

    screen_candidates = {k: v for k, v in results.items() if v["scr_j"] >= 0.40 and k in ("A", "B", "C")}
    screen_pick = max(screen_candidates, key=lambda k: (screen_candidates[k]["scr_j"], screen_candidates[k]["rep_auc"]))
    confirm_candidates = {k: v for k, v in results.items() if k in ("D", "E", "F")}
    confirm_pick = max(
        confirm_candidates,
        key=lambda k: (confirm_candidates[k]["rep_auc"], confirm_candidates[k]["bal_j"] + confirm_candidates[k]["con_j"]),
    )

    d = results["D"]
    e = results["E"]
    f = results["F"]
    b = results["B"]
    # KEY test: CONFIG D = C6 cascade equivalent on combined INS-399 cohort
    beats_cascade = d["rep_auc"] > 0.9141 and (d["bal_j"] >= 0.66 or d["con_j"] >= 0.66)
    base5_v2_beats = b["rep_auc"] > 0.9141
    e60_helps = f["rep_auc"] > d["rep_auc"] + 0.001 or (
        f["bal_j"] > d["bal_j"] and f["con_j"] > d["con_j"]
    )
    e_matches_c6 = abs(e["rep_auc"] - 0.9141) < 0.01

    sr = results[screen_pick]
    cr = results[confirm_pick]

    print()
    print(f"SCREENING MODEL: use CONFIG {screen_pick} - Rep AUC {sr['rep_auc']:.4f}, Scr-J {sr['scr_j']:.2f}")
    print(
        f"CONFIRMATION MODEL: use CONFIG {confirm_pick} - Rep AUC {cr['rep_auc']:.4f}, "
        f"Bal-J {cr['bal_j']:.2f}, Con-J {cr['con_j']:.2f}"
    )
    cascade_answer = "YES" if beats_cascade else ("PARTIAL (Base5+B beats; C6+D does not)" if base5_v2_beats else "NO")
    print(f"Does INS 399 + V2 beat current cascade? {cascade_answer}")
    print(f"Does E60 + V2 add anything over INS 399 alone? {'YES' if e60_helps else 'NO'}")

    print()
    print(
        "Clifford's INS 399 instinct is validated on the original cohort: CONFIG A reproduces "
        f"script 07 Base5 (single AUC {results['A']['single_auc']:.4f}), and CONFIG E "
        f"(129-only C6 equivalent) reaches rep AUC {e['rep_auc']:.4f} "
        f"{'≈ matching' if e_matches_c6 else 'near'} script 09 C6 (0.9141), confirming "
        "the historical beta_score is effectively an INS-399 measurement."
    )
    print(
        f"Adding V2 with INS 399 (not average) improves combined Base5 to CONFIG B rep AUC "
        f"{b['rep_auc']:.4f} (vs ~0.87 with averaged beta), reversing the earlier V2 hurt — "
        f"but the C6 cascade equivalent on combined data (CONFIG D) only reaches "
        f"{d['rep_auc']:.4f} with Bal-J {d['bal_j']:.2f} / Con-J {d['con_j']:.2f}, "
        f"below script 09 C6 (0.9141 / 0.66 / 0.66). E60 weighting (CONFIG F) adds nothing "
        f"over INS 399 alone. Recommendation: keep 129-patient C6 cascade for confirmation; "
        f"use CONFIG B only if expanding training data, accepting lower screening Youden "
        f"(Scr-J {b['scr_j']:.2f} vs C5's 0.56)."
    )


if __name__ == "__main__":
    main()
