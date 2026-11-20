"""Shared user experience components for Streamlit pages."""
from __future__ import annotations

from datetime import date, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.settings import DATA_NOTICE, END_DATE, START_DATE
from src import data_collection as dc


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_prices(tickers: tuple[str, ...], start: str, end: str) -> pd.DataFrame:
    return dc.fetch_prices(list(tickers), start, end)


def apply_colorful_theme() -> None:
    st.markdown("""
    <style>
      .stApp { background: radial-gradient(ellipse at 12% 0%, #142b48 0%, #101827 42%, #0b1220 100%); }
      [data-testid="stHeader"] { background: rgba(11,18,32,.78); }
      h1 { color: #f3f7ff; letter-spacing: -.035em; }
      h2, h3 { color: #a9d6ff; }
      [data-testid="stMetric"] { background: linear-gradient(135deg,rgba(56,189,248,.13),rgba(167,139,250,.13));
        border: 1px solid rgba(148,163,184,.24); padding: 14px; border-radius: 14px; }
      [data-testid="stMetricValue"] { color: #67e8f9; }
      div.stButton > button, div.stFormSubmitButton > button { border-radius: 10px; font-weight: 650;
        border: 1px solid rgba(103,232,249,.42); }
      [data-testid="stSidebar"] { background: linear-gradient(180deg,#121f34,#111827); }
      .market-note { color:#cbd5e1; font-size:.96rem; line-height:1.55; }
    </style>
    """, unsafe_allow_html=True)


def setup_page_experience(page_key: str, tickers: list[str] | tuple[str, ...]) -> dict[str, str]:
    apply_colorful_theme()
    st.sidebar.markdown("### ⚙️ Market controls")
    options = ["Live market data · last 3 years", "Original GWP2 study window"]
    mode = st.sidebar.radio("Data view", options, key=f"{page_key}_data_window")
    left, right = st.sidebar.columns(2)
    if left.button("↻ Refresh", key=f"{page_key}_refresh"):
        st.cache_data.clear()
        st.rerun()
    if right.button("Reset", key=f"{page_key}_reset"):
        for suffix, value in (("data_window", options[0]), ("sim_asset", "Market basket"),
                              ("sim_shock", 0), ("sim_horizon", 63)):
            st.session_state[f"{page_key}_{suffix}"] = value
        st.session_state[f"{page_key}_sim_ran"] = False
        st.cache_data.clear()
        st.rerun()

    if mode == options[1]:
        start, end = START_DATE, END_DATE
    else:
        today = date.today()
        start = (today - timedelta(days=365 * 3)).isoformat()
        end = (today + timedelta(days=1)).isoformat()

    st.caption("Live = latest available Yahoo Finance data, normally delayed/end-of-day.")
    _render_live_brief(tuple(tickers))
    return {"mode": mode, "start": start, "end": end}


@st.fragment(run_every="60s")
def _render_live_brief(tickers: tuple[str, ...]) -> None:
    today = date.today()
    start = (today - timedelta(days=180)).isoformat()
    end = (today + timedelta(days=1)).isoformat()
    with st.container(border=True):
        st.markdown("#### 🌤️ Market pulse · plain-language read")
        try:
            prices = _fetch_prices(tickers, start, end)
            basket = dc.compute_returns(prices).mean(axis=1).dropna().tail(20)
            if basket.empty:
                raise ValueError("Not enough recent return data")
            move = float((1 + basket).prod() - 1)
            daily_vol = float(basket.std())
            updated = prices.index.max().strftime("%b %d, %Y")
            if move > 0.02:
                tag = "Recent trend: upward"
                summary = f"The selected assets have risen about {move:.1%} over the latest 20 trading days. Recent momentum is positive, but gains can reverse quickly."
            elif move < -0.02:
                tag = "Recent trend: downward"
                summary = f"The selected assets have fallen about {abs(move):.1%} over the latest 20 trading days. Recent momentum is weak; consider time horizon and diversification before reacting."
            else:
                tag = "Recent trend: mixed / modest"
                summary = f"The selected assets are broadly range-bound over the latest 20 trading days ({move:+.1%}). A flat stretch does not remove investment risk."
            if daily_vol > 0.02:
                summary += " Recent daily swings are relatively large, so risk tolerance and position size matter."
            st.markdown(f"**{tag}** · Latest available prices dated **{updated}**")
            st.markdown(f'<div class="market-note">{summary}</div>', unsafe_allow_html=True)
            st.caption(f"Refreshed every 60 seconds. {DATA_NOTICE}")
        except Exception as exc:
            st.info(f"A fresh market summary is unavailable. Use Refresh to retry. ({exc})")


