"""Feature engineering used across the research laboratory and ML modules."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import TRADING_DAYS


def rolling_metrics(returns: pd.DataFrame, window: int = 63) -> pd.DataFrame:
    """Rolling annualized return & volatility per asset (stacked long format)."""
    rows = {}
    for t in returns.columns:
        rows[t] = {
            f"RollAnnRet_{window}": returns[t].rolling(window).mean() * TRADING_DAYS,
            f"RollVol_{window}": returns[t].rolling(window).std() * np.sqrt(TRADING_DAYS),
        }
    return pd.concat({t: pd.DataFrame(d) for t, d in rows.items()}, axis=1)


def drawdown_series(returns: pd.Series) -> pd.Series:
    wealth = (1 + returns).cumprod()
    return wealth / wealth.cummax() - 1
