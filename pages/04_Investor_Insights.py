"""Page 4: plain-language investor insights and transparent model signals."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import streamlit as st

from config.settings import TICKERS
from src import data_collection as dc, recommendations as rec
from src.data_processing import annualized_stats
from src.views import VIEWS, MARKET_CAPS_B
from src.ui import render_disclaimer_footer, render_market_simulator, setup_page_experience

st.title("💡 Investor Insights")
controls = setup_page_experience("insights", TICKERS)
st.caption("Model signals summarize historical data and assumptions. They are not personalized instructions to buy or sell.")

@st.cache_data(ttl=60, show_spinner="Fetching data and computing signals...")
def load(_tickers, start, end):
    prices = dc.fetch_prices(_tickers, start, end)
    returns = dc.compute_returns(prices)
    cov = returns.cov() * 252
    mkt = pd.Series(MARKET_CAPS_B)[list(_tickers)].fillna(0)
    mkt = mkt / mkt.sum()
    from src.models import views_matrices, black_litterman
    P, Q, Om, desc = views_matrices(list(_tickers), VIEWS, cov)
    bl = black_litterman(cov, mkt, P, Q, Om)
    return returns, bl["posterior_mu"]

rf = st.sidebar.number_input("Risk-free rate (annual)", 0.0, 0.15, 0.04, 0.005)
returns, bl_mu = load(tuple(TICKERS), controls["start"], controls["end"])
stats = annualized_stats(returns, rf)
scores = rec.asset_scores(stats, bl_mu, returns)

with st.expander("How to read these signals", expanded=True):
    st.markdown("The score blends historical risk-adjusted returns, Black-Litterman assumptions, and recent momentum. Higher ranking means stronger model output within this sample—not certainty of future performance.")

t1, t2, t3 = st.tabs(["🛍️ Everyday view", "🏛️ Quantitative view", "🏢 Business context"])
with t1:
    st.markdown("**Simple takeaway:** compare the leading score with volatility and historical drawdown. Consider diversification and whether you could tolerate a fall in value.")
    st.dataframe(scores.style.format({"Score": "{:.2f}", "Momentum (ann.)": "{:.1%}", "Hist. Sharpe": "{:.2f}"}), width="stretch")
with t2:
    st.dataframe(pd.DataFrame({"BL posterior μ": bl_mu, "Hist μ (ann.)": stats["Ann. Return"], "Hist σ (ann.)": stats["Ann. Volatility"]}).style.format("{:.2%}"), width="stretch")
    for line in rec.strategy_guidance(rf, {}): st.markdown(f"- {line}")
with t3:
    st.markdown("- Portfolio weights respond to estimates and the risk-free-rate assumption.")
    st.markdown("- Diversification can reduce one-company exposure, but not market-wide losses.")
    st.markdown("- Black-Litterman analyst views are assumptions, not verified forecasts.")
st.download_button("Download signals CSV", scores.to_csv(), "asset_signals.csv")

render_market_simulator("insights", TICKERS, controls)
render_disclaimer_footer("Signals are research outputs, not personalized investment advice or recommendations.")
