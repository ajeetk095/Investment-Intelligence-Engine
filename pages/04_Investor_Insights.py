"""Page 4: three audiences + evidence-based signals (Black-Litterman in the loop)."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import streamlit as st

from config.settings import TICKERS, START_DATE, END_DATE
from src import data_collection as dc, models, recommendations as rec
from src.data_processing import annualized_stats
from src.views import VIEWS, MARKET_CAPS_B
from src.ui import render_disclaimer_footer

st.title("💡 Investor Insights")
st.info("Signals below use a transparent scoring rule: "
        "0.5·z(historical Sharpe) + 0.3·z(Black-Litterman posterior return) + 0.2·z(momentum); "
        "BUY ≥ +0.5, SELL ≤ −0.5.")

@st.cache_data(ttl=3600, show_spinner="Fetching data and computing signals...")
def load(_tickers, start, end, rf):
    prices = dc.fetch_prices(_tickers, start, end)
    returns = dc.compute_returns(prices)
    cov = returns.cov() * 252
    mkt = pd.Series(MARKET_CAPS_B)[list(_tickers)]
    mkt = mkt / mkt.sum()
    from src.models import views_matrices, black_litterman
    P, Q, Om, desc = views_matrices(list(_tickers), VIEWS, cov)
    bl = black_litterman(cov, mkt, P, Q, Om)
    return returns, bl["posterior_mu"]

rf = st.sidebar.number_input("Risk-free rate (annual)", 0.0, 0.15, 0.04, 0.005)
returns, bl_mu = load(tuple(TICKERS), START_DATE, END_DATE, rf)
stats = annualized_stats(returns, rf)
scores = rec.asset_scores(stats, bl_mu, returns)

tab1, tab2, tab3 = st.tabs(["🛍️ Retail investors", "🏛️ Institutions & analysts", "🏢 Companies"])
with tab1:
    st.markdown("**In plain language**")
    best = scores.index[0]
    st.markdown(
        f"The model currently favours **{best}** (score {scores.loc[best,'Score']:.2f}, {scores.loc[best,'Signal']}). "
        f"Before acting, look at the Risk page: {stats['Ann. Volatility'].idxmax()} is the most volatile name here "
        f"({stats['Ann. Volatility'].max():.0%} a year), and a simple equal-weight portfolio historically beats "
        "more complex strategies out of sample about half the time.")
    st.dataframe(scores.style.format({"Score": "{:.2f}", "Momentum (ann.)": "{:.1%}",
                                      "Hist. Sharpe": "{:.2f}"}), width="stretch")
with tab2:
    st.markdown("**Quantitative view**")
    st.dataframe(pd.DataFrame({"BL posterior μ": bl_mu, "Hist μ (ann.)": stats["Ann. Return"],
                               "Hist σ (ann.)": stats["Ann. Volatility"]}).style.format("{:.2%}"),
                 width="stretch")
    for line in rec.strategy_guidance(rf, {}):
        st.markdown(f"- {line}")
with tab3:
    st.markdown("**Strategic read-across**")
    st.markdown("- Sector mix of optimized portfolios shifts with the risk-free input — rate changes directly "
                "move the financials vs. growth allocation.")
    st.markdown("- Correlations in this universe average well below 0.5, so cross-sector diversification "
                "remains effective; monitor the heatmap for convergence toward 1.")
    st.markdown("- The analyst views behind the Black-Litterman inputs are documented assumptions "
                "(see Research Methodology), not verified forecasts.")
st.download_button("Download signals CSV", scores.to_csv(), "asset_signals.csv")

render_disclaimer_footer(
    "Signals are research outputs from historical and model-derived data, not investment advice or recommendations. Analyst views in the Black-Litterman model are assumptions, not verified forecasts.",
)
