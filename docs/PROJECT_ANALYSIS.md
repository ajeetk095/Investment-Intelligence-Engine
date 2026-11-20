# Findings Memo — Original GWP2 Analysis, Code–Report Consistency Check
*(All verification runs executed 2026-11-20 on live Yahoo Finance data for the exact GWP2 window, Jan 3 2023 – Jun 27 2025, 622 return observations.)*

## 1. What was inspected
| File | Contents |
|---|---|
| `MScFE 652 PM GWP2 Set E (09.30.25).pdf` | Assignment (Set E): Steps 0–8, constraints, rubric. Groups of 1 student: Steps 0,1,2,4,5 + (6&7 **or** 8). |
| `GWP2 notebook (.ipynb)` | 27 cells implementing Steps 0–8 with SLSQP MVO, 5,000-run MVO vs 1/N simulation, Black-Litterman (tau=0.025 in code), Kelly weights + static-weight comparison. Stored outputs were extracted and read. |
| `Project Report 2 (PDF)` | 13-page report: executive summary, Steps 0–7 write-ups, tables 1–14, MLA references. |

## 2. Numbers re-run on live data vs the report — CONFIRMED ✔
| Metric | Report | Re-run (live data, same window/method) |
|---|---|---|
| Observations / window | 622 returns, 2023-01-03→2025-06-27 | identical |
| Step 1 (long-only) | ret 65.02%, vol 27.08%, Sharpe 2.2528; NVDA 41.28%, TSLA 20.36%, XOM 38.36% | **exact match to 4 decimals** (Sharpe 2.25276, identical weights) |
| Step 2 (20% cap) | ret 45.58%, vol 21.02%, Sharpe 1.9782 | **exact match** (45.577%, 21.017%, 1.97824) |
| Step 3 (short allowed) | ret 111.94%, vol 43.45%, Sharpe 2.4842 | **exact match** (111.99%, 43.47%, 2.48419) |
| Step 0 statistics | e.g. NVDA 111.31%/53.16%/skew 0.797; REGN −8.53%/skew −2.106/kurt 20.79; avg corr 0.229 | **all exact** |

The core Part 1 research is solid and reproducible. Data note: the notebook used raw close prices ("'Adj Close' not found" warning in its output); the rebuild uses auto-adjusted (total-return) prices, which is more defensible.

## 3. Errors and inconsistencies found — with evidence
1. **Step 2 weight table in the report is wrong.** Report Table 6 claims weights of 20% each for AAPL, NVDA, TSLA, REGN, LLY and 0% for XOM/JPM. Re-optimization gives: **AAPL 13.36%, NVDA 20%, TSLA 20%, XOM 20%, REGN 0%, LLY 6.64%, JPM 20%** (verified 2026-11-20; LLY and TSLA are interchangeable at 20%/6.64% — two equivalent optima, identical Sharpe to 4 decimals). Portfolio metrics are right; the weight table is not (it looks like a degenerate corner solution was hand-copied). The deliverable app computes and displays true weights.
2. **Step 3 weights missing from the report** (acknowledged in its own note: "the notebook output does not show the individual asset weights"). Actual optimum (label-corrected 2026-11-20 after verifying dataframe column ordering — an initial verification script mislabeled the vector): **JPM +78.19%, NVDA +58.11%, LLY +46.29%, TSLA +2.13%, XOM −5.50%, AAPL −17.58%, REGN −61.65%** — REGN and AAPL shorted to fund the JPM/NVDA/LLY longs, consistent with the report's narrative. See docs/CORRECTED_STEPS.md for the drafted replacement sections.
3. **Black-Litterman results are not reproducible as stated.** The report says tau = 0.05; the notebook code uses `tau=0.025`. A He-Litterman replication (tau = 0.05, delta = 2.5, report's views and market caps) yields (confidence-mapped Ω) BL weights JPM +142.9%, AAPL +41.9%, LLY +23.5%, REGN +16.0%, XOM +8.6%, TSLA −1.8%, NVDA −12.6% (Sharpe 0.9329) — materially different from report Table 13 (e.g. REGN 0%, NVDA 59.66%); the original Table 13 could not be reproduced under either tau or either Omega convention. Full replacement section drafted in docs/CORRECTED_STEPS.md. The headline **Sharpe 5.8063 with 2.08% volatility is an in-sample artifact** (optimizer fed its own blended inputs); it is not comparable with the out-of-sample 1/N result and should not anchor the recommendation.
4. **Kelly section (Step 8) is weak but present.** The original compares static full/half/double Kelly weights over one historical year; the printed "RECOMMENDATION: Double Kelly (f=2.0)" contradicts its own text ("Generally NOT recommended"). The rebuild compares the three fractions across hundreds of bootstrap paths with periodic rebalancing on an expanding window, and reports growth/drawdown trade-offs without a canned pick.
5. **Statistical-test phrasing.** The paired t-test significance (+7.73% mean for MVO) coexists with a *worse* MVO Sharpe (0.72 vs 1.76) and a 43% win rate; the report's conclusion section states this correctly, but the notebook's printed banner ("MVO significantly outperforms 1/N") overstates it. The variance test is a raw F ratio in the original; the rebuild uses Levene's robust test.
6. **Boundary hygiene.** SLSQP can return weights that overshoot bounds by ~1e-9; the original didn't clip (Step 2's table may partly stem from this). The rebuild clips to bounds and unit-tests every constraint set.

## 4. Gaps (stated, not invented)
- No Part 4 (Kelly) section in the report PDF — required for a 3-student group; the code exists but the 2-page presentation is not in the uploaded report.
- No efficient-frontier chart and no Step 3 weight table in the report.
- Market caps are hardcoded approximations (early-2025), not fetched live.
- Analyst views (Step 6) are assumptions with cited sources, but no live re-validation.
- Notebook header says "February 2026" while the report is dated February 26, 2026 — consistent, but the period under study ends June 2025 (per assignment).