def render_market_simulator(page_key: str, tickers: list[str] | tuple[str, ...], window: dict[str, str]) -> None:
    names = ["Market basket", *tickers]
    with st.expander("🧪 Market sandbox · optional what-if simulation", expanded=False):
        st.markdown("Explore a hypothetical shock using historical resampling. The sandbox is inactive by default; normal results remain based on the selected live or original dataset.")
        c1, c2, c3 = st.columns([1.3, 1, 1])
        asset = c1.selectbox("Asset / group", names, key=f"{page_key}_sim_asset")
        shock = c2.slider("Hypothetical initial shock", -30, 30, 0, 1, format="%d%%", key=f"{page_key}_sim_shock")
        horizon = c3.slider("Horizon (trading days)", 5, 252, 63, 5, key=f"{page_key}_sim_horizon")
        if st.button("▶ Run what-if projection", type="primary", key=f"{page_key}_sim_button"):
            st.session_state[f"{page_key}_sim_ran"] = True
        if not st.session_state.get(f"{page_key}_sim_ran", False):
            st.caption("By default, no simulation is active.")
            return
        try:
            prices = _fetch_prices(tuple(tickers), window["start"], window["end"])
            history = dc.compute_returns(prices)
            series = history.mean(axis=1) if asset == "Market basket" else history[asset]
            sample = series.dropna().tail(252).to_numpy(dtype=float)
            if len(sample) < 30:
                st.warning("At least 30 observations are needed.")
                return
            rng = np.random.default_rng(2026)
            draws = rng.choice(sample, size=(800, int(horizon)), replace=True)
            paths = 100 * (1 + shock / 100) * np.cumprod(1 + np.clip(draws, -0.95, 5.0), axis=1)
            median = np.percentile(paths, 50, axis=0)
            low = np.percentile(paths, 10, axis=0)
            high = np.percentile(paths, 90, axis=0)
            days = np.arange(1, int(horizon) + 1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=days, y=high, mode="lines", line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=days, y=low, mode="lines", line=dict(width=0), fill="tonexty", fillcolor="rgba(56,189,248,.18)", name="Middle 80% of paths"))
            fig.add_trace(go.Scatter(x=days, y=median, mode="lines", line=dict(color="#67e8f9", width=3), name="Median path"))
            fig.add_hline(y=100, line_dash="dash", line_color="#94a3b8")
            fig.update_layout(template="plotly_dark", height=390, margin=dict(l=12, r=12, t=30, b=12), xaxis_title="Trading days", yaxis_title="Value of 100 units")
            st.plotly_chart(fig, use_container_width=True)
            below = float((paths[:, -1] < 100).mean())
            st.markdown(f"**Plain-language read:** {below:.0%} of historical-resampling paths finish below the starting value; the median finishes at {median[-1]:.1f} per 100 starting units.")
            st.caption(f"800 bootstrap paths; initial shock {shock:+d}%. This exercise omits future news, fees, taxes and changing market conditions. Not investment advice.")
        except Exception as exc:
            st.error(f"Could not run the simulation: {exc}")


def render_disclaimer_footer(*additional_notices: str) -> None:
    notices = [
        "This application is for educational and research purposes only. It is not investment advice; model estimates are uncertain and are not guarantees.",
        DATA_NOTICE,
        "Market-data attribution: Yahoo Finance. Macro-data attribution: FRED (Federal Reserve Bank of St. Louis).",
        *[notice for notice in additional_notices if notice],
    ]
    st.divider()
    st.markdown("#### Disclaimers & data sources")
    for notice in notices:
        st.caption(notice)
