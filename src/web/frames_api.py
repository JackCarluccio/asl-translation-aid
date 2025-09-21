import cv2, numpy as np
from flask import Blueprint, request, abort
from src.model.main import process_frame

bp = Blueprint("frames", __name__, url_prefix="/api/frames")

@bp.route("", methods=["POST"])
def ingest():
    f = request.files.get("frame")
    if not f:
        abort(400, "missing frame")

    # decode JPEG/WEBP → np.ndarray (BGR)
    data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        abort(400, "could not decode image")
    
    label = process_frame(img)
    print(label)

    return ("", 204)
