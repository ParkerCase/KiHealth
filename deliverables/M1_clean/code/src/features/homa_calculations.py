"""
HOMA-IR and HOMA-beta calculations from fasting glucose and insulin.

Formulas (Matthews et al.):
- HOMA-IR = (glucose_mg_dL * insulin_uU_mL) / 405
- HOMA-beta = (360 * insulin_uU_mL) / (glucose_mg_dL - 63)

Units: fasting glucose in mg/dL, fasting insulin in μU/mL.
Edge cases: missing values, glucose <= 63 (HOMA-beta undefined), zero insulin/glucose.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Published constants
HOMA_DENOMINATOR = 405.0
HOMA_BETA_NUMERATOR = 360.0
HOMA_BETA_GLUCOSE_OFFSET = 63.0  # mg/dL
MMOL_TO_MGDL = 18.0182  # 1 mmol/L = 18.0182 mg/dL


def glucose_mmol_to_mg_dl(glucose_mmol: float | pd.Series) -> float | pd.Series:
    """Convert fasting glucose from mmol/L to mg/dL."""
    return glucose_mmol * MMOL_TO_MGDL


def glucose_mg_dl_to_mmol(glucose_mg_dl: float | pd.Series) -> float | pd.Series:
    """Convert fasting glucose from mg/dL to mmol/L."""
    return glucose_mg_dl / MMOL_TO_MGDL


def homa_ir(
    glucose_mg_dl: float | pd.Series,
    insulin_uU_mL: float | pd.Series,
    *,
    fill_invalid: float | None = np.nan,
) -> float | pd.Series:
    """
    HOMA-IR = (glucose_mg_dL * insulin_μU_mL) / 405.

    Invalid (missing, <=0) inputs produce fill_invalid (default NaN).
    """
    if isinstance(glucose_mg_dl, pd.Series) or isinstance(insulin_uU_mL, pd.Series):
        g = pd.Series(glucose_mg_dl).astype(float)
        i = pd.Series(insulin_uU_mL).astype(float)
        valid = g.gt(0) & i.gt(0)
        out = (g * i) / HOMA_DENOMINATOR
        out = out.where(valid, fill_invalid)
        return out
    g = float(glucose_mg_dl)
    i = float(insulin_uU_mL)
    if pd.isna(g) or pd.isna(i) or g <= 0 or i <= 0:
        return np.nan if fill_invalid is None else fill_invalid
    return (g * i) / HOMA_DENOMINATOR


def homa_beta(
    glucose_mg_dl: float | pd.Series,
    insulin_uU_mL: float | pd.Series,
    *,
    fill_invalid: float | None = np.nan,
) -> float | pd.Series:
    """
    HOMA-beta = (360 * insulin_μU_mL) / (glucose_mg_dL - 63).

    Invalid: missing, glucose <= 63, or insulin <= 0 → fill_invalid (default NaN).
    """
    if isinstance(glucose_mg_dl, pd.Series) or isinstance(insulin_uU_mL, pd.Series):
        g = pd.Series(glucose_mg_dl).astype(float)
        i = pd.Series(insulin_uU_mL).astype(float)
        valid = g.gt(HOMA_BETA_GLUCOSE_OFFSET) & i.gt(0)
        denom = g - HOMA_BETA_GLUCOSE_OFFSET
        out = (HOMA_BETA_NUMERATOR * i) / denom
        out = out.where(valid, fill_invalid)
        return out
    g = float(glucose_mg_dl)
    i = float(insulin_uU_mL)
    if pd.isna(g) or pd.isna(i) or g <= HOMA_BETA_GLUCOSE_OFFSET or i <= 0:
        return np.nan if fill_invalid is None else fill_invalid
    return (HOMA_BETA_NUMERATOR * i) / (g - HOMA_BETA_GLUCOSE_OFFSET)


def add_homa_columns(
    df: pd.DataFrame,
    glucose_col: str,
    insulin_col: str,
    *,
    homa_ir_col: str = "homa_ir",
    homa_beta_col: str = "homa_beta",
    glucose_units: str = "mg_dL",
) -> pd.DataFrame:
    """
    Add HOMA-IR and HOMA-beta columns to a DataFrame.

    glucose_units: "mg_dL" or "mmol_L". If mmol_L, values are converted to mg/dL for the formula.
    """
    out = df.copy()
    g = out[glucose_col]
    i = out[insulin_col]
    if glucose_units.lower() in ("mmol_l", "mmol/L"):
        g = glucose_mmol_to_mg_dl(g)
    out[homa_ir_col] = homa_ir(g, i)
    out[homa_beta_col] = homa_beta(g, i)
    return out


def validate_homa_reference(
    glucose_mg_dl: float,
    insulin_uU_mL: float,
    expected_ir: float,
    expected_beta: float,
    *,
    rtol: float = 1e-2,
) -> tuple[bool, str]:
    """
    Validate HOMA calculations against known reference values.

    Returns (passed, message).
    """
    ir = homa_ir(glucose_mg_dl, insulin_uU_mL)
    be = homa_beta(glucose_mg_dl, insulin_uU_mL)
    ir_ok = np.isclose(ir, expected_ir, rtol=rtol)
    be_ok = np.isclose(be, expected_beta, rtol=rtol)
    if ir_ok and be_ok:
        return True, "HOMA-IR and HOMA-beta match reference."
    msg = []
    if not ir_ok:
        msg.append(f"HOMA-IR: got {ir}, expected {expected_ir}")
    if not be_ok:
        msg.append(f"HOMA-beta: got {be}, expected {expected_beta}")
    return False, "; ".join(msg)
