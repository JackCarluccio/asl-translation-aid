import flask
from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

from .tts_api import bp as tts_bp

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
app.register_blueprint(tts_bp)

# Main route to serve the HTML page
@app.route('/')
def main():
    return flask.render_template('index.html')

# API endpoint to translate text
@app.route('/api/translate', methods=['POST'])
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

    return flask.jsonify({"translatedText": translated})
