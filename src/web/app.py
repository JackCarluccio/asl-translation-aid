import os
from flask import Flask

from .home import bp as home_bp
from .tts_api import bp as tts_bp
from .translate_api import bp as translate_bp
from .frames_api import bp as frames_bp

app = Flask(__name__)
app.register_blueprint(home_bp)
app.register_blueprint(tts_bp)
app.register_blueprint(translate_bp)
app.register_blueprint(frames_bp)

# Start the OpenCV viewer only in the reloader child
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    # IMPORTANT: import here so both modules share the same process/module state
    from .display_debug import start_viewer_thread
    start_viewer_thread()