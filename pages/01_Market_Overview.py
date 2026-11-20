"""Page 1: live market overview."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd

from config.settings import TICKERS, START_DATE, END_DATE, DATA_NOTICE
from src import data_collection as dc
from src import data_processing as dp
from src import visualization as viz

st.title("📊 Market Overview")
st.caption(DATA_NOTICE)

@st.cache_data(ttl=3600, show_spinner="Fetching live data from Yahoo Finance...")
def load(_tickers, start, end):
    prices = dc.fetch_prices(_tickers, start, end)
    return prices, dc.compute_returns(prices), dc.data_freshness(prices)

window = st.radio(
    "Data window",
    ["Live: last 3 years up to today", "GWP2 estimation window (Jan 2023 - Jun 2025)"],
    horizontal=True)
if window.startswith("Live"):
    _end = pd.Timestamp.today().strftime("%Y-%m-%d")
    _start = (pd.Timestamp.today() - pd.DateOffset(years=3)).strftime("%Y-%m-%d")
else:
    _start, _end = START_DATE, END_DATE

try:
    prices, returns, freshness = load(tuple(TICKERS), _start, _end)
except Exception as e:
    st.error(f"Data unavailable right now ({e}). Nothing is fabricated - please retry later.")
    st.stop()

st.success(f"🕒 {freshness} · Source: Yahoo Finance (delayed, unofficial)")
qc = dc.quality_checks(prices)
if not qc["pass"]:
    st.warning("Data quality issues: " + "; ".join(qc["issues"]))

rf = st.sidebar.number_input("Risk-free rate (annual)", 0.0, 0.15, 0.04, 0.005,
                             help="Override with the live FRED 10y yield on the Risk page")

stats = dp.annualized_stats(returns, rf)
st.subheader("Descriptive statistics (Step 0)")
st.dataframe(stats.style.format({"Ann. Return": "{:.2%}", "Ann. Volatility": "{:.2%}",
                                 "Sharpe Ratio": "{:.3f}", "Skewness": "{:.3f}",
                                 "Excess Kurtosis": "{:.3f}"}), width="stretch")

col1, col2 = st.columns(2)
with col1:
    norm = st.toggle("Show normalized (start = 100)")
    st.plotly_chart(viz.price_chart(prices, normalized=norm), width="stretch")
with col2:
    st.plotly_chart(viz.correlation_heatmap(dp.correlation_matrix(returns)), width="stretch")
    st.metric("Average pairwise correlation", f"{dp.avg_pairwise_correlation(returns):.3f}")
