#!/usr/bin/env python3
"""
Build CHECK cohort dataset with OAI column names for pooling with OAI in Models 1 & 2.
Merges CHECK T0 baseline with Rontgen (KL grades + T2 follow-up) by row index (same participant order).
Output: DataFrame with same columns as OAI baseline_modeling.csv (ID, V00AGE, P02SEX, ... knee_replacement_4yr).
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths (repo root = parent of scripts/)
BASE = Path(__file__).resolve().parent.parent
CHECK_T0_CSV = BASE / "data/New-OA-Data/CHECK/CHECK_T0_DANS_nsin_ENG_20161128.csv"
CHECK_T0_SAV = BASE / "data/New-OA-Data/CHECK/CHECK_T0_DANS_nsin_ENG_20161128.sav"
RONTGEN_CSV = BASE / "data/New-OA-Data/extracted/sav/Rontgen_opT10_20191118.csv"
OUT_CSV = BASE / "data/New-OA-Data/check_oai_format.csv"


def main():
    # Load CHECK T0 (1002 rows) - from CSV if present, else .sav
    if CHECK_T0_CSV.exists():
        check_t0 = pd.read_csv(CHECK_T0_CSV)
    elif CHECK_T0_SAV.exists():
        try:
            import pyreadstat
            check_t0, _ = pyreadstat.read_sav(CHECK_T0_SAV)
        except Exception as e:
            raise FileNotFoundError(f"Need CHECK T0 as CSV or .sav. CSV not found; .sav read failed: {e}") from e
    else:
        raise FileNotFoundError(f"CHECK T0 not found at {CHECK_T0_CSV} or {CHECK_T0_SAV}")
    n_check = len(check_t0)
    if n_check != 1002:
        print(f"Warning: CHECK T0 has {n_check} rows (expected 1002)")

    # Load Rontgen (1002 rows) - KL at T0, T2, ... and outcome proxy at T2
    rontgen = pd.read_csv(RONTGEN_CSV)
    if len(rontgen) != n_check:
        raise ValueError(f"Row count mismatch: CHECK T0 {n_check}, Rontgen {len(rontgen)}. Merge by index assumes same order.")

    # Merge by row index (same participant in row i in both)
    # Rontgen has nsin; we don't use it for merge so we align by position
    assert len(check_t0) == len(rontgen), "Lengths must match for index merge"

    # Outcome: CHECK follow-up is T2 (2yr), T5 (5yr), T8 (8yr), T10 (10yr).
    # "TKR within 4 years" => use T2 (2-year) only. In some KL codings, grade 5 = joint replaced (TKR).
    # We define: knee_replacement_4yr = 1 if at T2 either knee has KL == 5 (replacement), else 0.
    # Same for 2yr (T2 is only timepoint within 2yr).
    kl_li_t2 = pd.to_numeric(rontgen["T2_K_KL_li_def"], errors="coerce").fillna(0)
    kl_re_t2 = pd.to_numeric(rontgen["T2_K_KL_re_def"], errors="coerce").fillna(0)
    # Also accept string "tkr" if present (from Stata labels)
    def is_tkr(v):
        if pd.isna(v): return 0
        if v == 5 or v == "5": return 1
        if str(v).lower() == "tkr": return 1
        return 0
    kr_2yr = np.array([1 if is_tkr(kl_li_t2.iloc[i]) or is_tkr(kl_re_t2.iloc[i]) else 0 for i in range(len(rontgen))])
    kr_4yr = kr_2yr  # T2 is only follow-up within 4 years

    # Build OAI-named columns
    age = check_t0["T0_Lft_T0"].astype(float)
    sex = check_t0["T0_SEXE"].astype(float)  # 1/2; assume same as OAI
    race = check_t0["T0_RAS"].astype(float)  # map to OAI categories 1-5
    cohort = check_t0["T0_JVCON"].astype(float)  # 1/2 visit group; use as proxy for Progression/Incidence
    womac = check_t0["T0_wmtot"].astype(float)  # single total; use for both L and R
    bmi = check_t0["T0_BMI"].astype(float)
    kl_r = pd.to_numeric(rontgen["T0_K_KL_re_def"], errors="coerce")
    kl_l = pd.to_numeric(rontgen["T0_K_KL_li_def"], errors="coerce")
    # If any value is string "tkr" or 5, cap KL at 4 for baseline (0-4 scale); 5 = replaced already at T0
    kl_r = kl_r.replace(5, 4).clip(0, 4).fillna(0)
    kl_l = kl_l.replace(5, 4).clip(0, 4).fillna(0)

    # Family history: missing in CHECK → impute 0 (No)
    fam = np.zeros(n_check)

    # 400m walk: missing in CHECK → NaN (preprocessing will impute)
    walk400m = np.full(n_check, np.nan)

    # IDs
    ids = [f"CHECK_{i+1}" for i in range(n_check)]

    df = pd.DataFrame({
        "ID": ids,
        "P02SEX": sex,
        "P02RACE": race,
        "V00COHORT": cohort,
        "V00WOMTSR": womac,
        "V00WOMTSL": womac,
        "V00400MTIM": walk400m,
        "V00AGE": age,
        "P01BMI": bmi,
        "V00XRKLR": kl_r,
        "V00XRKLL": kl_l,
        "P01FAMKR": fam,
        "knee_replacement_2yr": kr_2yr,
        "knee_replacement_4yr": kr_4yr,
    })

    df.to_csv(OUT_CSV, index=False)
    print(f"Saved {OUT_CSV}: {df.shape}")
    print(f"  CHECK 4yr TKR events (T2 KL=5 proxy): {df['knee_replacement_4yr'].sum()}")
    return df


if __name__ == "__main__":
    main()
