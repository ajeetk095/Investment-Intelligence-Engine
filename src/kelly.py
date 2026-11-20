"""GWP2 Part 4 (Step 8): Kelly criterion via the GENERAL multivariate formula
w* = f * Sigma^{-1} (mu - rf). Correlations ARE captured (no gambling formula).
Includes a discrete-rebalancing path simulation to compare growth/drawdowns honestly."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import TRADING_DAYS


def kelly_weights(returns: pd.DataFrame, rf: float, fraction: float = 1.0) -> pd.Series:
    """Full/half/double Kelly from the general continuous formula."""
    mu = returns.mean().values * TRADING_DAYS
    cov = returns.cov().values * TRADING_DAYS
    try:
        raw = np.linalg.solve(cov, mu - rf)
    except np.linalg.LinAlgError:
        raw = np.linalg.pinv(cov) @ (mu - rf)
    return pd.Series(fraction * raw, index=returns.columns, name=f"kelly_f{fraction}")


def kelly_paths(returns: pd.DataFrame, rf: float, fraction: float,
                horizon_days: int = 252, n_paths: int = 500, seed: int = 42,
                rebalance_every: int = 63) -> pd.DataFrame:
    """Block-bootstrap market paths; portfolio is rebalanced to Kelly weights
    every `rebalance_every` days using only data available at that time (expanding window).
    Returns per-path terminal wealth and max drawdown."""
    rng = np.random.default_rng(seed + int(fraction * 10))
    R = returns.values
    n, k = R.shape
    block = 21
    n_blocks = int(np.ceil(horizon_days / block))
    finals, mdds = [], []
    for p in range(n_paths):
        starts = rng.integers(0, n - block, size=n_blocks)
        path_idx = np.concatenate([np.arange(i, i + block) for i in starts])[:horizon_days]
        wealth = 1.0
        peak, mdd = 1.0, 0.0
        hist = pd.DataFrame(R[: max(path_idx[0], 60)], columns=returns.columns)
        for day, mkt_day in enumerate(path_idx):
            if day % rebalance_every == 0:
                w = kelly_weights(hist, rf, fraction).values
            wealth *= float(1 + R[mkt_day] @ w + (0 if w.sum() == 1 else 0))
            peak = max(peak, wealth)
            mdd = min(mdd, wealth / peak - 1)
            hist = pd.concat([hist, returns.iloc[[mkt_day]]])
        finals.append(wealth - 1)
        mdds.append(mdd)
    return pd.DataFrame({"terminal_return": finals, "max_drawdown": mdds})


def compare_strategies(returns: pd.DataFrame, rf: float = 0.04,
                       n_paths: int = 300, seed: int = 42) -> dict:
    out = {"weights": {}, "paths": {}}
    for label, frac in [("Full Kelly (f=1.0)", 1.0), ("Half Kelly (f=0.5)", 0.5),
                        ("Double Kelly (f=2.0)", 2.0)]:
        w = kelly_weights(returns, rf, frac)
        out["weights"][label] = w
        out["paths"][label] = kelly_paths(returns, rf, frac, n_paths=n_paths, seed=seed)
    return out
