"""
Age-adjusted reference ranges for INS 399 (Beta Score), built empirically.

Jenna's question: natural beta cell apoptosis rises with age, so an INS 399 of 18
may mean something different at 25 than at 75. This script tests that hypothesis
against the pooled KiHealth cohorts and derives reference bands from the data.

Design rules enforced here:
  * No hardcoded reference values or clinical thresholds. Every band is a
    percentile of observed not-at-risk data.
  * Reference bands are built from NOT-AT-RISK patients only, so they describe a
    healthy baseline rather than the mixed population.
  * The age/beta relationship is tested statistically before it is presented as
    real; figures that would imply a trend are suppressed when the data cannot
    support one.
  * Cardinal 2026 "unascertained" donors (said No, A1c normal, never adjudicated)
    are labeled unknown rather than negative.

Outputs:
  outputs/age_adjusted_reference_ranges.json
  outputs/figures/age_vs_beta_scatter.png
  outputs/figures/age_group_boxplot.png
  outputs/figures/age_reference_bands.png   (only when data supports it)
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

BASE = Path(__file__).resolve().parents[2]
GOOD_ONES = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "Good-Ones-Kihealth"
M2_MODELS = BASE / "Diabetes-KiHealth" / "TL-KiHealth" / "M2_Models"
OUTPUTS = BASE / "outputs"
FIGURES = OUTPUTS / "figures"

UNIFIED_PATH = GOOD_ONES / "KiHealth_Unified_Clean.csv"
CARDINAL_2026_PATH = GOOD_ONES / "cardinal_health_2026_relabel.csv"
STRICT_CLEAN_PATH = GOOD_ONES / "m2b_features_strict_clean.csv"
V2_DEMOGRAPHICS_PATH = (
    BASE / "deliverables" / "M1_clean" / "data"
    / "V2_Reference_Range_Samples_with_Demographics_01JUN2026.csv"
)
BIOIVT_PATH = GOOD_ONES / "BioIVT.csv"
CARDINAL_LEGACY_PATH = GOOD_ONES / "Cardinal.csv"

JSON_PATH = OUTPUTS / "age_adjusted_reference_ranges.json"
# outputs/ is gitignored, so the Streamlit app needs its own committed copies.
UI_JSON_PATH = BASE / "kihealth_ui" / "age_adjusted_reference_ranges.json"
UI_FIGURES = BASE / "kihealth_ui" / "figures"

# Statistical validity rules (not clinical thresholds).
MIN_N_PER_BIN = 5           # bins below this are reported but excluded from ranges
MIN_N_FOR_REGRESSION = 10   # below this a slope estimate is not interpretable
MIN_N_PER_BOX = 3           # box plot needs at least this many points per group
SIGNIFICANCE_P = 0.10       # threshold for calling the age trend confirmed

# Biological plausibility bounds, used only to drop data-entry errors (the source
# files contain ages of -0.3, 0.16 and 125.59, and one negative % unmethylated).
# These are not clinical thresholds and every exclusion is printed.
AGE_MIN_PLAUSIBLE = 1.0
AGE_MAX_PLAUSIBLE = 110.0
BETA_MIN_PLAUSIBLE = 0.0  # % unmethylated cannot be negative

AGE_BINS = [
    ("under 20", -np.inf, 20),
    ("20-30", 20, 30),
    ("30-40", 30, 40),
    ("40-50", 40, 50),
    ("50-60", 50, 60),
    ("60-70", 60, 70),
    ("70+", 70, np.inf),
]

HIGHLIGHT_DONOR = "109384"

COHORT_CLINICAL = "Clinical Training"
COHORT_CARDINAL_2026 = "Cardinal Health 2026"
COHORT_V2 = "V2 Reference Range"
COHORT_BIOIVT_LEGACY = "BioIVT (legacy)"
COHORT_CARDINAL_LEGACY = "Cardinal (legacy)"

COHORT_MARKERS = {
    COHORT_CLINICAL: "o",
    COHORT_CARDINAL_2026: "s",
    COHORT_V2: "^",
    COHORT_BIOIVT_LEGACY: "D",
    COHORT_CARDINAL_LEGACY: "v",
}

RISK_COLORS = {"at_risk": "#f97316", "not_at_risk": "#2563eb", "unknown": "#9ca3af"}

MASTER_COLUMNS = ["donor_id", "cohort", "age", "beta_score_399", "at_risk"]


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def log(msg: str = "") -> None:
    print(msg)


def section(title: str) -> None:
    log()
    log("=" * 78)
    log(title)
    log("=" * 78)


def to_num(series: pd.Series) -> pd.Series:
    """Numeric coercion that also strips percent signs and stray whitespace."""
    cleaned = (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


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


def find_column(columns, *keywords: str) -> str | None:
    """Case-insensitive search for the first column containing all keywords.

    Matching is on whole words: a bare substring test makes "age" match
    "% Unmethylated Average", which silently swaps a methylation percentage in
    for patient age.
    """
    patterns = [re.compile(rf"(?<![a-z0-9]){re.escape(k.lower())}(?![a-z0-9])") for k in keywords]
    for col in columns:
        name = " ".join(str(col).replace("\xa0", " ").split()).lower()
        if all(p.search(name) for p in patterns):
            return col
    return None


def empty_master() -> pd.DataFrame:
    return pd.DataFrame(columns=MASTER_COLUMNS)


def bin_label_for_age(age: float) -> str | None:
    if pd.isna(age):
        return None
    for label, low, high in AGE_BINS:
        if low <= age < high:
            return label
    return None


# ----------------------------------------------------------------------------
# STEP 1: load cohorts
# ----------------------------------------------------------------------------
def load_clinical_training() -> pd.DataFrame:
    if not UNIFIED_PATH.exists():
        log(f"Skipping {COHORT_CLINICAL} cohort - file not found: {UNIFIED_PATH.name}")
        return empty_master()

    df = pd.read_csv(UNIFIED_PATH)
    out = pd.DataFrame(
        {
            "donor_id": df.get("Donor ID", pd.Series(index=df.index, dtype=object)).map(fmt_id),
            "cohort": COHORT_CLINICAL,
            "age": to_num(df["age"]),
            "beta_score_399": to_num(df["beta_score"]),
            "at_risk": pd.to_numeric(df["target"], errors="coerce"),
        }
    )
    return out


def load_cardinal_2026() -> pd.DataFrame:
    if not CARDINAL_2026_PATH.exists():
        log(f"Skipping {COHORT_CARDINAL_2026} cohort - file not found: {CARDINAL_2026_PATH.name}")
        return empty_master()

    df = pd.read_csv(CARDINAL_2026_PATH)

    # Unascertained donors said "No" and had a normal A1c but were never
    # clinically adjudicated. They are unknown, not confirmed negatives.
    at_risk = pd.Series(np.nan, index=df.index, dtype="float64")
    confident = pd.to_numeric(df.get("at_risk_confident"), errors="coerce")
    at_risk[confident == 0] = 0.0
    if "unascertained" in df.columns:
        at_risk[pd.to_numeric(df["unascertained"], errors="coerce") == 1] = np.nan
    at_risk[confident == 1] = 1.0

    n_unknown = int(at_risk.isna().sum())
    log(
        f"  {COHORT_CARDINAL_2026}: {n_unknown} unascertained donors labeled "
        "at_risk=unknown (not counted as healthy)"
    )

    return pd.DataFrame(
        {
            "donor_id": df["donor_id"].map(fmt_id),
            "cohort": COHORT_CARDINAL_2026,
            "age": to_num(df["age_years"]),
            "beta_score_399": to_num(df["ins_399_pct_unmeth"]),
            "at_risk": at_risk,
        }
    )


def load_v2_reference_range() -> tuple[pd.DataFrame, dict]:
    """V2 age lives in the demographics file; the modeling file carries no ID."""
    meta: dict = {}
    if not V2_DEMOGRAPHICS_PATH.exists():
        log(f"Skipping {COHORT_V2} cohort - no age data found "
            f"(missing {V2_DEMOGRAPHICS_PATH.name})")
        return empty_master(), {"status": "skipped_no_age_source"}

    demo = pd.read_csv(V2_DEMOGRAPHICS_PATH)
    age_col = find_column(demo.columns, "age")
    col_399 = find_column(demo.columns, "unmethylated", "399")
    risk_col = find_column(demo.columns, "risk")

    if age_col is None or col_399 is None:
        log(f"Skipping {COHORT_V2} cohort - no age data found")
        return empty_master(), {"status": "skipped_no_age_column"}

    demo_399 = to_num(demo[col_399])

    # The strict-clean modeling file has no donor identifier, so the only link
    # back to demographics is the INS 399 value itself. Report how well it joins.
    matched_mask = pd.Series(False, index=demo.index)
    if STRICT_CLEAN_PATH.exists():
        strict = pd.read_csv(STRICT_CLEAN_PATH)
        if "has_three_cpg_sites" in strict.columns:
            v2_strict = strict[strict["has_three_cpg_sites"].astype(str).str.lower() == "true"]
            strict_vals = set(to_num(v2_strict["ins_399_pct_unmeth"]).round(4).dropna())
            matched_mask = demo_399.round(4).isin(strict_vals)
            demo_vals = set(demo_399.round(4).dropna())
            strict_matched = sum(1 for v in strict_vals if v in demo_vals)
            meta["strict_clean_rows"] = int(len(v2_strict))
            meta["strict_rows_matched_to_demographics"] = int(strict_matched)
            meta["demographics_rows_matched_to_strict"] = int(matched_mask.sum())
            meta["join_key"] = "ins_399 value (no shared ID column)"
            log(
                f"  {COHORT_V2}: modeling file has no ID column, so it joins to demographics "
                f"only by INS 399 value ({strict_matched}/{len(v2_strict)} modeling rows matched). "
                "Using the demographics file directly as the cohort, since it is the "
                "original source of both age and INS 399."
            )

    at_risk = pd.Series(np.nan, index=demo.index, dtype="float64")
    if risk_col is not None:
        risk_text = demo[risk_col].astype(str).str.strip().str.lower()
        at_risk[risk_text.isin(["no", "n", "0", "false"])] = 0.0
        at_risk[risk_text.isin(["yes", "y", "1", "true"])] = 1.0

    out = pd.DataFrame(
        {
            "donor_id": demo[find_column(demo.columns, "uin") or demo.columns[0]].map(fmt_id),
            "cohort": COHORT_V2,
            "age": to_num(demo[age_col]),
            "beta_score_399": demo_399,
            "at_risk": at_risk,
        }
    )
    out["in_strict_model_set"] = matched_mask.values
    meta["status"] = "loaded"
    meta["rows"] = int(len(out))
    return out, meta


def load_legacy_table(path: Path, cohort: str) -> pd.DataFrame:
    """BioIVT.csv / Cardinal.csv carry two banner rows above the real header."""
    if not path.exists():
        log(f"Skipping {cohort} cohort - file not found: {path.name}")
        return empty_master()

    df = None
    for skip in (2, 0, 1, 3):
        try:
            candidate = pd.read_csv(path, skiprows=skip).dropna(axis=1, how="all")
        except Exception:
            continue
        if find_column(candidate.columns, "age") and find_column(candidate.columns, "unmethylated"):
            df = candidate
            break

    if df is None:
        log(f"Skipping {cohort} cohort - no age data found")
        return empty_master()

    age_col = find_column(df.columns, "age")
    beta_col = find_column(df.columns, "unmethylated")
    risk_col = find_column(df.columns, "at-risk", "binary") or find_column(df.columns, "at risk", "binary")
    id_col = find_column(df.columns, "donor id") or find_column(df.columns, "uin")

    if age_col is None:
        log(f"Skipping {cohort} cohort - no age data found")
        return empty_master()

    return pd.DataFrame(
        {
            "donor_id": df[id_col].map(fmt_id) if id_col else "",
            "cohort": cohort,
            "age": to_num(df[age_col]),
            "beta_score_399": to_num(df[beta_col]),
            "at_risk": pd.to_numeric(df[risk_col], errors="coerce") if risk_col else np.nan,
        }
    )


def deduplicate_against_reference(
    new_df: pd.DataFrame, reference: pd.DataFrame, cohort: str
) -> tuple[pd.DataFrame, dict]:
    """Drop legacy rows that are the same donor as a Clinical Training row.

    Removal happens only on donor ID, where identity is certain. An (age, beta)
    signature is too weak to delete on: rounded age collides constantly and many
    donors share beta = 0.00, so it flags patients who are genuinely distinct.
    Ambiguous overlap is therefore reported for review rather than removed.
    """
    info = {"input": int(len(new_df)), "duplicates_removed": 0, "kept": int(len(new_df))}
    if new_df.empty or reference.empty:
        return new_df, info

    ref_ids = {i for i in reference["donor_id"].map(fmt_id) if i}
    ids = new_df["donor_id"].map(fmt_id)
    dup_by_id = ids.isin(ref_ids) & (ids != "")

    # Distinctive = nonzero beta, so a match means more than "both were zero".
    ref_sig = {
        s for s in zip(reference["age"].round(0), reference["beta_score_399"].round(2))
        if s[1] not in (0.0, np.nan)
    }
    sig = list(zip(new_df["age"].round(0), new_df["beta_score_399"].round(2)))
    suspect = pd.Series([s in ref_sig for s in sig], index=new_df.index) & ~dup_by_id

    info.update(
        {
            "duplicates_removed": int(dup_by_id.sum()),
            "duplicates_by_donor_id": int(dup_by_id.sum()),
            "possible_overlap_not_removed": int(suspect.sum()),
            "possible_overlap_basis": "same rounded age and identical nonzero INS 399",
            "kept": int((~dup_by_id).sum()),
        }
    )

    if info["duplicates_removed"]:
        log(
            f"  {cohort}: {info['duplicates_removed']}/{info['input']} rows are the same donor IDs "
            f"as {COHORT_CLINICAL} - removed to avoid double counting; "
            f"{info['kept']} unique rows kept"
        )
    else:
        log(
            f"  {cohort}: no donor ID overlap with {COHORT_CLINICAL}; "
            f"all {info['kept']} rows kept as a distinct cohort"
        )
    if info["possible_overlap_not_removed"]:
        log(
            f"    Caution: {info['possible_overlap_not_removed']} rows share a rounded age and an "
            f"identical nonzero INS 399 with a {COHORT_CLINICAL} row. IDs differ, so they are kept; "
            "flagged in JSON for manual review."
        )
    return new_df.loc[~dup_by_id].copy(), info


def summarize_cohorts(df: pd.DataFrame) -> list[dict]:
    rows = []
    log()
    log(f"{'Cohort':<26} {'n':>5} {'at-risk':>9} {'not-at-risk':>13} {'unknown':>9}")
    log("-" * 66)
    for cohort, grp in df.groupby("cohort", sort=False):
        n_at = int((grp["at_risk"] == 1).sum())
        n_not = int((grp["at_risk"] == 0).sum())
        n_unk = int(grp["at_risk"].isna().sum())
        log(f"{cohort:<26} {len(grp):>5} {n_at:>9} {n_not:>13} {n_unk:>9}")
        rows.append(
            {
                "cohort": cohort,
                "n_total": int(len(grp)),
                "n_at_risk": n_at,
                "n_not_at_risk": n_not,
                "n_unknown": n_unk,
            }
        )
    n_at = int((df["at_risk"] == 1).sum())
    n_not = int((df["at_risk"] == 0).sum())
    n_unk = int(df["at_risk"].isna().sum())
    log("-" * 66)
    log(f"{'TOTAL':<26} {len(df):>5} {n_at:>9} {n_not:>13} {n_unk:>9}")
    return rows


# ----------------------------------------------------------------------------
# STEP 2: validate the age/beta relationship
# ----------------------------------------------------------------------------
def run_regression(df: pd.DataFrame, label: str) -> dict:
    sub = df.dropna(subset=["age", "beta_score_399"])
    n = int(len(sub))

    log()
    log(f"--- {label} (n={n}) ---")

    if n < MIN_N_FOR_REGRESSION:
        log(f"Interpretation: INSUFFICIENT DATA (n={n} < {MIN_N_FOR_REGRESSION} required)")
        return {
            "label": label,
            "n": n,
            "status": "insufficient_data",
            "interpretation": "INSUFFICIENT DATA",
        }

    fit = stats.linregress(sub["age"].to_numpy(float), sub["beta_score_399"].to_numpy(float))
    slope, intercept, r, p = fit.slope, fit.intercept, fit.rvalue, fit.pvalue

    confirmed = bool(slope > 0 and p < SIGNIFICANCE_P)
    interpretation = "CONFIRMED increasing" if confirmed else "FLAT"

    log(f"Slope: {slope:.2f} pp per year ({slope * 10:.2f} per decade)")
    log(f"R²: {r ** 2:.2f}")
    log(f"p-value: {p:.2f}")
    log(f"Interpretation: {interpretation}")
    if not confirmed:
        log(
            f"Note: age-beta relationship not statistically confirmed in current data "
            f"(n={n} {label.lower()} patients). Display ranges as descriptive only, "
            "not predictive."
        )

    return {
        "label": label,
        "n": n,
        "status": "fitted",
        "slope_per_year": round(float(slope), 4),
        "slope_per_decade": round(float(slope) * 10, 4),
        "intercept": round(float(intercept), 4),
        "r_squared": round(float(r ** 2), 4),
        "p_value": round(float(p), 6),
        "stderr": round(float(fit.stderr), 4),
        "significance_level": SIGNIFICANCE_P,
        "age_trend_confirmed": confirmed,
        "interpretation": interpretation,
    }


# ----------------------------------------------------------------------------
# STEP 3: reference ranges from not-at-risk patients
# ----------------------------------------------------------------------------
def build_age_bands(df: pd.DataFrame, label: str) -> dict:
    bands: dict[str, dict] = {}
    log()
    log(f"{label}")
    log(
        f"{'Age bin':<12} {'n':>4} {'mean':>7} {'median':>7} {'p10':>7} "
        f"{'p25':>7} {'p75':>7} {'p90':>7} {'max':>7}   status"
    )
    log("-" * 92)

    for name, low, high in AGE_BINS:
        vals = df.loc[
            (df["age"] >= low) & (df["age"] < high), "beta_score_399"
        ].dropna().to_numpy(float)
        n = int(len(vals))

        if n == 0:
            log(f"{name:<12} {0:>4} {'-':>7} {'-':>7} {'-':>7} {'-':>7} {'-':>7} {'-':>7} {'-':>7}   no data")
            bands[name] = {"n": 0, "usable": False, "status": "no data"}
            continue

        stats_block = {
            "n": n,
            "mean": round(float(np.mean(vals)), 2),
            "median": round(float(np.median(vals)), 2),
            "p10": round(float(np.percentile(vals, 10)), 2),
            "p25": round(float(np.percentile(vals, 25)), 2),
            "p75": round(float(np.percentile(vals, 75)), 2),
            "p90": round(float(np.percentile(vals, 90)), 2),
            "max": round(float(np.max(vals)), 2),
        }
        usable = n >= MIN_N_PER_BIN
        stats_block["usable"] = usable
        stats_block["status"] = "ok" if usable else f"insufficient data (n={n})"
        bands[name] = stats_block

        log(
            f"{name:<12} {n:>4} {stats_block['mean']:>7.2f} {stats_block['median']:>7.2f} "
            f"{stats_block['p10']:>7.2f} {stats_block['p25']:>7.2f} {stats_block['p75']:>7.2f} "
            f"{stats_block['p90']:>7.2f} {stats_block['max']:>7.2f}   {stats_block['status']}"
        )

    return bands


# ----------------------------------------------------------------------------
# STEP 4: figures
# ----------------------------------------------------------------------------
def save_figure(fig, name: str) -> Path:
    """Write to outputs/figures and mirror into kihealth_ui/figures for Streamlit."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path, dpi=300, bbox_inches="tight")
    if UI_FIGURES.parent.is_dir():
        UI_FIGURES.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, UI_FIGURES / name)
    return path


