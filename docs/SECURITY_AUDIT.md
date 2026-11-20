# Security Audit Report

*Scope: all Python in `app.py`, `pages/`, `src/`, `config/`, `tests/`, plus dependency and deployment configuration. Tooling: `bandit` (static), `pip-audit` (CVE database), custom secret-pattern tests. Executed 2026-11-20.*

## Findings and remediation
| # | Check | Finding | Severity | Action |
|---|---|---|---|---|
| 1 | Hardcoded secrets/keys | None in tree; `.env.example` contains a placeholder only; FRED key read from `st.secrets`/env via `config.settings.get_fred_api_key` | — | Verified by `tests/test_security.py::test_no_hardcoded_secrets` |
| 2 | Dependency vulnerabilities | pytest 9.0.2 → PYSEC-2026-1845 (pip-audit) | Medium | Pinned pytest==9.0.3; re-scan: **no known vulnerabilities** |
| 3 | Injection (SQL/shell) | No SQL, no `subprocess`/`os.system` with user input (bandit: 0 medium/high) | — | None needed |
| 4 | Code execution (`eval`/`pickle`) | Absent; regression test added | — | `test_no_eval_or_pickle` |
| 5 | File upload / deserialization | App has no upload surface; Streamlit `maxUploadSize` capped at 50 MB anyway | — | Config set |
| 6 | XSS / unsafe HTML | No `st.markdown(..., unsafe_allow_html=True)`; all content via Streamlit primitives | — | None needed |
| 7 | Transport security | All external calls over HTTPS (yfinance library default; FRED endpoint https) | — | None needed |
| 8 | Input validation | Numeric widgets bounded (risk-free 0–15%, confidence 90–99%, horizon 21–504d); tickers from a fixed allow-list, never free text | — | Implemented on every page |
| 9 | Information leakage | Errors show generic messages + retry guidance; no stack traces or secrets surfaced to users | — | try/except in data layer |
| 10 | DoS / resource exhaustion | Data fetches cached (`ttl=3600`); simulations bounded (5,000 default, slider-capped in lab); ML model small (200 trees) | — | Implemented |
| 11 | Bandit B110 (try/except/pass) | In `get_fred_series`/`get_fred_api_key` — intentional fallback to the public CSV endpoint / default rf | Low | Accepted, documented |
| 12 | Streamlit hardening | `enableXsrfProtection = true` in `.streamlit/config.toml` | — | Verified by test |
| 13 | Git hygiene | `.gitignore` excludes `.env`, `__pycache__`, generated CSV/PNG artifacts | — | Verified by test |

## Residual risks (honest statement)
- The app is **public and unauthenticated by design** — anyone can read the research outputs; there is nothing to write to.
- Yahoo/FRED responses are trusted as data (standard for market apps); a poisoned upstream feed would flow into the models. Mitigation: data-quality gate flags staleness/missing/constant columns.
- Static analysis cannot prove absence of all vulnerabilities. Bandit + pip-audit + targeted tests cover the realistic classes for an app with no auth, no DB, and no uploads.
- This audit covers the code as of the date above; re-run both scanners after any dependency change (`pip-audit -r requirements.txt`, `bandit -r src pages config app.py`).

## Final assessment
**Reasonably secure for a public, read-only research app.** No secrets in the repository, no injection or code-execution surface, dependencies currently CVE-free, graceful degradation on data-source failure.
