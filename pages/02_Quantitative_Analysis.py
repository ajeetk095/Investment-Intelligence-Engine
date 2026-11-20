"""Page 2: MVO Steps 1-3 + efficient frontier (true optimization)."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import streamlit as st

from config.settings import TICKERS, START_DATE, END_DATE
from src import data_collection as dc, models, visualization as viz
from src.ui import render_disclaimer_footer

st.title("🧮 Quantitative Analysis — MVO (Steps 1–3)")
st.caption("True SLSQP optimization maximizing the Sharpe ratio. No weight simulation "
           "(assignment requirement). Inputs estimated on the Jan 2023 – Jun 2025 window.")

@st.cache_data(ttl=3600, show_spinner="Fetching data and optimizing...")
def run(_tickers, start, end, rf):
    prices = dc.fetch_prices(_tickers, start, end)
    returns = dc.compute_returns(prices)
    mu = returns.mean() * 252
    cov = returns.cov() * 252
    return {"step1": models.max_sharpe_portfolio(mu, cov, rf, allow_short=False, max_weight=1.0),
            "step2": models.max_sharpe_portfolio(mu, cov, rf, allow_short=False, max_weight=0.20),
            "step3": models.max_sharpe_portfolio(mu, cov, rf, allow_short=True),
            "mu": mu, "cov": cov}

rf = st.sidebar.number_input("Risk-free rate (annual)", 0.0, 0.15, 0.04, 0.005)
res = run(tuple(TICKERS), START_DATE, END_DATE, rf)

weights = {f"Step {i} – {name}": res[f"step{i}"]["weights"]
           for i, name in zip((1, 2, 3), ("Long-only", "20% cap", "Short allowed"))}
st.plotly_chart(viz.weights_bar(weights, "Optimal weights per constraint regime"), width="stretch")

table = pd.DataFrame({
    "Strategy": list(weights),
    **{t: [weights[k][t] for k in weights] for t in TICKERS},
    "Ann. Return": [res[f"step{i}"]["return"] for i in (1, 2, 3)],
    "Ann. Volatility": [res[f"step{i}"]["volatility"] for i in (1, 2, 3)],
    "Sharpe": [res[f"step{i}"]["sharpe"] for i in (1, 2, 3)],
})
st.dataframe(table.style.format({t: "{:.2%}" for t in TICKERS} |
                                {"Ann. Return": "{:.2%}", "Ann. Volatility": "{:.2%}", "Sharpe": "{:.3f}"}), width="stretch")

st.subheader("Efficient frontier (long-only)")
if st.button("Compute efficient frontier"):
    f = models.efficient_frontier(res["mu"], res["cov"], rf)
    st.plotly_chart(viz.frontier_chart(
        f, {t: float(np.sqrt(res["cov"].loc[t, t])) for t in TICKERS},
        {t: float(res["mu"][t]) for t in TICKERS},
        best={"volatility": res["step1"]["volatility"], "return": res["step1"]["return"]}),
        width="stretch")
    st.download_button("Download frontier CSV", f.to_csv(index=False), "efficient_frontier.csv")

render_disclaimer_footer()
