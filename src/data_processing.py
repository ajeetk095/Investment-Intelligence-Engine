"""Return processing and descriptive statistics (GWP2 Step 0)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import TRADING_DAYS


def annualized_stats(returns: pd.DataFrame, rf: float = 0.04) -> pd.DataFrame:
    """Step 0 table: ann. return, ann. vol, Sharpe, skewness, excess kurtosis."""
    mu = returns.mean() * TRADING_DAYS
    vol = returns.std(ddof=1) * np.sqrt(TRADING_DAYS)
    sharpe = (mu - rf) / vol
    return pd.DataFrame({
        "Ann. Return": mu, "Ann. Volatility": vol, "Sharpe Ratio": sharpe,
        "Skewness": returns.skew(), "Excess Kurtosis": returns.kurtosis(),
    })


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def avg_pairwise_correlation(returns: pd.DataFrame) -> float:
    vals = returns.corr().values
    n = vals.shape[0]
    return float(vals[np.triu_indices(n, 1)].mean())
