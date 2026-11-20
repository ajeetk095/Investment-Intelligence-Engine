"""Forecasting layer (enhancement with explicit purpose): block-bootstrap forecast
of portfolio wealth (no iid-normal assumption -> respects fat tails) plus a
random-forest regime classifier with walk-forward validation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import TRADING_DAYS


def bootstrap_forecast(returns: pd.DataFrame, weights: pd.Series, horizon_days: int = 252,
                       n_sims: int = 1000, seed: int = 42) -> dict:
    """Stationary block bootstrap of historical daily returns -> distribution of
    horizon portfolio returns. Returns percentiles of terminal wealth."""
    rng = np.random.default_rng(seed)
    if not isinstance(weights, pd.Series):
        weights = pd.Series(weights)
    port = (returns @ weights.reindex(returns.columns).fillna(0.0)).dropna().values
    block = 21
    n = len(port)
    n_blocks = int(np.ceil(horizon_days / block))
    finals = np.empty(n_sims)
    for s in range(n_sims):
        starts = rng.integers(0, n - block, size=n_blocks)
        path = np.concatenate([port[i:i + block] for i in starts])[:horizon_days]
        finals[s] = np.exp(path.sum()) - 1
    pct = {p: float(np.percentile(finals, p)) for p in (5, 25, 50, 75, 95)}
    pct.update({"mean": float(finals.mean()), "prob_loss": float((finals < 0).mean())})
    pct["method"] = "Stationary block bootstrap of historical daily portfolio returns"
    pct["horizon_days"] = horizon_days
    return pct


def regime_features(returns: pd.DataFrame, asset: str = "AAPL") -> pd.DataFrame:
    """Features for regime classification: rolling momentum, vol, drawdown."""
    r = returns[asset].dropna()
    df = pd.DataFrame(index=r.index)
    df["mom_21"] = r.rolling(21).sum()
    df["mom_63"] = r.rolling(63).sum()
    df["vol_21"] = r.rolling(21).std() * np.sqrt(TRADING_DAYS)
    df["vol_ratio"] = df["vol_21"] / (r.rolling(126).std() * np.sqrt(TRADING_DAYS))
    wealth = (1 + r).cumprod()
    df["drawdown"] = wealth / wealth.cummax() - 1
    return df.dropna()


def regime_up_probability(returns: pd.DataFrame, asset: str = "AAPL",
                          seed: int = 42) -> dict | None:
    """RandomForest probability that next-63d return is positive, with walk-forward
    accuracy. Returns None if sklearn unavailable or data too short - never guesses."""
    try:
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:
        return None
    feats = regime_features(returns, asset)
    fwd = returns[asset].reindex(feats.index).rolling(63).sum().shift(-63)
    df = feats.assign(target=(fwd > 0).astype(int)).dropna()
    if len(df) < 150:
        return None
    X = df[["mom_21", "mom_63", "vol_21", "vol_ratio", "drawdown"]].values
    y = df["target"].values
    # walk-forward evaluation on the last 30% (no shuffling -> no look-ahead)
    split = int(len(X) * 0.7)
    clf = RandomForestClassifier(n_estimators=200, min_samples_leaf=10,
                                 random_state=seed, class_weight="balanced")
    clf.fit(X[:split], y[:split])
    acc = float((clf.predict(X[split:]) == y[split:]).mean())
    p_up = float(clf.predict_proba(X[-1:])[:, 1].item())
    return {"up_probability": p_up, "walkforward_accuracy": acc,
            "model": "RandomForest(200) on momentum/vol/drawdown features",
            "note": "Walk-forward accuracy of ~50-60% is common; treat as weak signal"}
