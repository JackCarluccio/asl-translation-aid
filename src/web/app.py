from flask import Flask

from .home import bp as home_bp
from .tts_api import bp as tts_bp
from .translate_api import bp as translate_bp

app = Flask(__name__)
app.register_blueprint(home_bp)
app.register_blueprint(tts_bp)
app.register_blueprint(translate_bp)