def load_reference_threshold_lines() -> list[dict]:
    """Only draw horizontal lines if a KiHealth reference range JSON supplies them."""
    lines: list[dict] = []
    for path in sorted(M2_MODELS.glob("*.json")) + sorted(OUTPUTS.glob("*reference_range*.json")):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        ref = data.get("reference_range") or data.get("beta_score_reference_range")
        if isinstance(ref, dict):
            for key, value in ref.items():
                if isinstance(value, (int, float)):
                    lines.append({"label": f"{key} ({path.name})", "value": float(value)})
    return lines


def regression_band(x: np.ndarray, y: np.ndarray, grid: np.ndarray):
    """Fitted line plus 95% CI for the mean response."""
    fit = stats.linregress(x, y)
    pred = fit.intercept + fit.slope * grid
    n = len(x)
    if n <= 2:
        return pred, None, None
    resid = y - (fit.intercept + fit.slope * x)
    s_err = np.sqrt(np.sum(resid ** 2) / (n - 2))
    sxx = np.sum((x - x.mean()) ** 2)
    if sxx == 0:
        return pred, None, None
    se_mean = s_err * np.sqrt(1.0 / n + (grid - x.mean()) ** 2 / sxx)
    tcrit = stats.t.ppf(0.975, n - 2)
    return pred, pred - tcrit * se_mean, pred + tcrit * se_mean


