"""Investment-Intelligence-Engine - Streamlit app entry point."""
import sys, os
from urllib.parse import urlencode
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config.settings import APP_TITLE, TICKERS
from src.ui import (render_disclaimer_footer, render_market_simulator,
                    setup_page_experience)

st.set_page_config(page_title=APP_TITLE, page_icon="chart_with_upwards_trend",
                   layout="wide", initial_sidebar_state="expanded")
controls = setup_page_experience("home", TICKERS)
st.sidebar.success("Navigate pages from the sidebar.")
st.title(APP_TITLE)
st.subheader("Bridging Code & Capital · quantitative portfolio research made easier to explore")

st.markdown("""
### Your portfolio research, in plain language
Explore current available market data, compare portfolio strategies, and see how risk changes under different assumptions. Use the sidebar to switch between the latest available market history and the original GWP2 study window.

| Explore | What you can learn |
|---|---|
| **Market Overview** | Prices, returns, volatility and how assets move together |
| **Quantitative Analysis** | How portfolio weights change under different constraints |
| **Predictive Analytics** | How historical-return resampling illustrates a range of possible outcomes |
| **Investor Insights** | What model signals mean in everyday language |
| **Risk Analysis** | Historical loss measures and drawdowns |
| **Research Methodology** | How the original GWP2 study was conducted |

### A simple way to explore
1. Start with **Market Overview** for the selected period and latest available prices.
2. Compare returns with volatility; higher potential return estimates can come with larger swings.
3. Try the optional **Market sandbox** on any page to explore a hypothetical shock and horizon.
4. Use **Refresh** to clear cached prices or **Reset** to return to the default live-data view.

The market pulse and sandbox help explain data; neither can know future events or determine what is suitable for your personal situation.
""")

st.markdown("### About the developer")
image_column, profile_column = st.columns([1, 3])
with image_column:
    st.markdown(
        '''<img src="https://media.licdn.com/dms/image/v2/D5603AQHv97cmwfVvxQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1692917722661?e=1796860800&v=beta&t=4u57u5_Tz7UqbEcUwTdKrXoPRt0lo8ZolJ5vRKRollk"
             alt="Ajeet Kumar" width="140" height="140"
             style="width:140px;height:140px;object-fit:cover;border-radius:50%;display:block;margin:0 auto;" />''',
        unsafe_allow_html=True,
    )
with profile_column:
    st.markdown("""
**Ajeet Kumar — Quantitative Finance & AI Professional**

*"Bridging code & capital."* Quantitative finance specialist with an M.Sc. in Financial Engineering
and a B.Tech in IT. Turns complex data into alpha using Python, C++, SQL and ML — from Markowitz MVO
and Black-Litterman to Monte Carlo and deep learning.

**Highlights:** 1st Place, IIT Kanpur ML Hackathon · Felicitated by the President of India ·
AI systems built at Algo8.ai and Amul. Seeking full-time Quant Research / Financial Engineering roles.
""")
st.markdown("[🔗 Connect on LinkedIn](https://www.linkedin.com/in/ajeek095/)  ·  "
            "[🐙 GitHub](https://github.com/ajeetk095)  ·  "
            "[✉️ Hire me](mailto:ajeetk095@gmail.com?subject=Quant%20role%20inquiry)")

st.markdown("#### Send me a message")
st.caption("Your mail app opens with the message filled in; the website does not send or store it.")
with st.form("developer_contact_form"):
    visitor_email = st.text_input("Your email", placeholder="you@example.com")
    email_subject = st.text_input("Subject")
    email_message = st.text_area("Message")
    send_message = st.form_submit_button("Send mail")
if send_message:
    if not visitor_email.strip() or not email_subject.strip() or not email_message.strip():
        st.warning("Please provide your email, a subject, and a message.")
    else:
        email_body = f"From: {visitor_email.strip()}\n\n{email_message.strip()}"
        mailto_url = f"mailto:ajeetk095@gmail.com?{urlencode({'subject': email_subject.strip(), 'body': email_body})}"
        st.link_button("Open email app", mailto_url)

render_market_simulator("home", TICKERS, controls)
render_disclaimer_footer()
