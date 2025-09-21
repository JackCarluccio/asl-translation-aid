# ASL Translation Aid (SteelHacks 12)

> Google‑Translate‑style app that adds **ASL video interpretation** on top of text/speech translation.

## Overview
A hackathon MVP that can:
- Translate text between languages
- Convert speech ⇄ text (STT/TTS)
- **Interpret ASL from a live webcam stream** and output text/speech

## Tech Stack
- **Backend:** Python, Flask  
- **Frontend:** HTML/CSS/JS (Flask templates)  
- **APIs:** Google (requires `GOOGLE_API_KEY`)  
- **ASL:** Browser video → hand/pose landmarks → classification (details to be documented post‑hackathon)

## Requirements
- Python 3.11+ (tested with 3.12)
- Google API key
- Windows/macOS/Linux

## Setup
```bash
# 1) Clone
git clone git@github.com:JackCarluccio/asl-translation-aid.git
cd asl-translation-aid

# 2) Env vars (create .env in repo root)
echo GOOGLE_API_KEY=your_api_key_here > .env

# 3) Virtual env
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate
# macOS/Linux
# source .venv/bin/activate

# 4) Dependencies
pip install -r requirements.txt

# 5) Run
flask --app=src/web/app run
```

### Access over LAN (optional)
```bash
flask --app=src/web/app run --host=0.0.0.0
```
Then visit `http://<your-ip>:5000` from another device on the same network.

## Environment Variables
- `GOOGLE_API_KEY` — required

## Troubleshooting
- **`py`/`python` not found:** Ensure Python is on PATH; try `python` instead of `py` on Windows.
- **Cannot reach from another device:** Bind to `0.0.0.0` and allow port 5000 through your firewall.
- **Static/templating issues:** Run from repo root; confirm `templates/` and `static/` exist and CSS is linked via `/static/...`.

## Attribution
- Icons: [flaticon.com](https://www.flaticon.com/)