def figure_a_scatter(master: pd.DataFrame, not_at_risk: pd.DataFrame, reg_lines: list[dict]) -> Path:
    fig, ax = plt.subplots(figsize=(11, 7))

    for cohort, grp in master.groupby("cohort", sort=False):
        marker = COHORT_MARKERS.get(cohort, "o")
        for risk_key, mask in (
            ("at_risk", grp["at_risk"] == 1),
            ("not_at_risk", grp["at_risk"] == 0),
            ("unknown", grp["at_risk"].isna()),
        ):
            pts = grp[mask]
            if pts.empty:
                continue
            ax.scatter(
                pts["age"], pts["beta_score_399"],
                c=RISK_COLORS[risk_key], marker=marker, s=46,
                alpha=0.78, edgecolors="white", linewidths=0.6, zorder=3,
            )

    if len(not_at_risk) >= MIN_N_FOR_REGRESSION:
        x = not_at_risk["age"].to_numpy(float)
        y = not_at_risk["beta_score_399"].to_numpy(float)
        grid = np.linspace(x.min(), x.max(), 200)
        pred, lo, hi = regression_band(x, y, grid)
        if lo is not None:
            ax.fill_between(grid, lo, hi, color="#2563eb", alpha=0.15, zorder=2,
                            label="95% CI (not-at-risk fit)")
        ax.plot(grid, pred, color="#1d4ed8", lw=2.2, zorder=4,
                label="Regression: not-at-risk only")

    for line in reg_lines:
        ax.axhline(line["value"], color="#6b7280", ls="--", lw=1.2, zorder=1)
        ax.annotate(line["label"], xy=(ax.get_xlim()[1], line["value"]),
                    fontsize=8, color="#6b7280", ha="right", va="bottom")

    hl = master[master["donor_id"].astype(str) == HIGHLIGHT_DONOR]
    if not hl.empty:
        row = hl.iloc[0]
        ax.scatter([row["age"]], [row["beta_score_399"]], s=210, facecolors="none",
                   edgecolors="#dc2626", linewidths=2.2, zorder=6)
        ax.annotate(
            f"UIN {HIGHLIGHT_DONOR}\n{row['age']:.1f}y, INS 399 {row['beta_score_399']:.1f}%",
            xy=(row["age"], row["beta_score_399"]),
            xytext=(row["age"] + 6, row["beta_score_399"] + 6),
            fontsize=9, color="#dc2626", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.4), zorder=6,
        )

    risk_handles = [
        mpatches.Patch(color=RISK_COLORS["at_risk"], label="At-risk"),
        mpatches.Patch(color=RISK_COLORS["not_at_risk"], label="Not at-risk"),
        mpatches.Patch(color=RISK_COLORS["unknown"], label="Unknown / unascertained"),
    ]
    cohort_handles = [
        plt.Line2D([], [], color="#4b5563", marker=COHORT_MARKERS.get(c, "o"),
                   ls="", markersize=7, label=c)
        for c in master["cohort"].unique()
    ]
    first = ax.legend(handles=risk_handles, loc="upper left", fontsize=9, title="Risk status")
    ax.add_artist(first)
    ax.legend(handles=cohort_handles, loc="upper right", fontsize=8, title="Cohort")

    ax.set_xlabel("Age (years)", fontsize=11)
    ax.set_ylabel("INS 399 (% unmethylated)", fontsize=11)
    ax.set_title("INS 399 by Age — All KiHealth Cohorts", fontsize=14, fontweight="bold")
    ax.grid(alpha=0.25, ls=":")
    fig.text(0.5, 0.015, "Regression line fit to not-at-risk patients only",
             ha="center", fontsize=9, style="italic", color="#4b5563")
    fig.tight_layout(rect=(0, 0.035, 1, 1))

    path = save_figure(fig, "age_vs_beta_scatter.png")
    plt.close(fig)
    return path


