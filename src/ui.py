"""Shared UI helpers for Streamlit pages."""
import streamlit as st

from config.settings import DATA_NOTICE


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
