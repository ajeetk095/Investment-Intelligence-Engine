# Model Methodology — What Each Number Means

## Original GWP2 core (preserved)
| Model | Math | Purpose | Limitation |
|---|---|---|---|
| MVO Steps 1–3 | maximize (w'μ − rf)/√(w'Σw) s.t. Σw=1, bounds: [0,1] / [0,0.2] / [−2,2] | Optimal allocation per constraint regime; true optimization (SLSQP), never weight simulation | In-sample; μ estimated from history is noisy (the 1/N study quantifies the cost) |
| MVO vs 1/N (Step 5) | random 5-of-20 asset draws; 2y train → SLSQP MVO; 1y test; 5,000 reps; paired t, Wilcoxon, variance test | Tests whether optimization beats naive diversification out-of-sample | Single train/test split era (2022–2024); results are period-dependent |
| Black-Litterman (Steps 6–7) | posterior μ = (τΣ)⁻¹+P'Ω⁻¹P)⁻¹((τΣ)⁻¹π + P'Ω⁻¹Q), π = δΣw_mkt | Blends market equilibrium with analyst views; tames MVO corner solutions | Views are assumptions (documented in `src/views.py`), not verified forecasts |
| Kelly (Step 8) | w* = f·Σ⁻¹(μ−rf), f ∈ {0.5, 1, 2}; correlations included — the general formula, not the gambling formula | Growth-optimal leverage and its fragility | Full Kelly weights are extreme on 7 assets; treat as pedagogy, not a mandate |

## Enhancements (each added for a concrete purpose)
| Tool | Purpose | Assumptions / limits |
|---|---|---|
| Adjusted (total-return) prices | Include dividends/splits → fairer inputs than the original raw close | Yahoo corporate-action data can be revised |
| VaR / CVaR (historical, with bootstrap CI) | Tail-risk view absent from the original | Historical quantiles; CI only reflects sampling error |
| Max drawdown | Loss experience, not just volatility | Path-dependent; past drawdowns don't bound future ones |
| Block-bootstrap forecast | Forward distribution that keeps fat tails (unlike iid-normal MC) | Assumes future resembles resampled history |
| Monte Carlo (normal) paths | Scenario exploration with explicit iid-normal assumption | Understates tails — labelled as such in the app |
| Random-forest regime probability | Probabilistic, walk-forward-validated signal | ~coin-flip accuracy is common; displayed with its own accuracy and caution |
| Regime flag (Risk-On/Neutral/Off) | Descriptive trend/vol context | Rule-of-thumb thresholds, not a model forecast |
| Levene's variance test | Robust replacement for the raw F ratio in the MVO vs 1/N study | — |

## Signal rule book (BUY/HOLD/SELL)
`score = 0.5·z(historical Sharpe) + 0.3·z(BL posterior return) + 0.2·z(momentum)`; BUY ≥ +0.5, SELL ≤ −0.5, else HOLD.
Thresholds fixed in `src/recommendations.py`; no discretionary overrides. Signals are research outputs, not advice.

## Data lineage
Yahoo Finance (delayed, unofficial) for prices; FRED DGS10 for the risk-free rate (falls back to the report's 4% if FRED is unreachable). Every page shows the last successful update. Historical observations, model estimates, forecasts and hypothetical scenarios are labelled as such wherever they appear.