def figure_b_boxplot(master: pd.DataFrame) -> tuple[Path | None, dict]:
    groups = [("20-40", 20, 40), ("40-60", 40, 60), ("60+", 60, np.inf)]
    data, labels, colors, included = [], [], [], {}

    for name, low, high in groups:
        band = master[(master["age"] >= low) & (master["age"] < high)]
        entry = {}
        for risk_key, mask in (("not_at_risk", band["at_risk"] == 0), ("at_risk", band["at_risk"] == 1)):
            vals = band.loc[mask, "beta_score_399"].dropna().to_numpy(float)
            entry[risk_key] = int(len(vals))
            if len(vals) >= MIN_N_PER_BOX:
                data.append(vals)
                labels.append(f"{name}\n{'not at-risk' if risk_key == 'not_at_risk' else 'at-risk'}\nn={len(vals)}")
                colors.append(RISK_COLORS[risk_key])
        included[name] = entry

    if not data:
        log(f"Figure B skipped - no age group reached n >= {MIN_N_PER_BOX} per risk category.")
        return None, included

    fig, ax = plt.subplots(figsize=(10, 6.5))
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=False)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.35)
        patch.set_edgecolor(color)
    for element in ("medians", "whiskers", "caps"):
        for artist in bp[element]:
            artist.set_color("#374151")
    for art in bp["medians"]:
        art.set_linewidth(2)

    rng = np.random.default_rng(0)
    for idx, (vals, color) in enumerate(zip(data, colors), start=1):
        jitter = rng.normal(0, 0.055, size=len(vals))
        ax.scatter(np.full(len(vals), idx) + jitter, vals, s=26, color=color,
                   alpha=0.85, edgecolors="white", linewidths=0.5, zorder=3)

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("INS 399 (% unmethylated)", fontsize=11)
    ax.set_title("INS 399 by Age Group and Risk Status", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.25, ls=":")
    fig.text(0.5, 0.015,
             f"Groups shown only where n >= {MIN_N_PER_BOX} per risk category; individual points overlaid",
             ha="center", fontsize=9, style="italic", color="#4b5563")
    fig.tight_layout(rect=(0, 0.035, 1, 1))

    path = save_figure(fig, "age_group_boxplot.png")
    plt.close(fig)
    return path, included


