import cv2, numpy as np
from flask import Blueprint, request, abort, jsonify
import src.model.main as asl_model

bp = Blueprint("frames", __name__, url_prefix="/api/frames")

# Ingest a single frame (JPEG/WEBP) and return the current running text
@bp.route("/frame", methods=["POST"])
def ingest():
    f = request.files.get("frame")
    if not f:
        abort(400, "missing frame")

    # decode JPEG/WEBP → np.ndarray (BGR)
    data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        abort(400, "could not decode image")
    
    running_text = asl_model.process_frame(img)
    return jsonify({"runningText": running_text})

# Clear all accumulated state (frames, sentence, etc)
@bp.route("/clear", methods=["POST"])
def clear():
    asl_model.clear_all()
    return ("", 204)

# Set the current running text (for manual correction)
@bp.route("/set_text", methods=["POST"])
def set_text():
    data = request.get_json()
    text = data.get("text", "")
    asl_model.set_text(text)
    return ("", 204)