"""Simulation/Kelly tests on synthetic data (fast; no network)."""
import numpy as np
import pandas as pd
import pytest

from src.simulation import run_simulation, summarize
from src.kelly import kelly_weights


@pytest.fixture
def synthetic_returns():
    rng = np.random.default_rng(3)
    idx = pd.date_range("2022-01-01", periods=900, freq="B")
    return pd.DataFrame(rng.normal(0.0004, 0.01, size=(900, 6)),
                        columns=list("ABCDEF"), index=idx)


def test_kelly_weights_use_general_formula(synthetic_returns):
    rf = 0.04
    w = kelly_weights(synthetic_returns, rf, fraction=1.0)
    mu = synthetic_returns.mean().values * 252
    cov = synthetic_returns.cov().values * 252
    expected = np.linalg.solve(cov, mu - rf)
    assert np.allclose(w.values, expected)


def test_half_kelly_is_half(synthetic_returns):
    full = kelly_weights(synthetic_returns, 0.04, 1.0)
    half = kelly_weights(synthetic_returns, 0.04, 0.5)
    assert np.allclose(half.values, full.values / 2)


def test_small_simulation_runs_and_summarizes(synthetic_returns):
    mask_train = synthetic_returns.index.year <= 2023
    mask_test = synthetic_returns.index.year == 2024
    res = run_simulation(synthetic_returns, mask_train, mask_test,
                         n_sims=10, k=3, seed=1)
    assert len(res) == 10
    s = summarize(res, rf=0.04)
    assert 0 <= s["win_rate_mvo"] <= 1
    assert "t_test" in s and "wilcoxon" in s
