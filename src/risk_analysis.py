"""Risk measurement: VaR/CVaR, max drawdown, Monte Carlo paths, regime flags.
Enhancement module - each tool has a stated purpose (see docs/MODEL_METHODOLOGY.md)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def historical_var(returns: pd.Series | pd.DataFrame, confidence: float = 0.95) -> float:
    """Daily historical Value-at-Risk (positive = loss magnitude)."""
    return float(-returns.quantile(1 - confidence))


def historical_cvar(returns: pd.Series | pd.DataFrame, confidence: float = 0.95) -> float:
    """Daily Conditional VaR (expected shortfall beyond VaR)."""
    var = historical_var(returns, confidence)
    tail = returns[returns <= -var]
    return float(-tail.mean()) if len(tail) else var


def max_drawdown(cumulative: pd.Series) -> float:
    """Max drawdown of a cumulative-return series (negative number)."""
    wealth = 1 + cumulative
    peak = wealth.cummax()
    return float((wealth / peak - 1).min())


def portfolio_return_series(weights, returns: pd.DataFrame) -> pd.Series:
    w = pd.Series(weights).reindex(returns.columns).fillna(0.0)
    return returns @ w


def monte_carlo_paths(mu: float, cov: np.ndarray, weights: np.ndarray,
                      horizon_days: int = 252, n_sims: int = 2000,
                      seed: int = 42) -> np.ndarray:
    """Monte Carlo terminal wealth paths under a multivariate-normal day-by-day model.
    Explicit assumption: normal iid daily returns - fat tails are NOT captured."""
    rng = np.random.default_rng(seed)
    port_mu = float(weights @ mu)
    port_var = float(weights @ cov @ weights)
    daily_mu, daily_vol = port_mu / 252, np.sqrt(port_var / 252)
    shocks = rng.normal(daily_mu - daily_vol**2 / 2, daily_vol, size=(n_sims, horizon_days))
    return np.exp(shocks.cumsum(axis=1))  # path of wealth factors


def var_confidence(returns: pd.Series, confidence: float = 0.95, n_boot: int = 500,
                   seed: int = 42) -> tuple[float, float]:
    """Bootstrap CI for VaR so reported risk numbers carry uncertainty estimates."""
    rng = np.random.default_rng(seed)
    arr = returns.dropna().values
    estimates = []
    for _ in range(n_boot):
        sample = rng.choice(arr, size=len(arr), replace=True)
        estimates.append(-np.quantile(sample, 1 - confidence))
    return float(np.percentile(estimates, 5)), float(np.percentile(estimates, 95))


def regime_flag(returns: pd.Series, short_w: int = 21, long_w: int = 126) -> str:
    """Simple trend/absorption regime label from rolling-momentum spread.
    Descriptive - not a forecast. Values: Risk-On / Neutral / Risk-Off."""
    r = returns.dropna()
    if len(r) < long_w:
        return "Neutral"
    short_mom = r.tail(short_w).mean() * 252
    long_mom = r.tail(long_w).mean() * 252
    vol = r.tail(short_w).std() * np.sqrt(252)
    if short_mom > 0 and short_mom >= long_mom and vol < 0.45:
        return "Risk-On"
    if short_mom < 0 and short_mom <= long_mom:
        return "Risk-Off"
    return "Neutral"
