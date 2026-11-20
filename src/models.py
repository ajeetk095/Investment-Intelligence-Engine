"""Core GWP2 models: MVO (Steps 1-3) and Black-Litterman (Steps 6-7).
True mathematical optimization only - no weight simulation (per assignment)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from config.settings import TRADING_DAYS


def portfolio_performance(w: np.ndarray, mu: np.ndarray, cov: np.ndarray,
                          rf: float = 0.04) -> dict:
    ret = float(w @ mu)
    vol = float(np.sqrt(w @ cov @ w))
    return {"return": ret, "volatility": vol, "sharpe": (ret - rf) / vol if vol > 0 else np.nan}


def max_sharpe_portfolio(mu: pd.Series, cov: pd.DataFrame, rf: float = 0.04,
                         allow_short: bool = False, max_weight: float = 1.0,
                         weight_cap_short: float = 2.0) -> dict:
    """SLSQP maximization of the Sharpe ratio under the Step 1/2/3 constraint sets."""
    mu_v = np.asarray(mu, dtype=float)
    cov_v = np.asarray(cov, dtype=float)
    n = len(mu_v)
    lo, hi = (-weight_cap_short, weight_cap_short) if allow_short else (0.0, max_weight)
    res = minimize(
        lambda w: -( (w @ mu_v - rf) / np.sqrt(w @ cov_v @ w) ),
        x0=np.repeat(1 / n, n), method="SLSQP",
        bounds=[(lo, hi)] * n,
        constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0}],
        options={"maxiter": 500, "ftol": 1e-12},
    )
    w = np.clip(res.x, lo, hi)  # SLSQP eq-constraint keeps sum=1; clip tiny bound overshoot
    perf = portfolio_performance(w, mu_v, cov_v, rf)
    perf.update({"weights": pd.Series(w, index=mu.index), "success": bool(res.success),
                 "message": res.message})
    return perf


def efficient_frontier(mu: pd.Series, cov: pd.DataFrame, rf: float = 0.04,
                       allow_short: bool = False, points: int = 40) -> pd.DataFrame:
    """Frontier by minimizing variance per target return (long-only by default)."""
    mu_v, cov_v = np.asarray(mu), np.asarray(cov)
    n = len(mu_v)
    lo = -1.5 if allow_short else 0.0
    targets = np.linspace(mu_v.min(), mu_v.max(), points)
    rows = []
    for t in targets:
        res = minimize(lambda w: w @ cov_v @ w, x0=np.repeat(1 / n, n), method="SLSQP",
                       bounds=[(lo, 1.5)] * n,
                       constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1},
                                    {"type": "eq", "fun": lambda w, k=t: w @ mu_v - k}])
        if res.success:
            vol = float(np.sqrt(res.x @ cov_v @ res.x))
            rows.append({"target_return": t, "volatility": vol,
                         "sharpe": (t - rf) / vol if vol > 0 else np.nan})
    return pd.DataFrame(rows)


def black_litterman(cov: pd.DataFrame, mkt_weights: pd.Series,
                    P: np.ndarray, Q: np.ndarray, omega: np.ndarray | None,
                    tau: float = 0.05, delta: float = 2.5) -> dict:
    """He-Litterman implementation. omega=None -> Idzorek-style diag(tau * P Sigma P').
    Returns blended posterior returns/covariance and the equilibrium prior."""
    Sigma = np.asarray(cov, dtype=float)
    w_mkt = np.asarray(mkt_weights, dtype=float)
    pi = delta * Sigma @ w_mkt
    if omega is None:
        omega = np.diag(np.diag(tau * P @ Sigma @ P.T))
    omega = np.asarray(omega, dtype=float)
    prior_prec = np.linalg.inv(tau * Sigma)
    M = np.linalg.inv(prior_prec + P.T @ np.linalg.inv(omega) @ P)
    mu_bl = M @ (prior_prec @ pi + P.T @ np.linalg.inv(omega) @ Q)
    sigma_bl = Sigma + M - tau * Sigma  # He-Litterman posterior covariance
    return {"equilibrium_pi": pd.Series(pi, index=cov.index),
            "posterior_mu": pd.Series(mu_bl, index=cov.index),
            "posterior_cov": pd.DataFrame(sigma_bl, index=cov.index, columns=cov.index)}


def views_matrices(tickers: list[str], views: list[dict],
                   cov: pd.DataFrame, tau: float = 0.05) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Build P, Q, Omega from view dicts: {'asset':..,'value':..,'confidence':..} for
    absolute views, or {'long':..,'short':..,'value':..,'confidence':..} for relative views.
    Confidence c in (0,1] maps to omega_j = ((1-c)/c) * tau * Var(view_j) (Idzorek-style:
    higher confidence -> smaller uncertainty)."""
    n, k = len(tickers), len(views)
    idx = {t: i for i, t in enumerate(tickers)}
    Sigma = np.asarray(cov, dtype=float)
    P = np.zeros((k, n)); Q = np.zeros(k); Omega = np.zeros((k, k)); desc = []
    for j, v in enumerate(views):
        if "asset" in v:  # absolute view
            P[j, idx[v["asset"]]] = 1.0
            desc.append(f"Absolute: {v['asset']} = {v['value']:.1%} (confidence {v['confidence']:.0%})")
        else:             # relative view
            P[j, idx[v["long"]]] = 1.0
            P[j, idx[v["short"]]] = -1.0
            desc.append(f"Relative: {v['long']} - {v['short']} = {v['value']:.1%} (confidence {v['confidence']:.0%})")
        Q[j] = v["value"]
        var_j = float(P[j] @ Sigma @ P[j])
        c = float(np.clip(v["confidence"], 1e-3, 1.0))
        Omega[j, j] = ((1 - c) / c) * tau * var_j
    return P, Q, Omega, desc
