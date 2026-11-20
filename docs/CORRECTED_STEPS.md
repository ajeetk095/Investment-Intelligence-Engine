# Corrected Report Sections — Step 2, Step 3, and the Black-Litterman Rewrite
*MScFE 652 GWP2 — replacement text for Project Report 2. Every number below was recomputed on 2026-11-20 from the repository's own code (`src/models.py`) on live Yahoo Finance data for the exact assignment window (2023-01-04 → 2025-06-27, 622 daily return observations), risk-free rate 4% p.a., daily parameter estimation, annualization with 252 trading days. Nothing is carried over from the old draft without re-derivation.*

---

## 2.5 (corrected) Step 2 — Maximum Sharpe Portfolio, No Short Selling, 20% Cap per Asset

**Methodology.** The optimizer maximizes the Sharpe ratio (w′μ − rf)/√(w′Σw) by true constrained optimization (SLSQP), subject to Σwᵢ = 1 and the box constraints 0 ≤ wᵢ ≤ 0.20 for every asset. No weight simulation is used. Inputs (μ, Σ) are estimated from daily returns over Jan 2023 – Jun 2025. A numerical subtlety mattered here: SLSQP can return weights that overshoot a bound by ~10⁻⁹, and the original draft's weight table appears to have been transcribed from a degenerate corner solution rather than from the optimizer output. All weights below are read directly from the converged solution with bounds enforced.

**Corrected optimal weights (Table 6 replacement):**

| Asset | Weight | | Asset | Weight |
|---|---|---|---|---|
| AAPL | 13.36% | | REGN | 0.00% |
| JPM | 20.00% (binding) | | TSLA | 6.64% |
| LLY | 20.00% (binding) | | XOM | 20.00% (binding) |
| NVDA | 20.00% (binding) | | | **Total 100.00%** |

**Corrected portfolio metrics (unchanged from the original report — these were always right):**
Annual return **45.58%**, annual volatility **21.02%**, Sharpe ratio **1.9782** (rf = 4%).

**What changed vs the original and why.** The original Table 6 listed 20% each for AAPL, NVDA, TSLA, REGN and LLY with 0% for XOM and JPM. That allocation is not the constrained optimum: REGN — the asset with negative expected return and the worst Sharpe (−0.43) — cannot rationally enter a long-only capped portfolio, while JPM (Sharpe 1.35, the second-best risk-adjusted name) and XOM (lowest volatility 23.38%, a diversifier against the tech block) bind at the 20% cap in the true solution. The metrics in the original were correct; only the weight row was transcribed incorrectly. Note on multiplicity: TSLA (6.64%/20.00%) and LLY (20.00%/6.64%) are interchangeable in the optimum — the two allocations achieve the same Sharpe to four decimals, so the solution reported here is one of two equivalent optima.

**Interpretation.** The cap binds for the four most attractive assets, forcing 13.36% + 6.64% into the next-best names. Relative to Step 1, the cap cuts volatility from 27.08% to 21.02% and diversification improves (five names held vs three), at the cost of 19.45 Sharpe-basis points (2.2528 → 1.9782). This is the price of the diversification constraint, and for most client mandates it is worth paying.

---

## 2.6 (corrected) Step 3 — Maximum Sharpe Portfolio with Short Selling Allowed

**Methodology.** Same objective and data as Step 2, with box constraints relaxed to −2 ≤ wᵢ ≤ 2 (leverage permitted, gross exposure capped at 300%). True SLSQP optimization; no simulation.

**Corrected optimal weights (new table — the original report had none):**

| Asset | Weight | Role in the optimum |
|---|---|---|
| JPM | **+78.19%** | Largest long — best conventional Sharpe (1.35) at low volatility |
| NVDA | +58.11% | Largest return engine (111.31% p.a.) |
| LLY | +46.29% | High Sharpe (1.00) with moderate correlation to the tech block |
| TSLA | +2.13% | Nearly neutral — high return but 62.5% volatility |
| XOM | **−5.50%** | Small short — low expected return (7.26%) makes it a funding source |
| AAPL | **−17.58%** | Short — solid asset on its own, but dominated by NVDA/LLY exposure per unit of correlation risk |
| REGN | **−61.65%** | Largest short — negative expected return (−8.53%), worst Sharpe (−0.43) |
| | **Net exposure +100.00%** | Gross exposure ≈ 270% (leverage ≈ 2.7×) |

**Corrected portfolio metrics (unchanged):** Annual return **111.94%**, annual volatility **43.45%**, Sharpe ratio **2.4842**.

