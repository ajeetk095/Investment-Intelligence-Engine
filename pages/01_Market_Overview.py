"""Page 1: live market overview."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd

from config.settings import TICKERS
from src import data_collection as dc
from src import data_processing as dp
from src import visualization as viz
from src.ui import render_disclaimer_footer, render_market_simulator, setup_page_experience

st.title("📊 Market Overview")
controls = setup_page_experience("market", TICKERS)

@st.cache_data(ttl=60, show_spinner="Fetching latest available data from Yahoo Finance...")
def load(_tickers, start, end):
    prices = dc.fetch_prices(_tickers, start, end)
    return prices, dc.compute_returns(prices), dc.data_freshness(prices)

try:
    prices, returns, freshness = load(tuple(TICKERS), controls["start"], controls["end"])
except Exception as e:
    st.error(f"Data unavailable right now ({e}). Nothing is fabricated - please use Refresh to retry later.")
    st.stop()

st.success(f"🕒 {freshness} · Source: Yahoo Finance (delayed, unofficial)")
qc = dc.quality_checks(prices)
if not qc["pass"]:
    st.warning("Data quality issues: " + "; ".join(qc["issues"]))

rf = st.sidebar.number_input("Risk-free rate (annual)", 0.0, 0.15, 0.04, 0.005,
                             help="Override with the live FRED 10y yield on the Risk page")
st.caption("A return is how much an investment changed; volatility describes how widely its returns have swung.")
stats = dp.annualized_stats(returns, rf)
st.subheader("Descriptive statistics")
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

render_market_simulator("market", TICKERS, controls)
render_disclaimer_footer()
