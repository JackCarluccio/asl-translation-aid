import cv2, numpy as np
from flask import Blueprint, request, abort
from src.model.main import process_frame

bp = Blueprint("frames", __name__, url_prefix="/api/frames")

latest_frame = None  # global var, same role as `cap.read()`

@bp.route("", methods=["POST"])
def ingest():
    global latest_frame

    f = request.files.get("frame")
    if not f:
        abort(400, "missing frame")

    # decode JPEG/WEBP → np.ndarray (BGR)
    data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        abort(400, "could not decode image")
    
    process_frame(img)

    latest_frame = img  # this is equivalent to `image = cap.read()`
    return ("", 204)
