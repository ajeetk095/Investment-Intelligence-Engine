"""Unit tests for the core GWP2 models (synthetic data - no network needed)."""
import numpy as np
import pandas as pd
import pytest

from src.models import (portfolio_performance, max_sharpe_portfolio,
                        efficient_frontier, black_litterman, views_matrices)


@pytest.fixture
def synthetic():
    rng = np.random.default_rng(7)
    n_obs, n_assets = 800, 4
    truth = rng.normal(0.0005, 0.012, size=(n_obs, n_assets))
    cols = ["A", "B", "C", "D"]
    returns = pd.DataFrame(truth, columns=cols)
    return returns, returns.mean() * 252, returns.cov() * 252


def test_equal_weights_match_formula(synthetic):
    _, mu, cov = synthetic
    w = np.repeat(0.25, 4)
    perf = portfolio_performance(w, mu.values, cov.values, rf=0.04)
    assert perf["return"] == pytest.approx(float(w @ mu.values))
    assert perf["volatility"] == pytest.approx(float(np.sqrt(w @ cov.values @ w)))


def test_long_only_weights_constrained(synthetic):
    _, mu, cov = synthetic
    res = max_sharpe_portfolio(mu, cov, rf=0.04, allow_short=False, max_weight=1.0)
    w = res["weights"]
    assert (w >= -1e-8).all()
    assert w.sum() == pytest.approx(1.0, abs=1e-6)
    assert res["success"]


def test_cap_respected(synthetic):
    _, mu, cov = synthetic
    res = max_sharpe_portfolio(mu, cov, rf=0.04, allow_short=False, max_weight=0.20)
    assert (res["weights"] <= 0.20 + 1e-6).all()


def test_short_allowed_can_go_negative(synthetic):
    _, mu, cov = synthetic
    res = max_sharpe_portfolio(mu, cov, rf=0.04, allow_short=True)
    assert res["weights"].sum() == pytest.approx(1.0, abs=1e-6)


def test_frontier_shapes(synthetic):
    _, mu, cov = synthetic
    f = efficient_frontier(mu, cov, points=8)
    assert not f.empty
    assert (f["volatility"] > 0).all()


def test_black_litterman_posterior_between_prior_and_views(synthetic):
    _, mu, cov = synthetic
    w_mkt = pd.Series([0.4, 0.3, 0.2, 0.1], index=cov.index)
    views = [{"asset": "A", "value": 0.10, "confidence": 0.9}]
    P, Q, Om, desc = views_matrices(list(cov.columns), views, cov)
    bl = black_litterman(cov, w_mkt, P, Q, Om)
    # posterior for A should sit between equilibrium prior and the view
    pi_A = bl["equilibrium_pi"]["A"]
    assert min(pi_A, 0.10) - 1e-9 <= bl["posterior_mu"]["A"] <= max(pi_A, 0.10) + 1e-9


def test_views_relative_row():
    cov = pd.DataFrame(np.eye(2) * 0.04, index=["X", "Y"], columns=["X", "Y"])
    views = [{"long": "X", "short": "Y", "value": 0.05, "confidence": 0.7}]
    P, Q, Om, desc = views_matrices(["X", "Y"], views, cov)
    assert P[0].tolist() == [1.0, -1.0]
    assert Q[0] == pytest.approx(0.05)
    assert Om[0, 0] > 0
