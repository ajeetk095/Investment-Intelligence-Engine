# GWP2 Investment Intelligence 📈

**Bridging Code & Capital** — a Streamlit platform that turns the MScFE 652 (WorldQuant University) Group Work Project 2 portfolio-optimization study into a working research tool on live market data.

Built by **Ajeet Kumar** — [LinkedIn](https://www.linkedin.com/in/ajeek095/) · [GitHub](https://github.com/ajeetk095) · [✉️ Hire me](mailto:ajeetk095@gmail.com?subject=Quant%20role%20inquiry)

## What it does
- **True portfolio optimization** (SLSQP max-Sharpe): long-only, 20% cap, short-allowed — Steps 1–3 of GWP2
- **MVO vs 1/N study**: 5,000 out-of-sample simulations with paired t / Wilcoxon / variance tests — Step 5
- **Black-Litterman** with seven documented analyst views (incl. relative views) — Steps 6–7
- **Kelly criterion** (general multivariate formula, correlations included): full/half/double via bootstrap paths — Step 8
- **Risk & forecasting layer**: VaR/CVaR with bootstrap CIs, drawdowns, block-bootstrap forecasts, walk-forward ML regime probabilities
- **Live data**: Yahoo Finance (delayed) + FRED risk-free rate, with graceful degradation — never fabricated numbers
- Every page explains its metrics in plain language; BUY/HOLD/SELL tags come from one published scoring rule

## Quick start (local)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (no local Python needed)
See `docs/DEPLOYMENT_GUIDE.md` — GitHub upload + Streamlit Community Cloud, ~15 minutes.

## Repository map
```
app.py                    Home page (dashboard, developer profile, hiring links)
pages/                    6 feature pages (market, quant, forecasts, insights, risk, methodology)
src/                      data_collection, data_processing, models, simulation, kelly,
                          black-litterman views, forecasting, risk_analysis, recommendations,
                          feature_engineering, visualization
config/settings.py        Single source of truth (tickers, windows, params, secrets access)
tests/                    27 tests incl. headless AppTest page smoke tests + security tests
docs/                     PROJECT_ANALYSIS, MODEL_METHODOLOGY, TEST_REPORT, SECURITY_AUDIT,
                          USER_GUIDE, DEPLOYMENT_GUIDE
```

## Data sources & disclaimer
Yahoo Finance (end-of-day, delayed, unofficial) and FRED (Federal Reserve Bank of St. Louis).
Everything shown is educational research output — **not investment advice**; estimates are not guarantees.

## License
MIT — see `LICENSE`.