def figure_c_reference_bands(bands: dict, regression: dict) -> tuple[Path | None, dict]:
    usable = [name for name, b in bands.items() if b.get("usable")]
    with_data = [name for name, b in bands.items() if b.get("n", 0) > 0]
    enough_bins = bool(with_data) and len(usable) >= max(1, (len(with_data) + 1) // 2)
    significant = bool(regression.get("age_trend_confirmed"))
    gate = {
        "regression_significant": significant,
        "bins_with_data": len(with_data),
        "bins_meeting_min_n": len(usable),
        "min_n_per_bin": MIN_N_PER_BIN,
        "generated": bool(significant or enough_bins),
    }

    if not gate["generated"]:
        log()
        log("Insufficient data for reference band figure. "
            "Cardinal batch alone is not enough to establish age norms.")
        return None, gate

    order = [name for name, _, _ in AGE_BINS if bands.get(name, {}).get("usable")]
    xs = np.arange(len(order))
    p10 = np.array([bands[n]["p10"] for n in order])
    p25 = np.array([bands[n]["p25"] for n in order])
    p75 = np.array([bands[n]["p75"] for n in order])
    p90 = np.array([bands[n]["p90"] for n in order])
    vmax = np.array([bands[n]["max"] for n in order])
    med = np.array([bands[n]["median"] for n in order])

    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    ax.fill_between(xs, p90, vmax, color="#fca5a5", alpha=0.6, label="above p90 (above reference)")
    ax.fill_between(xs, p75, p90, color="#fde68a", alpha=0.7, label="p75–p90 (upper / borderline)")
    ax.fill_between(xs, p25, p75, color="#86efac", alpha=0.65, label="p25–p75 (typical range)")
    ax.fill_between(xs, p10, p25, color="#dbeafe", alpha=0.7, label="p10–p25 (lower tail)")
    ax.plot(xs, med, color="#166534", lw=2.4, marker="o", label="Median")
    ax.plot(xs, p90, color="#dc2626", lw=1.4, ls="--", label="p90")

    for i, name in enumerate(order):
        ax.annotate(f"n={bands[name]['n']}", xy=(i, vmax[i]), xytext=(0, 8),
                    textcoords="offset points", ha="center", fontsize=8, color="#4b5563")

    ax.set_xticks(xs)
    ax.set_xticklabels(order)
    ax.set_xlabel("Age group (years)", fontsize=11)
    ax.set_ylabel("INS 399 (% unmethylated)", fontsize=11)
    ax.set_title("Age-Adjusted INS 399 Reference Bands (not-at-risk patients)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(alpha=0.25, ls=":")

    caption = (
        f"Percentiles from not-at-risk patients only; bins with n < {MIN_N_PER_BIN} excluded. "
        f"Age trend {'statistically confirmed' if significant else 'NOT statistically confirmed'} "
        f"(p={regression.get('p_value', float('nan')):.2f}) — descriptive, not predictive."
    )
    fig.text(0.5, 0.015, caption, ha="center", fontsize=8.5, style="italic", color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    path = save_figure(fig, "age_reference_bands.png")
    plt.close(fig)
    return path, gate


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    section("STEP 1: LOAD COHORTS")
    clinical = load_clinical_training()
    cardinal_2026 = load_cardinal_2026()
    v2, v2_meta = load_v2_reference_range()
    bioivt = load_legacy_table(BIOIVT_PATH, COHORT_BIOIVT_LEGACY)
    cardinal_legacy = load_legacy_table(CARDINAL_LEGACY_PATH, COHORT_CARDINAL_LEGACY)

    # Legacy exports are earlier snapshots of the unified training file.
    bioivt, bioivt_dedup = deduplicate_against_reference(bioivt, clinical, COHORT_BIOIVT_LEGACY)
    cardinal_legacy, cardinal_dedup = deduplicate_against_reference(
        cardinal_legacy, clinical, COHORT_CARDINAL_LEGACY
    )

    frames = [f for f in (clinical, cardinal_2026, v2, bioivt, cardinal_legacy) if not f.empty]
    master = pd.concat(frames, ignore_index=True)

    before = len(master)
    master = master.dropna(subset=["age", "beta_score_399"])
    dropped_null = before - len(master)

    bad_age = ~master["age"].between(AGE_MIN_PLAUSIBLE, AGE_MAX_PLAUSIBLE)
    n_bad_age = int(bad_age.sum())
    if n_bad_age:
        vals = sorted(round(float(v), 2) for v in master.loc[bad_age, "age"].unique())
        log(f"  Dropped {n_bad_age} rows with implausible age (data-entry errors): {vals}")
    master = master.loc[~bad_age].copy()

    bad_beta = master["beta_score_399"] < BETA_MIN_PLAUSIBLE
    n_bad_beta = int(bad_beta.sum())
    if n_bad_beta:
        vals = sorted(round(float(v), 2) for v in master.loc[bad_beta, "beta_score_399"].unique())
        log(f"  Dropped {n_bad_beta} rows with negative INS 399 (impossible): {vals}")
    master = master.loc[~bad_beta].copy()

    log(f"  Dropped {dropped_null} rows missing age or INS 399")
    log(f"  Master dataframe: {len(master)} patients")

    cohort_summary = summarize_cohorts(master)

    not_at_risk = master[master["at_risk"] == 0]
    at_risk = master[master["at_risk"] == 1]

    section("STEP 2: VALIDATE AGE-BETA RELATIONSHIP")
    reg_not_at_risk = run_regression(not_at_risk, "NOT AT RISK")
    reg_at_risk = run_regression(at_risk, "AT RISK")

    section("STEP 3: REFERENCE RANGES (NOT-AT-RISK PATIENTS ONLY)")
    bands_not_at_risk = build_age_bands(not_at_risk, "Reference bands — NOT AT RISK (healthy baseline)")
    bands_at_risk = build_age_bands(at_risk, "Comparison — AT RISK")

    section("STEP 4: FIGURES")
    reg_lines = load_reference_threshold_lines()
    if not reg_lines:
        log("  No KiHealth reference-range JSON found - no horizontal threshold lines drawn.")

    fig_a = figure_a_scatter(master, not_at_risk, reg_lines)
    log(f"  Saved {fig_a.relative_to(BASE)}")

    fig_b, box_counts = figure_b_boxplot(master)
    if fig_b:
        log(f"  Saved {fig_b.relative_to(BASE)}")

    fig_c, band_gate = figure_c_reference_bands(bands_not_at_risk, reg_not_at_risk)
    if fig_c:
        log(f"  Saved {fig_c.relative_to(BASE)}")

    payload = {
        "generated_from": "scripts/m2b/19_age_adjusted_reference_ranges.py",
        "methodology": {
            "reference_population": "not-at-risk patients only",
            "thresholds": "none hardcoded; all bands are empirical percentiles",
            "min_n_per_bin": MIN_N_PER_BIN,
            "min_n_for_regression": MIN_N_FOR_REGRESSION,
            "significance_level": SIGNIFICANCE_P,
            "age_plausibility_bounds": [AGE_MIN_PLAUSIBLE, AGE_MAX_PLAUSIBLE],
            "beta_min_plausible": BETA_MIN_PLAUSIBLE,
            "band_definition": {
                "lower_tail": "p10-p25",
                "typical": "p25-p75",
                "upper_borderline": "p75-p90",
                "above_reference": ">p90",
            },
        },
        "cohorts": cohort_summary,
        "totals": {
            "n_total": int(len(master)),
            "n_at_risk": int((master["at_risk"] == 1).sum()),
            "n_not_at_risk": int((master["at_risk"] == 0).sum()),
            "n_unknown": int(master["at_risk"].isna().sum()),
            "dropped_missing_age_or_beta": int(dropped_null),
            "dropped_implausible_age": n_bad_age,
            "dropped_negative_beta": n_bad_beta,
        },
        "data_quality": {
            "v2_join": v2_meta,
            "bioivt_legacy_dedup": bioivt_dedup,
            "cardinal_legacy_dedup": cardinal_dedup,
        },
        "regression": {"not_at_risk": reg_not_at_risk, "at_risk": reg_at_risk},
        "age_bins": [name for name, _, _ in AGE_BINS],
        "reference_ranges_not_at_risk": bands_not_at_risk,
        "comparison_at_risk": bands_at_risk,
        "boxplot_group_counts": box_counts,
        "figures": {
            "age_vs_beta_scatter": str(fig_a.relative_to(BASE)) if fig_a else None,
            "age_group_boxplot": str(fig_b.relative_to(BASE)) if fig_b else None,
            "age_reference_bands": str(fig_c.relative_to(BASE)) if fig_c else None,
            "age_reference_bands_gate": band_gate,
        },
    }

    serialized = json.dumps(payload, indent=2) + "\n"
    JSON_PATH.write_text(serialized)
    if UI_JSON_PATH.parent.is_dir():
        UI_JSON_PATH.write_text(serialized)

    section("SUMMARY")
    log(f"Saved: {JSON_PATH.relative_to(BASE)}")
    if UI_JSON_PATH.parent.is_dir():
        log(f"Saved: {UI_JSON_PATH.relative_to(BASE)} (committed copy for Streamlit)")
    log(
        f"Age trend (not-at-risk): {reg_not_at_risk.get('interpretation')} "
        f"(n={reg_not_at_risk.get('n')}, p={reg_not_at_risk.get('p_value', float('nan'))})"
    )
    usable = [n for n, b in bands_not_at_risk.items() if b.get("usable")]
    log(f"Usable reference bins (n >= {MIN_N_PER_BIN}): {', '.join(usable) if usable else 'none'}")


if __name__ == "__main__":
    main()
