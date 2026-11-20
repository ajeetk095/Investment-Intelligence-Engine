"""Shared user experience components for Streamlit pages."""
from __future__ import annotations

from datetime import date, datetime, timedelta
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
    """Fetch prices for the current snapshot/sandbox; short cache honors manual refresh."""
    return dc.fetch_prices(list(tickers), start, end)


def apply_colorful_theme() -> None:
    """Add consistent, accessible color accents without relying on external assets."""
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
        border: 1px solid rgba(103,232,249,.42); transition: transform .15s ease, box-shadow .15s ease; }
      div.stButton > button:hover, div.stFormSubmitButton > button:hover { transform: translateY(-1px);
        box-shadow: 0 6px 22px rgba(34,211,238,.18); border-color: #67e8f9; }
      [data-testid="stSidebar"] { background: linear-gradient(180deg,#121f34,#111827); }
      [data-testid="stExpander"] { border-color: rgba(148,163,184,.25); border-radius: 12px; }
      .market-note { color:#cbd5e1; font-size:.96rem; line-height:1.55; }
      .small-muted { color:#94a3b8; font-size:.82rem; }
    </style>
    """, unsafe_allow_html=True)


def _get_window(page_key: str) -> tuple[str, str, str]:
    """Select recent live data by default or the fixed original study window."""
    mode_key = f"{page_key}_data_window"
    options = ["Live market data · last 3 years", "Original GWP2 study window"]
    mode = st.sidebar.radio("Data view", options, key=mode_key,
                            help="Yahoo Finance data is delayed/end-of-day, not a real-time feed.")
    if mode == options[1]:
        return mode, START_DATE, END_DATE
    today = date.today()
    return mode, (today - timedelta(days=365 * 3)).isoformat(), (today + timedelta(days=1)).isoformat()


def setup_page_experience(page_key: str, tickers: list[str] | tuple[str, ...]) -> dict[str, str]:
    """Set theme, live-data controls, and an auto-refreshing plain-language market brief."""
    apply_colorful_theme()
    st.sidebar.markdown("### ⚙️ Market controls")
    mode, start, end = _get_window(page_key)
    left, right = st.sidebar.columns(2)
    if left.button("↻ Refresh", key=f"{page_key}_refresh", help="Clear cached market data and reload the latest available values."):
        st.cache_data.clear()
        st.rerun()
    if right.button("Reset", key=f"{page_key}_reset", help="Restore live data, default settings, and no active simulation."):
        for suffix, value in (("data_window", "Live market data · last 3 years"),
                              ("sim_asset", "Market basket"), ("sim_shock", 0), ("sim_horizon", 63)):
            st.session_state[f"{page_key}_{suffix}"] = value
        st.session_state[f"{page_key}_sim_ran"] = False
        st.cache_data.clear()
        st.rerun()
    st.caption("Live = latest available market data (typically delayed/end-of-day).")
    _render_live_brief(tuple(tickers))
    return {"mode": mode, "start": start, "end": end}


@st.fragment(run_every="60s")
def _render_live_brief(tickers: tuple[str, ...]) -> None:
    """Refresh the descriptive summary every minute; do not imply source prices are real-time."""
    today = date.today()
    start = (today - timedelta(days=180)).isoformat()
    end = (today + timedelta(days=1)).isoformat()
    with st.container(border=True):
        st.markdown("#### 🌤️ Market pulse · plain-language read")
        try:
            prices = _fetch_prices(tickers, start, end)
            daily = dc.compute_returns(prices)
            basket = daily.mean(axis=1).dropna()
            if basket.empty:
                raise ValueError("Not enough recent return data")
            recent = basket.tail(20)
            move = float((1 + recent).prod() - 1)
            daily_vol = float(recent.std()) if len(recent) > 1 else 0.0
            updated = prices.index.max().strftime("%b %d, %Y")
            if move > 0.02:
                summary = f"The selected assets have risen about {move:.1%} over their latest 20 trading days. Recent momentum is positive, but short-term gains can reverse; avoid making a decision from momentum alone."
                tag = "Recent trend: upward"
            elif move < -0.02:
                summary = f"The selected assets have fallen about {abs(move):.1%} over their latest 20 trading days. Recent momentum is weak; consider your time horizon and diversification rather than reacting to one stretch of prices."
                tag = "Recent trend: downward"
            else:
                summary = f"The selected assets are broadly range-bound over their latest 20 trading days ({move:+.1%}). A flat recent move does not remove investment risk; compare potential losses with your own tolerance."
                tag = "Recent trend: mixed / modest"
            if daily_vol > 0.02:
                summary += " Recent daily swings are relatively large, so smaller position sizes and a longer decision window may help manage risk."
            st.markdown(f"**{tag}**  ·  Equal-weight basket, latest prices dated **{updated}**")
            st.markdown(f'<div class="market-note">{summary}</div>', unsafe_allow_html=True)
            st.caption(f"Summary recalculated every 60 seconds from the latest cached source data. Source data may not change that often. {DATA_NOTICE}")
        except Exception as exc:  # graceful when external market data is unavailable
            st.info(f"A fresh market summary is unavailable right now. Use the page's last loaded results or press Refresh to retry. ({exc})")


def render_market_simulator(page_key: str, tickers: list[str] | tuple[str, ...], window: dict[str, str]) -> None:
    """Show a clearly labeled historical-bootstrap what-if projection, never a live forecast."""
    names = ["Market basket", *tickers]
    asset_key = f"{page_key}_sim_asset"
    with st.expander("🧪 Market sandbox · optional what-if simulation", expanded=False):
        st.markdown("Choose a historical return sample, a hypothetical one-time shock, and a horizon. "
                    "This is a resampling exercise—not a prediction of what the market will do. "
                    "Actual page results remain based on the selected data view.")
        col1, col2, col3 = st.columns([1.3, 1, 1])
        asset = col1.selectbox("Asset / group", names, key=asset_key)
        shock = col2.slider("Hypothetical initial shock", -30, 30, 0, 1, format="%d%%", key=f"{page_key}_sim_shock")
        horizon = col3.slider("Horizon (trading days)", 5, 252, 63, 5, key=f"{page_key}_sim_horizon")
        run = st.button("▶ Run what-if projection", type="primary", key=f"{page_key}_sim_button")
        if run:
            st.session_state[f"{page_key}_sim_ran"] = True
        if not st.session_state.get(f"{page_key}_sim_ran", False):
            st.caption("By default, the sandbox is inactive and all displayed market analysis uses the selected source data.")
            return
        try:
            prices = _fetch_prices(tuple(tickers), window["start"], window["end"])
            history = dc.compute_returns(prices)
            series = history.mean(axis=1) if asset == "Market basket" else history[asset]
            sample = series.dropna().tail(252).to_numpy(dtype=float)
            if len(sample) < 30:
                st.warning("At least 30 daily observations are needed for a useful resampling exercise.")
                return
            rng = np.random.default_rng(2026)
            draws = rng.choice(sample, size=(800, int(horizon)), replace=True)
            draws = np.clip(draws, -0.95, 5.0)
            paths = 100 * (1 + shock / 100) * np.cumprod(1 + draws, axis=1)
            median = np.percentile(paths, 50, axis=0)
            low = np.percentile(paths, 10, axis=0)
            high = np.percentile(paths, 90, axis=0)
            days = np.arange(1, int(horizon) + 1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=days, y=high, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=days, y=low, mode="lines", line=dict(width=0), fill="tonexty",
                                     fillcolor="rgba(56,189,248,.18)", name="Middle 80% of resampled paths"))
            fig.add_trace(go.Scatter(x=days, y=median, mode="lines", line=dict(color="#67e8f9", width=3), name="Median path"))
            fig.add_hline(y=100, line_dash="dash", line_color="#94a3b8", annotation_text="Starting value = 100")
            fig.update_layout(template="plotly_dark", height=390, margin=dict(l=12, r=12, t=30, b=12),
                              xaxis_title="Trading days (illustrative)", yaxis_title="Value of 100 units",
                              legend=dict(orientation="h", y=1.08))
            st.plotly_chart(fig, use_container_width=True)
            below = float((paths[:, -1] < 100).mean())
            st.markdown(f"**Plain-language read:** In this historical-resampling exercise, {below:.0%} of paths finish below the starting value. "
                        f"The median simulated value is {median[-1]:.1f} per 100 starting units.")
            st.caption(f"Uses the latest {len(sample)} observed daily returns and 800 bootstrap paths; initial scenario shock: {shock:+d}%. "
                       "Outcomes depend on the chosen history and omit future news, fees, taxes, and changing market conditions. Not investment advice.")
        except Exception as exc:
            st.error(f"Could not run the what-if simulation with the selected data: {exc}")


def render_disclaimer_footer(*additional_notices: str) -> None:
    """Render application-wide and page-specific disclosures at the bottom of a page."""
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
