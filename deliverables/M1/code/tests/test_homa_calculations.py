"""Tests for HOMA-IR and HOMA-beta calculations."""

import numpy as np
import pandas as pd
import pytest

from src.features.homa_calculations import (
    homa_ir,
    homa_beta,
    add_homa_columns,
    glucose_mmol_to_mg_dl,
    glucose_mg_dl_to_mmol,
    validate_homa_reference,
)


def test_homa_ir_scalar():
    # HOMA-IR = (glucose * insulin) / 405
    assert np.isclose(homa_ir(100.0, 10.0), 100 * 10 / 405)
    assert np.isclose(homa_ir(90.0, 18.0), 90 * 18 / 405)


def test_homa_beta_scalar():
    # HOMA-beta = 360 * insulin / (glucose - 63)
    assert np.isclose(homa_beta(100.0, 10.0), 360 * 10 / (100 - 63))
    assert np.isclose(homa_beta(126.0, 25.0), 360 * 25 / (126 - 63))


def test_homa_ir_invalid():
    assert np.isnan(homa_ir(0, 10))
    assert np.isnan(homa_ir(100, 0))
    assert np.isnan(homa_ir(np.nan, 10))
    assert np.isnan(homa_beta(63, 10))
    assert np.isnan(homa_beta(50, 10))


def test_homa_series():
    g = pd.Series([100.0, 90.0, 0.0])
    i = pd.Series([10.0, 18.0, 5.0])
    ir = homa_ir(g, i)
    assert ir.iloc[0] == 100 * 10 / 405
    assert ir.iloc[1] == 90 * 18 / 405
    assert np.isnan(ir.iloc[2])


def test_add_homa_columns():
    df = pd.DataFrame({"Glucose": [100, 90], "Insulin": [10, 18]})
    out = add_homa_columns(df, "Glucose", "Insulin")
    assert "homa_ir" in out.columns
    assert "homa_beta" in out.columns
    assert np.isclose(out["homa_ir"].iloc[0], 100 * 10 / 405)


def test_glucose_conversion():
    assert np.isclose(glucose_mmol_to_mg_dl(5.55), 100.0, rtol=1e-2)
    assert np.isclose(glucose_mg_dl_to_mmol(100.0), 5.55, rtol=1e-2)


def test_validate_homa_reference():
    passed, msg = validate_homa_reference(100.0, 10.0, expected_ir=100 * 10 / 405, expected_beta=360 * 10 / 37)
    assert passed, msg
