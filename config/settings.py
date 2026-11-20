"""Central configuration for the GWP2 Investment Intelligence app."""
import os

TICKERS = ["AAPL", "NVDA", "TSLA", "XOM", "REGN", "LLY", "JPM"]

UNIVERSE_20 = [
    "AAPL", "MSFT", "GOOGL", "NVDA", "JNJ", "UNH", "PFE",
    "JPM", "BAC", "GS", "AMZN", "WMT", "HD", "XOM",
    "CVX", "CAT", "BA", "LIN", "APD", "NEE",
]

START_DATE = "2023-01-01"
END_DATE = "2025-06-30"          # original GWP2 estimation window
SIMULATION_START = "2022-01-01"  # Part 2 simulation window
SIMULATION_END = "2024-12-31"
DATA_INTERVAL = "1d"
TRADING_DAYS = 252

# 10y UST proxy used in the original report; overridden live by FRED DGS10 when reachable
RISK_FREE_RATE_DEFAULT = 0.04

TAU = 0.05            # Black-Litterman tau (report Section 4.1)
RISK_AVERSION = 2.5   # delta

# FRED series used for the live risk-free rate / macro panel
FRED_SERIES = {"DGS10": "10-Year Treasury Constant Maturity (%, daily)"}

DATA_NOTICE = (
    "Market data via Yahoo Finance (yfinance). Prices are end-of-day / delayed, "
    "unofficial and for research use only - not exchange-grade real-time feeds. "
    "Macro data via FRED (Federal Reserve Bank of St. Louis)."
)

APP_TITLE = "GWP2 Investment Intelligence"
APP_SUBTITLE = "Quantitative portfolio research platform - built on MScFE 652 GWP2 methodology"


def get_fred_api_key() -> str:
    """Read the FRED key from st.secrets (Streamlit) or environment. May be empty."""
    try:
        import streamlit as st  # noqa
        if hasattr(st, "secrets") and "FRED_API_KEY" in st.secrets:
            return str(st.secrets["FRED_API_KEY"])
    except Exception:
        pass
    return os.environ.get("FRED_API_KEY", "")
