"""Central configuration for the Investment-Intelligence-Engine app."""
import os

TICKERS = ["AAPL", "NVDA", "TSLA", "XOM", "REGN", "LLY", "JPM"]
UNIVERSE_20 = ["AAPL", "MSFT", "GOOGL", "NVDA", "JNJ", "UNH", "PFE", "JPM", "BAC", "GS", "AMZN", "WMT", "HD", "XOM", "CVX", "CAT", "BA", "LIN", "APD", "NEE"]
START_DATE = "2023-01-01"
END_DATE = "2025-06-30"
SIMULATION_START = "2022-01-01"
SIMULATION_END = "2024-12-31"
DATA_INTERVAL = "1d"
TRADING_DAYS = 252
RISK_FREE_RATE_DEFAULT = 0.04
TAU = 0.05
RISK_AVERSION = 2.5
FRED_SERIES = {"DGS10": "10-Year Treasury Constant Maturity (%, daily)"}
DATA_NOTICE = "Market data via Yahoo Finance (yfinance). Prices are end-of-day/delayed and unofficial. Macro data via FRED (Federal Reserve Bank of St. Louis)."
APP_TITLE = "Investment-Intelligence-Engine"
APP_SUBTITLE = "Quantitative portfolio research platform — built on MScFE 652 GWP2 methodology"

def get_fred_api_key() -> str:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "FRED_API_KEY" in st.secrets:
            return str(st.secrets["FRED_API_KEY"])
    except Exception:
        pass
    return os.environ.get("FRED_API_KEY", "")
