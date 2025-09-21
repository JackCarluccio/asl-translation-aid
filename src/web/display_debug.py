# display_debug.py
import threading, time, cv2
from . import frames_api as frames

def _viewer():
    cv2.namedWindow("server preview", cv2.WINDOW_NORMAL)
    while True:
        frame = frames.latest_frame  # a NumPy array (BGR) you set in the POST handler
        if frame is not None:
            cv2.imshow("server preview", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to close
            break
        time.sleep(0.01)
    cv2.destroyAllWindows()

def start_viewer_thread():
    t = threading.Thread(target=_viewer, daemon=True)
    t.start()
