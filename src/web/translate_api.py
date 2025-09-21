import os, requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

bp = Blueprint("translate", __name__, url_prefix="/api/translate")

@bp.route("", methods=["POST"])
def translate():
    data = request.get_json()
    text = data.get('text')
    source = data.get('source')
    target = data.get('target')

    url = f"https://translation.googleapis.com/language/translate/v2?key={GOOGLE_API_KEY}"
    response = requests.post(url, json={
        "q": [text],
        "source": source,
        "target": target,
        "format": "text"
    })

    result = response.json()
    translated = result['data']['translations'][0]['translatedText']

    return jsonify({"translatedText": translated})
