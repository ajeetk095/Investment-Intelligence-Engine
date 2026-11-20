"""Page 5: VaR/CVaR, drawdowns, Monte Carlo, live risk-free rate from FRED."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import streamlit as st

from config.settings import TICKERS, START_DATE, END_DATE, RISK_FREE_RATE_DEFAULT
from src import data_collection as dc
from src.data_processing import annualized_stats
from src.risk_analysis import (historical_var, historical_cvar, max_drawdown,
                               var_confidence, regime_flag, portfolio_return_series)

st.title("🛡️ Risk Analysis")
st.caption("All risk figures are historical estimates with sampling uncertainty — not worst-case guarantees.")

@st.cache_data(ttl=3600, show_spinner="Fetching data...")
def load(_tickers, start, end):
    prices = dc.fetch_prices(_tickers, start, end)
    return prices, dc.compute_returns(prices)

prices, returns = load(tuple(TICKERS), START_DATE, END_DATE)

rf_live, rf_date = dc.live_risk_free_rate()
rf_box = st.empty()
if rf_live is not None:
    rf = rf_box.number_input("Risk-free rate (live FRED 10y)", 0.0, 0.15, float(rf_live), 0.005,
                             help=f"FRED DGS10 as of {rf_date}")
    st.caption(f"Live risk-free rate loaded from FRED (DGS10, {rf_date}). "
               "FRED attribution: Federal Reserve Bank of St. Louis.")
else:
    rf = rf_box.number_input("Risk-free rate (FRED unavailable — manual)", 0.0, 0.15,
                             RISK_FREE_RATE_DEFAULT, 0.005)
    st.caption("FRED could not be reached; the manual 4% default from the original report is used.")

conf = st.slider("VaR confidence", 0.90, 0.99, 0.95, 0.01)
rows = []
for t in TICKERS:
    lo, hi = var_confidence(returns[t], conf)
    rows.append({"Asset": t, f"VaR {conf:.0%} (daily)": historical_var(returns[t], conf),
                 "VaR 90% CI": f"[{lo:.2%}, {hi:.2%}]",
                 f"CVaR {conf:.0%}": historical_cvar(returns[t], conf),
                 "Max Drawdown": max_drawdown(returns[t]),
                 "Regime (desc.)": regime_flag(returns[t])})
st.dataframe(pd.DataFrame(rows).style.format({
    f"VaR {conf:.0%} (daily)": "{:.2%}", f"CVaR {conf:.0%}": "{:.2%}",
    "Max Drawdown": "{:.2%}"}), width="stretch")

st.subheader("Portfolio-level risk")
st.markdown("Pick a strategy and see its own daily VaR/CVaR and drawdown across the sample.")
strategies = {"1/N Equal Weight": {t: 1 / len(TICKERS) for t in TICKERS}}
choice = st.selectbox("Strategy", list(strategies))
port = portfolio_return_series(pd.Series(strategies[choice]), returns)
c1, c2, c3 = st.columns(3)
c1.metric("Daily VaR", f"{historical_var(port, conf):.2%}")
c2.metric("Daily CVaR", f"{historical_cvar(port, conf):.2%}")
c3.metric("Max Drawdown", f"{max_drawdown(port):.2%}")
