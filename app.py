"""GWP2 Investment Intelligence - Streamlit app entry point."""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config.settings import APP_TITLE, TICKERS
from src.ui import render_disclaimer_footer, render_market_simulator, setup_page_experience

st.set_page_config(page_title=APP_TITLE, page_icon="chart_with_upwards_trend", layout="wide", initial_sidebar_state="expanded")
controls = setup_page_experience("home", TICKERS)
st.sidebar.success("Navigate pages from the sidebar.")
st.title(APP_TITLE)
st.subheader("Bridging Code & Capital · quantitative portfolio research made easier to explore")

st.markdown("""
### Your portfolio research, in plain language
Explore current available market data, compare portfolio strategies, and see how risk changes under different assumptions.

| Explore | What you can learn |
|---|---|
| **Market Overview** | Prices, returns, volatility and how assets move together |
| **Quantitative Analysis** | How portfolio weights change under constraints |
| **Predictive Analytics** | How historical resampling illustrates a range of outcomes |
| **Investor Insights** | What model signals mean in everyday language |
| **Risk Analysis** | Historical loss measures and drawdowns |
| **Research Methodology** | How the original GWP2 study was conducted |

### A simple way to explore
1. Start with **Market Overview** for the selected period.
2. Compare returns with volatility; higher estimated returns can come with larger swings.
3. Try the optional **Market sandbox** to explore a hypothetical shock and horizon.
4. Use **Refresh** to reload cached prices or **Reset** to return to the default live-data view.
""")

render_market_simulator("home", TICKERS, controls)
render_disclaimer_footer()
