"""Page 3: historical bootstrap scenarios and machine-learning signals."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

from config.settings import TICKERS
from src import data_collection as dc, visualization as viz
from src.forecasting import bootstrap_forecast, regime_up_probability
from src.ui import render_disclaimer_footer, render_market_simulator, setup_page_experience

st.title("🔮 Predictive Analytics")
controls = setup_page_experience("predict", TICKERS)

@st.cache_data(ttl=60, show_spinner="Fetching data and running models...")
def load(_tickers, start, end):
    prices = dc.fetch_prices(_tickers, start, end)
    return prices, dc.compute_returns(prices)

prices, returns = load(tuple(TICKERS), controls["start"], controls["end"])
st.subheader("1) Block-bootstrap portfolio range")
st.markdown("Resamples blocks of historical daily returns to illustrate a range of possible outcomes. "
            "This is a historical scenario, not a forecast of future market performance.")
col1, col2 = st.columns(2)
strategy = col1.selectbox("Portfolio illustration", ["1/N equal weight", "MVO 20% cap (proxy: equal weight of 5 names)"])
horizon = col2.slider("Horizon (trading days)", 21, 504, 252, 21)
w = {t: 1 / len(TICKERS) for t in TICKERS}
fc = bootstrap_forecast(returns, w, horizon_days=int(horizon))
st.plotly_chart(viz.monte_carlo_fan(fc, f"Illustrative range · {horizon} trading days"), width="stretch")
st.markdown(f"**In plain language:** resampled average outcome **{fc['mean']:.1%}** · simulated paths ending below zero **{fc['prob_loss']:.1%}** · "
            f"middle 90% range [{fc[5]:.1%}, {fc[95]:.1%}]")
st.subheader("2) Regime probability (machine learning)")
st.markdown("The model estimates whether a ticker's next-quarter return would have been positive based on historical features; "
            "walk-forward validation reduces look-ahead but cannot remove uncertainty.")
ticker = st.selectbox("Ticker", TICKERS)
ml = regime_up_probability(returns, ticker)
if ml is None:
    st.info("Model unavailable for this input (insufficient data). Nothing is fabricated.")
else:
    c1, c2 = st.columns(2)
    c1.metric(f"Historical model P(next 63d up) — {ticker}", f"{ml['up_probability']:.1%}")
    c2.metric("Walk-forward accuracy", f"{ml['walkforward_accuracy']:.1%}")
    st.caption(ml["note"])

render_market_simulator("predict", TICKERS, controls)
render_disclaimer_footer(
    "Forecast-style charts and regime probabilities are model estimates with substantial uncertainty, not predictions of future market performance.",
    "Bootstrap forecasts assume future returns resemble the resampled history; regime shifts are not modeled. Machine-learning outputs are weak signals, not investment recommendations.",
)
