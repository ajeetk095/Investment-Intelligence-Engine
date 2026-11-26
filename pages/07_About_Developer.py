"""Page 7: About the developer and contact form."""
import sys, os
from pathlib import Path
from urllib.parse import urlencode
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

from src.ui import apply_colorful_theme, render_disclaimer_footer

apply_colorful_theme()
st.title("👤 About the Developer")

PHOTO_FILE = Path(__file__).resolve().parents[1] / "assets" / "profile.jpg"  # optional local photo
PHOTO_URL = "https://media.licdn.com/dms/image/v2/D5603AQHv97cmwfVvxQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1692917722661?e=1796860800&v=beta&t=4u57u5_Tz7UqbEcUwTdKrXoPRt0lo8ZolJ5vRKRollk"

i1, i2 = st.columns([1, 3])
with i1:
    if PHOTO_FILE.exists():
        st.image(str(PHOTO_FILE), width=160)
    else:
        st.markdown(
            f'<img src="{PHOTO_URL}" alt="Ajeet Kumar" width="140" height="140" '
            'style="width:140px;height:140px;object-fit:cover;border-radius:50%;display:block;margin:0 auto;" />',
            unsafe_allow_html=True,
        )
with i2:
    st.markdown("""
**Ajeet Kumar — Quantitative Finance & AI Professional**

*"Bridging code & capital."* Quantitative finance specialist with an M.Sc. in Financial Engineering
and a B.Tech in IT. Turns complex data into alpha using Python, C++, SQL and ML — from Markowitz MVO
and Black-Litterman to Monte Carlo and deep learning.

**Highlights:** 1st Place, IIT Kanpur ML Hackathon · Felicitated by the President of India ·
AI systems built at Algo8.ai and Amul. Seeking full-time Quant Research / Financial Engineering roles.
""")

c1, c2, c3 = st.columns(3)
c1.link_button("🔗 LinkedIn", "https://www.linkedin.com/in/ajeek095/", use_container_width=True)
c2.link_button("🐙 GitHub", "https://github.com/ajeetk095", use_container_width=True)
c3.link_button("✉️ Hire me", "mailto:ajeetk095@gmail.com?subject=Quant%20role%20inquiry", use_container_width=True)

st.divider()
st.header("Send me a message")
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

render_disclaimer_footer()
