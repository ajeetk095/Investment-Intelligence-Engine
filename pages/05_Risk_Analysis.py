"""Page 5: historical loss measures and FRED risk-free-rate context."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import streamlit as st

from config.settings import TICKERS, RISK_FREE_RATE_DEFAULT
from src import data_collection as dc
from src.risk_analysis import historical_var, historical_cvar, max_drawdown, var_confidence, regime_flag, portfolio_return_series
from src.ui import render_disclaimer_footer, render_market_simulator, setup_page_experience

st.title("🛡️ Risk Analysis")
controls = setup_page_experience("risk", TICKERS)

@st.cache_data(ttl=60, show_spinner="Fetching data...")
def load(_tickers, start, end):
    prices = dc.fetch_prices(_tickers, start, end)
    return prices, dc.compute_returns(prices)

prices, returns = load(tuple(TICKERS), controls["start"], controls["end"])
rf_live, rf_date = dc.live_risk_free_rate()
if rf_live is not None:
    rf = st.sidebar.number_input("Risk-free rate (live FRED 10y)", 0.0, 0.15, float(rf_live), 0.005)
    st.caption(f"Live FRED DGS10 dated {rf_date}")
else:
    rf = st.sidebar.number_input("Risk-free rate (FRED unavailable)", 0.0, 0.15, RISK_FREE_RATE_DEFAULT, 0.005)
    st.caption("Using the original study's 4% default.")

st.markdown("**In everyday terms:** VaR estimates a loss threshold from past days; CVaR averages worse losses in the tail. Neither predicts the maximum loss you could experience.")
conf = st.slider("VaR confidence", 0.90, 0.99, 0.95, 0.01)
rows = []
for t in TICKERS:
    lo, hi = var_confidence(returns[t], conf)
    rows.append({"Asset": t, f"VaR {conf:.0%} (daily)": historical_var(returns[t], conf), "VaR 90% CI": f"[{lo:.2%}, {hi:.2%}]", f"CVaR {conf:.0%}": historical_cvar(returns[t], conf), "Max Drawdown": max_drawdown(returns[t]), "Regime (desc.)": regime_flag(returns[t])})
st.dataframe(pd.DataFrame(rows).style.format({f"VaR {conf:.0%} (daily)": "{:.2%}", f"CVaR {conf:.0%}": "{:.2%}", "Max Drawdown": "{:.2%}"}), width="stretch")

c1, c2, c3 = st.columns(3)
weights = pd.Series({t: 1 / len(TICKERS) for t in TICKERS})
port = portfolio_return_series(weights, returns)
c1.metric("Daily VaR", f"{historical_var(port, conf):.2%}")
c2.metric("Daily CVaR", f"{historical_cvar(port, conf):.2%}")
c3.metric("Max Drawdown", f"{max_drawdown(port):.2%}")

render_market_simulator("risk", TICKERS, controls)
render_disclaimer_footer("Risk measures are historical estimates subject to sampling uncertainty; VaR and CVaR do not guarantee or bound worst-case losses.")
