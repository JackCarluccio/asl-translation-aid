import os, base64, requests
from flask import Blueprint, request, send_file, abort
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

bp = Blueprint("tts", __name__, url_prefix="/api/tts")

@bp.route("", methods=["POST"])
def tts():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    lang = (data.get("lang") or "en-US").strip()

    if not text:
        abort(400, "Missing text")

    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": lang, "ssmlGender": "NEUTRAL"},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    r = requests.post(url, json=payload)
    if r.status_code != 200:
        abort(r.status_code, r.text)

    audio_content = r.json()["audioContent"]
    audio_bytes = BytesIO(base64.b64decode(audio_content))

    return send_file(audio_bytes, mimetype="audio/mpeg")
