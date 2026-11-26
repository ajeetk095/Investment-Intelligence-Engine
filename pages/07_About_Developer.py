"""Page 7: About the developer and contact form (sends real email via SMTP)."""
import sys, os, re, smtplib
from pathlib import Path
from urllib.parse import urlencode
from email.message import EmailMessage
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

from src.ui import apply_colorful_theme, render_disclaimer_footer

RECIPIENT = "ajeetk095@gmail.com"

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
c3.link_button("✉️ Hire me", f"mailto:{RECIPIENT}?subject=Quant%20role%20inquiry", use_container_width=True)

st.divider()


# ---------- SMTP settings lookup (works with [smtp] section, flat secrets, or env vars) ----------
ALIASES = {
    "host": ["SMTP_HOST", "EMAIL_HOST", "MAIL_HOST"],
    "port": ["SMTP_PORT", "EMAIL_PORT", "MAIL_PORT"],
    "user": ["SMTP_USER", "SMTP_USERNAME", "EMAIL_USER", "EMAIL_ADDRESS", "GMAIL_USER", "MAIL_USER", "EMAIL"],
    "password": ["SMTP_PASSWORD", "SMTP_PASS", "EMAIL_PASSWORD", "EMAIL_PASS", "GMAIL_APP_PASSWORD", "APP_PASSWORD", "MAIL_PASSWORD"],
}


def _secret(key):
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def smtp_setting(key, default=None):
    try:
        section = dict(st.secrets["smtp"])
    except Exception:
        section = {}
    candidates = [section.get(key), _secret(key)]
    for name in ALIASES[key]:
        candidates += [_secret(name), os.environ.get(name)]
    for value in candidates:
        if value not in (None, ""):
            return value
    return default


def send_email(name, visitor_email, subject, message):
    host = str(smtp_setting("host", "smtp.gmail.com")).strip()
    port = int(smtp_setting("port", 465))
    user, pwd = smtp_setting("user"), smtp_setting("password")
    if not user or not pwd:
        raise KeyError("smtp user/password")
    user, pwd = str(user).strip(), str(pwd).replace(" ", "").strip()  # Gmail app passwords show with spaces

    m = EmailMessage()
    m["Subject"] = f"[Portfolio] {subject} – from {name}"
    m["From"] = user
    m["To"] = RECIPIENT
    m["Reply-To"] = visitor_email
    m.set_content(f"Name: {name}\nEmail: {visitor_email}\nSubject: {subject}\n\n{message}")

    if port == 465:  # implicit SSL
        with smtplib.SMTP_SSL(host, port, timeout=20) as srv:
            srv.login(user, pwd)
            srv.send_message(m)
    else:  # 587 -> STARTTLS
        with smtplib.SMTP(host, port, timeout=20) as srv:
            srv.starttls()
            srv.login(user, pwd)
            srv.send_message(m)


# ---------- Contact form ----------
st.header("Send me a message")
with st.form("developer_contact_form", clear_on_submit=False):
    name = st.text_input("Your name", placeholder="Jane Doe")
    visitor_email = st.text_input("Your email", placeholder="you@example.com")
    subject = st.text_input("Subject")
    message = st.text_area("Message", height=160)
    send = st.form_submit_button("Send mail", type="primary")

if send:
    name, visitor_email, subject, message = name.strip(), visitor_email.strip(), subject.strip(), message.strip()
    errors = []
    if len(name) < 2:
        errors.append("Please enter your name.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", visitor_email):
        errors.append("Please enter a valid email address.")
    if len(subject) < 3:
        errors.append("Please enter a subject.")
    if len(message) < 10:
        errors.append("Message must be at least 10 characters.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        sent = False
        try:
            send_email(name, visitor_email, subject, message)
            st.success("Message sent – thank you! I'll get back to you soon.")
            sent = True
        except KeyError:
            try:
                visible = list(st.secrets.keys())
            except Exception:
                visible = []
            st.warning(f"Email credentials were not found. Secret keys the app can see: {visible}")
        except smtplib.SMTPAuthenticationError:
            st.warning("SMTP login failed. Use a Gmail App Password (not your normal password); 2-Step Verification must be on.")
        except Exception as exc:
            st.warning(f"SMTP error: {type(exc).__name__}: {exc}")

        if not sent:
            body = f"From: {name} <{visitor_email}>\n\n{message}"
            st.info("Direct sending didn't work, so you can send it from your mail app instead.")
            st.link_button("📨 Open in mail app", f"mailto:{RECIPIENT}?{urlencode({'subject': subject, 'body': body})}")

render_disclaimer_footer()
