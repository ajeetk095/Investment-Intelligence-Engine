# Deployment Manual — GitHub + Streamlit Community Cloud (beginner-friendly, ~15 minutes)
> **Status:** not deployed yet — you must do these steps yourself (they need your GitHub/Streamlit accounts).
> Verified against current Streamlit docs (2026): public repo required for Community Cloud free tier; deploy = Create app → repo → branch → main file → Python version → Deploy; secrets via the app's Settings → Secrets UI (never committed). Sources: docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app (+ /deploy, /secrets-management).

## Part A — Put the project on GitHub
1. Create repo: github.com → **+** → **New repository** → name `GWP2-Investment-Intelligence` → **Public** → Create (do NOT add a README).
2. Upload (browser way): "uploading an existing file" → drag the CONTENTS of this folder (app.py, requirements.txt, pages/, src/, config/, tests/, docs/, .streamlit/, assets/, README.md, LICENSE, .gitignore, .env.example). Hidden folders: Windows Explorer → enable "Hidden items"; macOS Finder → Cmd+Shift+. → commit "Initial app".
3. Upload (git command way):
```bash
cd GWP2-Investment-Intelligence
git init
git add .
git commit -m "Initial GWP2 Investment Intelligence app"
git branch -M main
git remote add origin https://github.com/<your-username>/GWP2-Investment-Intelligence.git
git push -u origin main
```
   When prompted for a password, use a **Personal Access Token (PAT)**, not your GitHub password: GitHub → Settings → Developer settings → Personal access tokens → Generate (classic, `repo` scope) → paste it as the password. (Password authentication over git was removed by GitHub in 2021.)

## Part B — Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io → **Sign in with GitHub** (authorize access).
2. Top-right **Create app** → "Paste repo URL" → enter `https://github.com/<your-username>/GWP2-Investment-Intelligence` (or pick the repo from the dropdown).
3. Fill the form:
   - **Repository:** your repo
   - **Branch:** `main`
   - **Main file path:** `app.py` (must be at repo root — a wrong path is the #1 deploy error)
   - **App URL:** pick a subdomain, e.g. `gwp2-investment-intelligence`
4. Click **Advanced settings** → **Python version: 3.12** (matches the verified pins in requirements.txt).
5. Click **Deploy**. First boot: 3–8 minutes (dependencies install from requirements.txt). The app then opens at `https://<subdomain>.streamlit.app`.

## Part C — Secrets (optional)
The app runs with NO keys (FRED public CSV endpoint fallback). For higher FRED limits: free key at fred.stlouisfed.org/docs/api/api_key.html → in Streamlit Cloud: app → **Settings → Secrets** → add one line `FRED_API_KEY = "your_key"` → Save. Never commit keys; `.gitignore` already excludes `.env` / `secrets.toml`.

## Part D — Update the live app
Edit any file on GitHub (web editor OK) or `git push` → Streamlit auto-redeploys on every commit to `main`.

## Troubleshooting
| Symptom | Fix |
|---|---|
| ModuleNotFoundError | dependency missing → add exact pin to requirements.txt and push |
| app.py not found | Main file path must be `app.py` at repo root |
| Wrong Python version | Advanced settings → 3.12, or add `runtime.txt` with `python-3.12` |
| App sleeps / slow first load | free tier sleeps after ~7 days inactivity; first visitor reboots it |
| Yahoo data errors in-app | cloud-IP rate limits; wait/retry — app never shows fabricated data |
| FRED missing | fine — app falls back to the 4% default and says so on the Risk page |
