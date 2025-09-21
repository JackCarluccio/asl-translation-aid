from .schema import (
    SCHEMA_VERSION, CLASSES, UNKNOWN_CLASS,
    TEMPORAL_WINDOW, MIN_VOTES, MIN_CONFIDENCE, COOLDOWN_MS,
    Status, MLFrame, LetterEvent, StateSnapshot
)

class Detector:
    def __init__(self):
        # keeps the last TEMPORAL_WINDOW top-1 class names (e.g., "A", "B", ...)
        self.window = []
        # accepted characters we’ve locked in
        self.buffer_chars = []
        # current status for the UI
        self.status = Status.NO_HAND
        # when we last accepted a letter (ms). big negative = “long ago”
        self.last_accept_ts = -10**9

    def _push_window(self, cls_name):
        """Append a class name and keep only the last TEMPORAL_WINDOW items."""
        self.window.append(cls_name)
        if len(self.window) > TEMPORAL_WINDOW:
            # remove oldest
            self.window.pop(0)

    def update(self, frame: MLFrame):
        """
        Process one frame from the model.
        If a letter becomes stable, return a LetterEvent; otherwise return None.
        """
        # 1) Hand present?
        if not frame.hand_present:
            self.status = Status.NO_HAND
            self.window = []
            return None

        # 2) Top-1 prediction with enough confidence?
        top = frame.predictions[0] if frame.predictions else None
        if top is None or top.prob < MIN_CONFIDENCE:
            self.status = Status.LOW_CONFIDENCE
            return None

        # 3) Cooldown: avoid accepting letters too fast
        if frame.timestamp_ms - self.last_accept_ts < COOLDOWN_MS:
            self.status = Status.TRACKING
            self._push_window(top.cls)
            return None

        # 4) Voting: collect recent top-1s and see if one dominates
        self.status = Status.TRACKING
        self._push_window(top.cls)

        # Not enough samples yet to decide
        if len(self.window) < MIN_VOTES:
            return None

        # Find the class with most votes in the window
        # (basic approach using list.count)
        leader = None
        leader_votes = 0
        for c in set(self.window):
            votes = self.window.count(c)
            if votes > leader_votes:
                leader = c
                leader_votes = votes

        if leader_votes < MIN_VOTES:
            return None

        # 5) Accept the leader and update buffer
        accepted = leader
        if accepted == "SPACE":
            self.buffer_chars.append(" ")
        elif accepted == "BACKSPACE":
            if self.buffer_chars:
                self.buffer_chars.pop()
        elif accepted != UNKNOWN_CLASS and accepted in CLASSES:
            self.buffer_chars.append(accepted)
        # UNKNOWN is ignored

        # reset votes and start cooldown
        self.window = []
        self.last_accept_ts = frame.timestamp_ms

        return LetterEvent(
            schema_version=SCHEMA_VERSION,
            accepted_letter=(None if accepted == UNKNOWN_CLASS else accepted),
            buffer="".join(self.buffer_chars),
            status=self.status,
        )

    def snapshot(self):
        """Give the frontend the current buffer and status at any time."""
        return StateSnapshot(
            schema_version=SCHEMA_VERSION,
            buffer="".join(self.buffer_chars),
            status=self.status,
        )
