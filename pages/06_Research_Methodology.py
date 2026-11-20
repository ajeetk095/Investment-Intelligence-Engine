"""Page 6: the original GWP2 methodology and source documents."""
import base64
import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from config.settings import TICKERS, SIMULATION_START, SIMULATION_END
from src.ui import (render_disclaimer_footer, render_market_simulator,
                    setup_page_experience)

st.title("📚 Research Methodology (MScFE 652 GWP2)")
controls = setup_page_experience("methodology", TICKERS)
DOCS_DIR = Path(__file__).resolve().parents[1] / "assets" / "docs"
SOURCES = {
    "GWP2_SetE_assignment.pdf": ("📋 Project instructions (Set E, Sep 30 2025)", "Official assignment: scenario, Steps 0-8, constraints and grading rubric."),
    "Project_Report_2.pdf": ("📄 Project Report 2 (original submission)", "The group's full report: Steps 0-7, tables 1-14, references."),
    "GWP2_notebook.ipynb": ("📓 Original implementation notebook", "The code the report is based on (SLSQP MVO, MVO vs 1/N simulation, Black-Litterman, Kelly)."),
}
st.header("Source documents — original files, viewable here")
st.caption("The three original project files ship inside this repository (assets/docs/) so the research behind this app is fully auditable.")
for fname, (label, blurb) in SOURCES.items():
    fpath = DOCS_DIR / fname
    if not fpath.exists():
        st.warning(f"{fname} not found in the repository.")
        continue
    with st.expander(f"{label} — `{fname}` ({fpath.stat().st_size/1024:.0f} KB)"):
        st.markdown(blurb)
        if fname.endswith(".pdf"):
            b64 = base64.b64encode(fpath.read_bytes()).decode()
            components.html(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600" style="border:1px solid #333"></iframe>', height=620)
        else:
            nb = json.loads(fpath.read_text())
            n_md = sum(1 for c in nb["cells"] if c["cell_type"] == "markdown")
            n_code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
            st.caption(f"{len(nb['cells'])} cells ({n_md} markdown, {n_code} code). Showing narrative and code (outputs omitted).")
            for shown, cell in enumerate(nb["cells"][:60], start=1):
                src = "".join(cell["source"])
                if cell["cell_type"] == "markdown": st.markdown(src)
                elif cell["cell_type"] == "code": st.code(src, language="python")
            if len(nb["cells"]) > 60: st.caption("… remaining cells omitted here — download the notebook for the full file.")
        st.download_button(f"⬇️ Download {fname}", data=fpath.read_bytes(), file_name=fname,
                           mime="application/pdf" if fname.endswith(".pdf") else "application/x-ipynb+json", key=f"dl_{fname}")

st.divider()
st.header("Original study")
st.markdown(f"""
**Scenario:** Smart Money Inc. allocates client portfolios among seven assets ({', '.join(TICKERS)}), estimated on the original Jan 2023 – Jun 2025 daily data.

| Part | Task | Method actually used |
|---|---|---|
| 1 (Steps 0–4) | Descriptive stats; optimal weights: long-only, 20% cap, short allowed; comparison | SLSQP maximization of Sharpe |
| 2 (Step 5) | MVO vs 1/N | {SIMULATION_START[:4]}–{SIMULATION_END[:4]} 20-asset universe; 2y train / 1y test; 5,000 random 5-asset draws; SLSQP MVO; paired t-test, Wilcoxon, variance test |
| 3 (Steps 6–7) | Analyst views + Black-Litterman | 7 views (5 absolute, 2 relative), He-Litterman posterior, market-cap prior |
| 4 (Step 8) | Kelly criterion | General formula w* = f·Σ⁻¹(μ−rf), correlations included; full/half/double Kelly |
""")
st.header("Key results from the original report (in-sample, rf = 4%)")
st.markdown("""
| Strategy | Ann. Return | Ann. Vol | Sharpe |
|---|---|---|---|
| MVO long-only (Step 1) | 65.02% | 27.08% | 2.2528 |
| MVO 20% cap (Step 2) | 45.58% | 21.02% | 1.9782 |
| MVO short allowed (Step 3) | 111.94% | 43.45% | 2.4842 |
| MVO vs 1/N (out-of-sample means) | 33.78% vs 26.05% | 47.14% vs 14.81% | 0.72 vs 1.76 |
""")
st.header("What the app changes (and why)")
st.markdown("""
- Adjusted close prices include dividends/splits; live FRED risk-free rates are used when available.
- MVO vs 1/N uses Levene's test; Kelly strategies use bootstrap paths with periodic rebalancing.
- Corrected Step 2/3 weight tables and a reproduced Black-Litterman section are in `docs/CORRECTED_STEPS.md`.
- Added VaR, bootstrap and ML regime analysis answer questions beyond the original study.
""")
st.header("Reference for the Black-Litterman model")
st.markdown("Black, F., & Litterman, R. (1992). *Global Portfolio Optimization*. Financial Analysts Journal, 48(5), 28–43. Views are documented assumptions, not verified forecasts.")

render_market_simulator("methodology", TICKERS, controls)
render_disclaimer_footer()
