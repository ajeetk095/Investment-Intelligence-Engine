"""Live data collection: Yahoo Finance (delayed) + FRED macro data, with caching,
retries and graceful degradation. Never fabricates data - failures raise or return None."""
from __future__ import annotations

import time
from datetime import datetime, timezone

import pandas as pd
import requests

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FRED_SERIES, get_fred_api_key


def fetch_prices(tickers, start: str, end: str, retries: int = 3) -> pd.DataFrame:
    """Download adjusted close prices from Yahoo Finance. Raises on total failure."""
    import yfinance as yf

    last_err = None
    for attempt in range(retries):
        try:
            raw = yf.download(tickers, start=start, end=end, progress=False,
                              auto_adjust=True, threads=True)
            if raw.empty:
                raise ValueError("empty dataframe returned by Yahoo Finance")
            close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
            if isinstance(close, pd.Series):
                close = close.to_frame(tickers[0] if isinstance(tickers, str) else tickers[0])
            prices = close.dropna(how="all")
            if len(prices) < 30:
                raise ValueError(f"only {len(prices)} rows retrieved")
            return prices
        except Exception as err:  # noqa: BLE001 - retry any network/parse failure
            last_err = err
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Yahoo Finance download failed after {retries} attempts: {last_err}")


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna(how="all").dropna(axis=0, how="any")


def get_fred_series(series_id: str = "DGS10", limit_rows: int = 900) -> pd.Series | None:
    """Fetch a FRED series. Uses the API key when configured, else the public CSV
    endpoint (verified working without a key). Returns None on failure - no synthetic data."""
    api_key = get_fred_api_key()
    try:
        if api_key:
            r = requests.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={"series_id": series_id, "api_key": api_key,
                        "file_type": "json", "sort_order": "desc", "limit": limit_rows},
                timeout=15)
            r.raise_for_status()
            obs = r.json().get("observations", [])
            vals = {o["date"]: float(o["value"]) for o in obs if o["value"] not in (".", "")}
        else:
            r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv",
                             params={"id": series_id}, timeout=20)
            r.raise_for_status()
            df = pd.read_csv(pd.io.common.StringIO(r.text))
            vals = {d: float(v) for d, v in df.itertuples(index=False) if str(v) not in ("nan", ".")}
        s = pd.Series(vals, name=series_id)
        s.index = pd.to_datetime(s.index)
        return s.sort_index().tail(limit_rows)
    except Exception:
        return None


def live_risk_free_rate() -> tuple[float | None, str | None]:
    """Latest 10y Treasury yield (%) from FRED -> decimal. (None, None) if unavailable."""
    s = get_fred_series("DGS10")
    if s is None or s.empty:
        return None, None
    return float(s.iloc[-1]) / 100.0, str(s.index[-1].date())


def data_freshness(prices: pd.DataFrame) -> str:
    """Human-readable last-successful-update timestamp for display in the app."""
    last_px = prices.index.max().strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"Latest price row: {last_px} | Last successful update: {now}"


def quality_checks(prices: pd.DataFrame, max_missing_pct: float = 2.0) -> dict:
    """Basic data-quality gate: staleness, missing values, zero-variance columns."""
    report = {"rows": len(prices), "cols": prices.shape[1], "issues": []}
    miss = prices.isna().mean() * 100
    if (miss > max_missing_pct).any():
        report["issues"].append(f"columns with >{max_missing_pct}% missing: {miss[miss > max_missing_pct].index.tolist()}")
    if (prices.nunique() <= 1).any():
        report["issues"].append(f"constant columns: {prices.columns[prices.nunique() <= 1].tolist()}")
    if isinstance(prices.index, pd.DatetimeIndex):
        gap = (pd.Timestamp.today(timezone.utc).tz_localize(None) - prices.index.max()).days
        if gap > 7:
            report["issues"].append(f"data may be stale: last row is {gap} days old")
    report["pass"] = len(report["issues"]) == 0
    return report
