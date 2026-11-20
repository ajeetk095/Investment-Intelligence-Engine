"""GWP2 Investment Intelligence - Streamlit app entry point.
Run: streamlit run app.py"""
import sys, os
from urllib.parse import urlencode
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config.settings import APP_TITLE, APP_SUBTITLE, DATA_NOTICE

st.set_page_config(page_title=APP_TITLE, page_icon="chart_with_upwards_trend",
                   layout="wide", initial_sidebar_state="expanded")

st.sidebar.success("Navigate pages from the sidebar.")
st.title(APP_TITLE)
st.subheader("Bridging Code & Capital - quantitative portfolio research on real market data")

st.markdown("""
### What this application does
This platform turns an academic portfolio-optimization study (MScFE 652 Group Work Project 2,
WorldQuant University) into a working research tool. It runs **real optimization on live
market data** and explains every number it shows.

| Page | What you get |
|---|---|
| **Market Overview** | Live prices, returns, volatility, correlation heatmap |
| **Quantitative Analysis** | The three optimized MVO portfolios (Steps 1-3) + efficient frontier |
| **Predictive Analytics** | Bootstrap forecast + walk-forward ML regime probability (with honesty notes) |
| **Investor Insights** | Evidence-based signals for retail, institutional and corporate readers |
| **Risk Analysis** | VaR, CVaR, drawdowns, Monte Carlo scenarios |
| **Research Methodology** | The original GWP2 study, reproduced step by step |

### How to use this app (2-minute guide)
1. Open **Market Overview** and confirm the data timestamp at the top - all figures come from Yahoo Finance (delayed) and FRED.
2. Go to **Quantitative Analysis** to see the optimized portfolios and their weights.
3. Check **Risk Analysis** before acting on any expected return - look at VaR and drawdowns, not just returns.
4. Read **Research Methodology** for how each number is produced and what its limits are.
""")

st.info("⚠️ **Disclaimer:** Everything here is educational research output from statistical models. "
        "It is **not** investment advice, and model estimates are not guarantees. Data feeds are delayed "
        "and unofficial.")

st.caption(DATA_NOTICE)

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
st.caption("Enter your details, then use Send mail to open a pre-addressed email in your mail app. The website does not send or store your message.")
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