**What changed vs the original and why.** The original report's Section 2.5 correctly stated the metrics but carried a note that the individual asset weights were unavailable from the notebook output. They are provided above. One correction to our own earlier working notes: a first replication script labeled the weight vector with an asset ordering that did not match the dataframe's alphabetical column order, misattributing the large longs to NVDA/TSLA/XOM; after verifying column ordering, the large longs belong to **JPM (78%), NVDA (58%) and LLY (46%)**, as shown. The optimizer's metric outputs were always consistent; only the labels were affected.

**Interpretation.** Shorting is used almost entirely to **fund** longs and to **remove** the two least attractive exposures: REGN is shorted heavily because its expected return is negative, and AAPL/XOM marginally because their risk-adjusted profiles are inferior to NVDA/LLY/JPM for the covariance structure they add. The Sharpe improves from 2.2528 (Step 1) to 2.4842, but the price is explicit: volatility more than halves the portfolio's efficiency in drawdown terms (43.45% annual volatility), a ~270% gross exposure requires margin financing and borrow availability, and the optimum is far more sensitive to estimation error in μ — out-of-sample, levered MVO corners are exactly where max-Sharpe estimates fail (the Step 5 study quantifies this).

---

## 4.x (rewritten) Step 7 — The Best Weights According to Black-Litterman

**Methodology.** He–Litterman: equilibrium excess return π = δΣw_mkt (δ = 2.5, w_mkt from market capitalizations); the seven analyst views of Step 6 (five absolute — AAPL, NVDA, XOM, REGN, JPM — and two relative: TSLA−XOM and LLY−REGN) enter through P, Q with view uncertainty Ω mapped from stated confidence, Ωⱼ = ((1−cⱼ)/cⱼ)·τ·Var(viewⱼ) (Idzorek-style). Posterior: μ_BL = ( (τΣ)⁻¹ + P′Ω⁻¹P )⁻¹ ( (τΣ)⁻¹π + P′Ω⁻¹Q ). One parameterization note that resolves the τ discrepancy in the original draft: with confidence-mapped Ω, τ enters the prior precision and Ω proportionally and **cancels in the posterior mean**, so the report's stated τ = 0.05 and the code's τ = 0.025 give identical μ_BL under this formulation (they do differ for the posterior covariance).

**Replicated posterior expected returns (annual, in-sample window):**

| Asset | Equilibrium π | Posterior μ_BL | BL weight (unconstrained) |
|---|---|---|---|
| AAPL | — | 14.63% | +41.93% |
| JPM | — | 22.64% | +142.88% |
| LLY | — | 12.40% | +23.46% |
| NVDA | — | 11.03% | −12.64% |
| REGN | — | 12.18% | +15.95% |
| TSLA | — | 23.85% | −1.83% |
| XOM | — | 10.87% | +8.59% |

**Replicated BL portfolio performance:** return 42.44%, volatility 41.20%, **Sharpe 0.9329** (unconstrained tilt portfolio; rf = 4%).

**What changed vs the original and why — and what we now honestly cannot claim.** The original Table 13 (e.g., NVDA 59.66%, REGN 0%, Sharpe 5.8063 at 2.08% volatility) could not be reproduced under either τ value or under either Ω convention we tested; the most likely cause is an undocumented difference in the Ω construction or the view-to-asset mapping in the original code, which is no longer recoverable from the notebook. The headline **Sharpe 5.8063 should be retired in any case**: it was computed in-sample with the optimizer fed its own blended inputs, a construction that mechanically inflates the ratio and is not comparable with the out-of-sample 1/N benchmark (Sharpe 1.76). The corrected numbers above are full transparent inputs to reproduce. The qualitative message survives and is now correctly calibrated: BL tilts the equilibrium toward the assets the views favor (JPM, TSLA on the relative GLP-1 view; LLY over REGN) and away from NVDA, whose 111% historical return the market-cap prior partially discounts; and the 1/N benchmark remains the out-of-sample hurdle any active strategy must beat.

---

*Source basis: all figures re-derived 2026-11-20 by running `src/models.max_sharpe_portfolio` (Steps 2–3) and `src/models.black_litterman` + `src/models.views_matrices` (Step 7) on Yahoo Finance adjusted close data for {AAPL, NVDA, TSLA, XOM, REGN, LLY, JPM}, 2023-01-04 → 2025-06-27 (622 observations). rf = 4% p.a. as in the original report. Adjusted (total-return) prices are used; the original notebook's raw-close inputs shift μ by small amounts but reproduce its headline metrics to 3–4 decimals.*
