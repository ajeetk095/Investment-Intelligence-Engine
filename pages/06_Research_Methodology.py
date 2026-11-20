"""Page 6: original GWP2 methodology and source documents."""
import base64
import json
import sys, os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import streamlit.components.v1 as components

from config.settings import TICKERS, SIMULATION_START, SIMULATION_END
from src.ui import render_disclaimer_footer, render_market_simulator, setup_page_experience

st.title("📚 Research Methodology")
controls = setup_page_experience("methodology", TICKERS)
DOCS_DIR = Path(__file__).resolve().parents[1] / "assets" / "docs"
SOURCES = {
    "GWP2_SetE_assignment.pdf": ("📋 Project instructions", "Official assignment, constraints and grading rubric."),
    "Project_Report_2.pdf": ("📄 Project Report 2", "The group's full report, tables and references."),
    "GWP2_notebook.ipynb": ("📓 Original notebook", "Original MVO, MVO vs 1/N, Black-Litterman and Kelly implementation."),
}
st.header("Source documents")
for fname, (label, blurb) in SOURCES.items():
    fpath = DOCS_DIR / fname
    if not fpath.exists():
        st.warning(f"{fname} not found.")
        continue
    with st.expander(f"{label} — {fname}"):
        st.markdown(blurb)
        if fname.endswith(".pdf"):
            b64 = base64.b64encode(fpath.read_bytes()).decode()
            components.html(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600"></iframe>', height=620)
        else:
            nb = json.loads(fpath.read_text())
            for cell in nb["cells"][:60]:
                src = "".join(cell["source"])
                if cell["cell_type"] == "markdown": st.markdown(src)
                elif cell["cell_type"] == "code": st.code(src, language="python")
        st.download_button(f"Download {fname}", fpath.read_bytes(), fname)

st.divider()
st.header("Original study")
st.markdown(f"""
**Scenario:** Smart Money Inc. allocates among seven assets ({', '.join(TICKERS)}), estimated on Jan 2023–Jun 2025 data.

| Part | Task | Method |
|---|---|---|
| 1 (Steps 0–4) | Descriptive stats and optimal weights | SLSQP Sharpe optimization |
| 2 (Step 5) | MVO vs 1/N | {SIMULATION_START[:4]}–{SIMULATION_END[:4]}, 5,000 random draws and paired tests |
| 3 (Steps 6–7) | Black-Litterman | Seven views and market-cap prior |
| 4 (Step 8) | Kelly criterion | Full, half and double Kelly |
""")
st.header("What this app adds")
st.markdown("- Adjusted close prices and live FRED risk-free rates when available.\n- VaR, bootstrap forecasts and ML regime analysis.\n- A clear market-data and model-estimation disclaimer at the footer.")

render_market_simulator("methodology", TICKERS, controls)
render_disclaimer_footer()
