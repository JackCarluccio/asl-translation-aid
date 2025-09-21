# ASL Translation Aid (SteelHacks 12)

A Google-Translate-style application that provides **American Sign Language (ASL) real-time video interpretation** in addition to text and speech translation between many langauges.

## Overview

ASL Translation Aid enables users to:
- Translate text between multiple languages
- Convert speech to text and text to speech (STT/TTS)
- **Interpret ASL from a live webcam stream** and output the results as text or speech

## Contributers 
- Jack Carluccio - jec432@pitt.edu
- Anthony Cardello - ajc434@pitt.edu
- Kolja Hribar - koh16@pitt.edu
- Gautam Udupa - gau14@pitt.edu

## Technology Stack

- **Backend:** Python, Flask  
- **Frontend:** HTML/CSS/JavaScript (Flask templates)  
- **APIs:** Google Cloud (requires `GOOGLE_API_KEY`)  
- **ASL Interpretation:**  
  - MediaPipe (hand/pose landmark detection)  
  - YOLO (Trained model on asl alphabet traing data + landmarks and image masks)

## Requirements

- Python 3.11+ (tested with 3.12)
- Google API key
- Windows, macOS, or Linux

## Setup

```bash
# 1) Clone the repository
git clone git@github.com:JackCarluccio/asl-translation-aid.git
cd asl-translation-aid

# 2) Set environment variables (create .env in repo root)
echo GOOGLE_API_KEY=your_api_key_here > .env

# 3) Set up a virtual environment
python -m venv .venv
# For Windows PowerShell
.\.venv\Scripts\Activate
# For macOS/Linux
# source .venv/bin/activate

# 4) Install dependencies
pip install -r requirements.txt

# 5) Start the application
flask --app=src/web/app run
```

### Access Over LAN (Optional)

```bash
flask --app=src/web/app run --host=0.0.0.0
```
Visit `http://<your-ip>:5000` from another device on your local network.

## Environment Variables

- `GOOGLE_API_KEY` — required for translation features

## Troubleshooting

- **`py`/`python` not found:** Ensure Python is in your PATH. On Windows, try `python` instead of `py`.
- **Cannot access from another device:** Bind to `0.0.0.0` and ensure port 5000 is open on your firewall.
- **Static/template issues:** Run commands from the repository root and confirm `templates/` and `static/` directories exist. CSS should be linked via `/static/...`.

## Attribution

- Icons: [flaticon.com](https://www.flaticon.com/)
