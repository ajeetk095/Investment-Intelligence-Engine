"""Evidence-based recommendation layer. BUY/HOLD/SELL flags are generated ONLY from
the model's own computed signals with a transparent rule book - nothing hand-picked."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import TRADING_DAYS

# Transparent rule book (documented in docs/MODEL_METHODOLOGY.md):
#   score = 0.5*z(historical Sharpe) + 0.3*z(BL posterior return) + 0.2*z(momentum)
#   BUY >= +0.5 | HOLD in (-0.5, +0.5) | SELL <= -0.5


def asset_scores(hist_stats: pd.DataFrame, bl_mu: pd.Series | None,
                 returns: pd.DataFrame) -> pd.DataFrame:
    mom = (1 + returns).prod() ** (TRADING_DAYS / len(returns)) - 1
    def z(s):
        s = s.astype(float)
        sd = s.std(ddof=0)
        return (s - s.mean()) / sd if sd > 0 else s * 0
    score = 0.5 * z(hist_stats["Sharpe Ratio"]) + 0.2 * z(mom)
    score = score.add(0.3 * z(bl_mu) if bl_mu is not None else 0.0, fill_value=0)
    labels = np.select([score >= 0.5, score <= -0.5], ["BUY", "SELL"], default="HOLD")
    return pd.DataFrame({"Score": score, "Signal": labels,
                         "Momentum (ann.)": mom,
                         "Hist. Sharpe": hist_stats["Sharpe Ratio"]}).sort_values("Score", ascending=False)


def strategy_guidance(rf: float, results: dict) -> list[str]:
    """Conditional, transparent guidance derived from computed results only."""
    lines = []
    s1, s2, s3 = results.get("step1"), results.get("step2"), results.get("step3")
    if s1 and s2:
        lines.append(
            f"The capped portfolio (Sharpe {s2['sharpe']:.2f}, vol {s2['volatility']:.1%}) trades "
            f"{(s1['sharpe']-s2['sharpe']):.2f} Sharpe points versus the uncapped version for materially "
            "lower concentration risk - suitable as the default mandate.")
    if s3:
        lines.append(
            f"Short-selling lifts the modelled Sharpe to {s3['sharpe']:.2f} but at {s3['volatility']:.1%} "
            "volatility with leverage, margin cost and borrow risk - only for sophisticated mandates.")
    lines.append("1/N equal-weight remains a hard out-of-sample benchmark: prefer it whenever "
                 "expected-return estimates are weak (DeMiguel et al. 2009).")
    lines.append(f"Risk-free input: {rf:.2%} (FRED DGS10 when available). All figures are "
                 "model estimates from historical data, not guarantees.")
    return lines
