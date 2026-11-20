"""GWP2 Part 2 (Step 5): MVO vs 1/N out-of-sample simulation.
Faithful to the original methodology: 20-asset universe, random 5-asset draws,
2y training / 1y testing, 5,000 simulations, MVO via true SLSQP optimization."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

from config.settings import TRADING_DAYS


def _mvo_weights(train_returns: pd.DataFrame, rf: float) -> np.ndarray | None:
    mu = train_returns.mean().values * TRADING_DAYS
    cov = train_returns.cov().values * TRADING_DAYS
    n = len(mu)
    res = minimize(lambda w: -((w @ mu - rf) / np.sqrt(w @ cov @ w)),
                   x0=np.repeat(1 / n, n), method="SLSQP",
                   bounds=[(0.0, 1.0)] * n,
                   constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}])
    return res.x if res.success else None


def run_simulation(returns_all: pd.DataFrame, train_mask: pd.Series, test_mask: pd.Series,
                   n_sims: int = 5000, k: int = 5, rf: float = 0.04,
                   seed: int = 42, progress_every: int | None = None,
                   progress_cb=None) -> pd.DataFrame:
    """Run the study. train_mask/test_mask are boolean indexers on the returns index."""
    rng = np.random.default_rng(seed)
    train_r = returns_all.loc[train_mask]
    test_r = returns_all.loc[test_mask]
    tickers = list(returns_all.columns)
    rows = []
    for i in range(n_sims):
        pick = rng.choice(tickers, size=k, replace=False)
        w = _mvo_weights(train_r[pick], rf)
        if w is None:
            continue
        mu_t = train_r[pick].mean().values * TRADING_DAYS
        cov_t = train_r[pick].cov().values * TRADING_DAYS
        mvo_ret = float(np.exp((test_r[pick].values @ w).sum()) - 1)   # 1y geometric
        eq_ret = float(np.exp(test_r[pick].mean().sum()) - 1)          # 1/N, equal 0.2
        mvo_vol = float(np.sqrt(w @ cov_t @ w))
        rows.append({"sim": i, "assets": ",".join(pick), "MVO_Return": mvo_ret,
                     "1N_Return": eq_ret, "MVO_Vol": mvo_vol})
        if progress_cb and progress_every and (i + 1) % progress_every == 0:
            progress_cb(i + 1, n_sims)
    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame, rf: float = 0.04) -> dict:
    """Descriptive stats + hypothesis tests (paired t, Wilcoxon, F variance ratio)."""
    mvo, eq = results["MVO_Return"], results["1N_Return"]

    def desc(s: pd.Series) -> dict:
        return {"mean": float(s.mean()), "median": float(s.median()), "std": float(s.std()),
                "skew": float(s.skew()), "kurt": float(s.kurtosis()),
                "min": float(s.min()), "max": float(s.max()),
                "p5": float(s.quantile(0.05)), "p95": float(s.quantile(0.95))}

    d_mvo, d_eq = desc(mvo), desc(eq)
    t_stat, t_p = stats.ttest_rel(mvo, eq)
    try:
        w_stat, w_p = stats.wilcoxon(mvo, eq)
    except ValueError:
        w_stat, w_p = np.nan, np.nan
    f_stat, f_p = stats.levene(mvo, eq)  # variance-equality test (robust F-style)
    # Sharpe computed from mean/std of the return distributions
    sharpe_mvo = (d_mvo["mean"] - rf) / d_mvo["std"]
    sharpe_eq = (d_eq["mean"] - rf) / d_eq["std"]
    return {
        "MVO": d_mvo, "1N": d_eq,
        "sharpe": {"MVO": sharpe_mvo, "1N": sharpe_eq},
        "win_rate_mvo": float((mvo > eq).mean()),
        "t_test": {"stat": float(t_stat), "p": float(t_p)},
        "wilcoxon": {"stat": float(w_stat) if w_stat == w_stat else None,
                     "p": float(w_p) if w_p == w_p else None},
        "variance_test": {"stat": float(f_stat), "p": float(f_p),
                          "note": "Levene's test for equal variances (robust alternative to a raw F ratio)"},
        "n_sims": int(len(results)),
    }
