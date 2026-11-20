"""GWP2 Investment Intelligence - Streamlit app entry point."""
import sys, os
from urllib.parse import urlencode
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config.settings import APP_TITLE, TICKERS
from src.ui import render_disclaimer_footer, render_market_simulator, setup_page_experience

st.set_page_config(page_title=APP_TITLE, page_icon="chart_with_upwards_trend", layout="wide", initial_sidebar_state="expanded")
controls = setup_page_experience("home", TICKERS)
st.sidebar.success("Navigate pages from the sidebar.")
st.title(APP_TITLE)
st.subheader("Bridging Code & Capital · quantitative portfolio research made easier to explore")

st.markdown("""
### Your portfolio research, in plain language
Explore current available market data, compare portfolio strategies, and see how risk changes under different assumptions.

| Explore | What you can learn |
|---|---|
| **Market Overview** | Prices, returns, volatility and how assets move together |
| **Quantitative Analysis** | How portfolio weights change under constraints |
| **Predictive Analytics** | How historical resampling illustrates a range of outcomes |
| **Investor Insights** | What model signals mean in everyday language |
| **Risk Analysis** | Historical loss measures and drawdowns |
| **Research Methodology** | How the original GWP2 study was conducted |

### A simple way to explore
1. Start with **Market Overview** for the selected period.
2. Compare returns with volatility; higher estimated returns can come with larger swings.
3. Try the optional **Market sandbox** to explore a hypothetical shock and horizon.
4. Use **Refresh** to reload cached prices or **Reset** to return to the default live-data view.
""")

st.markdown("### About the developer")
i1, i2 = st.columns([1, 3])
with i1:
    st.markdown('''<img src="https://media.licdn.com/dms/image/v2/D5603AQHv97cmwfVvxQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1692917722661?e=1796860800&v=beta&t=4u57u5_Tz7UqbEcUwTdKrXoPRt0lo8ZolJ5vRKRollk" alt="Ajeet Kumar" width="140" height="140" style="width:140px;height:140px;object-fit:cover;border-radius:50%;display:block;margin:0 auto;" />''', unsafe_allow_html=True)
with i2:
    st.markdown("""
**Ajeet Kumar — Quantitative Finance & AI Professional**

*"Bridging code & capital."* Quantitative finance specialist with an M.Sc. in Financial Engineering
and a B.Tech in IT. Turns complex data into alpha using Python, C++, SQL and ML — from Markowitz MVO
and Black-Litterman to Monte Carlo and deep learning.

**Highlights:** 1st Place, IIT Kanpur ML Hackathon · Felicitated by the President of India ·
AI systems built at Algo8.ai and Amul. Seeking full-time Quant Research / Financial Engineering roles.
""")
st.markdown("[🔗 Connect on LinkedIn](https://www.linkedin.com/in/ajeek095/) · [🐙 GitHub](https://github.com/ajeetk095) · [✉️ Hire me](mailto:ajeetk095@gmail.com?subject=Quant%20role%20inquiry)")

st.markdown("#### Send me a message")
with st.form("developer_contact_form"):
    visitor_email = st.text_input("Your email", placeholder="you@example.com")
    subject = st.text_input("Subject")
    message = st.text_area("Message")
    send = st.form_submit_button("Send mail")
if send:
    if not visitor_email.strip() or not subject.strip() or not message.strip():
        st.warning("Please provide your email, a subject, and a message.")
    else:
        body = f"From: {visitor_email.strip()}\n\n{message.strip()}"
        st.link_button("Open email app", f"mailto:ajeetk095@gmail.com?{urlencode({'subject': subject.strip(), 'body': body})}")

render_market_simulator("home", TICKERS, controls)
render_disclaimer_footer()
