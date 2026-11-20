# Test Report — GWP2 Investment Intelligence
*All results below are copied from actual runs executed in this build session (2026-11-20, Python 3.12).*

## 1. Automated unit/integration tests — `pytest tests/ -q`
```
...........................                                              [100%]
27 passed in 9.88s
```
| Suite | Coverage | Result |
|---|---|---|
| tests/test_models.py (9) | MVO weights non-negative/capped/sum-to-1, frontier positivity, BL posterior between prior and view, relative-view row construction | 9 passed |
| tests/test_data.py (5) | quality-check flags constant columns, retry-then-raise on network failure, FRED returns None (never fake data) when offline | 5 passed |
| tests/test_security.py (6) | no hardcoded secrets, .env.example placeholder only, XSRF on, no eval/pickle | 6 passed |
| tests/test_simulation.py (3) | Kelly weights equal Σ⁻¹(μ−rf) exactly, half-Kelly = ½ full, 10-sim run + summarize | 3 passed |
| tests/test_app_smoke.py (7) | every Streamlit page (app.py + 6 pages) executed headless via AppTest **with live data**; no exceptions | 7 passed |

Defects found by the smoke tests and fixed during testing (all re-tested):
1. `pages/02` format-spec typo (`"{:.2%"` → `"{:.2%}"`) — crashed table render.
2. `bootstrap_forecast` / `portfolio_return_series` rejected dict weights — fixed, robust to dict/Series.
3. `monte_carlo_fan` looked up string keys on integer percentiles — fixed.
4. `regime_up_probability` scalar-conversion TypeError on predict_proba — fixed.
5. Deprecated `use_container_width` migrated to `width="stretch"`.

## 2. Live data integration — real network calls
| Check | Result |
|---|---|
| `yfinance` download, 7 tickers, Jan 2023–Jun 2025, auto-adjust | ✔ 623 price rows (2023-01-03 → 2025-06-27), 622 return rows |
| `yfinance` current data | ✔ (latest row 2026-11-18 at test time) |
| FRED DGS10 CSV endpoint (no key) | ✔ HTTP 200, 269,455 bytes |
| Offline behavior (mocked) | ✔ returns None / raises — app shows an error, never fabricated numbers |

## 3. Server smoke test — `streamlit run app.py --server.headless`
```
curl http://localhost:8599/  -> HTTP 200, 7,863 bytes
curl http://localhost:8599/healthz -> 200 OK
No tracebacks/errors in server log.
```

## 4. Security scans — see SECURITY_AUDIT.md
- `bandit -r src pages config app.py`: 931 LOC, **0 medium/high**, 1 low (B110 try/except/pass, intentional graceful degradation).
- `pip-audit -r requirements.txt`: **"No known vulnerabilities found"** (after upgrading pytest 9.0.2 → 9.0.3; the initial scan flagged PYSEC-2026-1845 in pytest 9.0.2 and the pin was fixed).

## 5. Known limitations
- All model outputs are in-sample estimates on the GWP2 window unless a page says otherwise; the MVO-vs-1/N page numbers shown in the app come from re-running the study on whatever data window is configured (defaults to the original 2022–2024 design).
- Streamlit Cloud egress to Yahoo/FRED can be rate-limited; the app degrades with clear errors.
- `st.cache_data` TTL is 1 hour; the timestamp shown is the last *successful* fetch.
- No authentication: the app is read-only public research; no admin functions exist.
