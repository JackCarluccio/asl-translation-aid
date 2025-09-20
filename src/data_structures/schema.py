from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

SCHEMA_VERSION = "0.1.0"

# ----- Classes / Tokens -----
CLASSES: List[str] = [
    "A","B","C","D","E","F","G","H","I","J","K","L","M",
    "N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
    "SPACE","BACKSPACE","UNKNOWN"
]
CLASS_TO_ID = {c: i for i, c in enumerate(CLASSES)}
ID_TO_CLASS = {i: c for c, i in CLASS_TO_ID.items()}
UNKNOWN_CLASS = "UNKNOWN"

# ----- Minimal decision defaults (used by detection.py) -----
TEMPORAL_WINDOW = 10     # how many recent frames to consider
MIN_VOTES = 7            # how many must agree to lock a letter
MIN_CONFIDENCE = 0.60    # floor for accepting a frame
COOLDOWN_MS = 500        # ignore repeats for this long after accept

# ----- Status for UI -----
class Status(str, Enum):
    TRACKING = "tracking"
    NO_HAND = "no_hand"
    LOW_CONFIDENCE = "low_confidence"

# ----- ML → You (per-frame) -----
@dataclass
class Prediction:
    cls: str      # must be one of CLASSES
    prob: float   # 0..1

@dataclass
class MLFrame:
    timestamp_ms: int  # ms since session start
    hand_present: bool
    predictions: List[Prediction]  # top-k sorted by prob desc

# ----- You → Frontend (event when a letter is accepted) -----
@dataclass
class LetterEvent:
    schema_version: str
    accepted_letter: Optional[str]   # None if nothing accepted this frame
    buffer: str
    status: Status

# ----- You → Frontend (state snapshot anytime) -----
@dataclass
class StateSnapshot:
    schema_version: str
    buffer: str
    status: Status