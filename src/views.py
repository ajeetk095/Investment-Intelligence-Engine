"""GWP2 Part 3 (Step 6): analyst views for the 7 assets.
Views are reproduced from the original report (Table 12) with source attribution;
they are input assumptions for the Black-Litterman model, not verified forecasts."""
from __future__ import annotations

VIEWS = [
    {"asset": "AAPL", "value": 0.15, "confidence": 0.60,
     "rationale": "iPhone momentum and services growth; India manufacturing ramp.",
     "source": "Apple Q4 2024 earnings call; Morgan Stanley research (Jan 2025); IDC smartphone forecast"},
    {"asset": "NVDA", "value": 0.28, "confidence": 0.75,
     "rationale": "AI/data-center demand, Blackwell ramp, dominant training/inference position.",
     "source": "NVIDIA Q4 2024 earnings; Gartner AI semiconductor forecast; Goldman Sachs AI infra report (Dec 2024)"},
    {"long": "TSLA", "short": "XOM", "value": 0.12, "confidence": 0.50,
     "rationale": "EV adoption vs. long-run oil headwinds; FSD progress.",
     "source": "IEA Global EV Outlook 2024; EIA Short-Term Energy Outlook 2025"},
    {"asset": "XOM", "value": 0.09, "confidence": 0.65,
     "rationale": "Oil range $75-85/bbl, Guyana volume growth, dividend stability.",
     "source": "EIA Short-Term Energy Outlook 2025; ExxonMobil investor materials"},
    {"asset": "REGN", "value": 0.13, "confidence": 0.55,
     "rationale": "Eylea HD share gains and oncology pipeline vs. biosimilar risk.",
     "source": "Regeneron investor updates; sell-side pharma consensus (late 2024)"},
    {"long": "LLY", "short": "REGN", "value": 0.07, "confidence": 0.70,
     "rationale": "GLP-1 franchise (Mounjaro/Zepbound) growth outpaces REGN pipeline.",
     "source": "Eli Lilly earnings; industry GLP-1 demand forecasts"},
    {"asset": "JPM", "value": 0.11, "confidence": 0.60,
     "rationale": "NIM support from rates, strong trading revenue, buybacks.",
     "source": "JPMorgan Q4 2024 earnings; Fed rate path projections"},
]

MARKET_CAPS_B = {"AAPL": 3000, "NVDA": 2200, "TSLA": 800, "XOM": 450,
                 "REGN": 85, "LLY": 650, "JPM": 550}
