import queue
import re
import threading
from datetime import datetime

import numpy as np

from config import (
    MIN_SEGMENT_DURATION,
    SAMPLE_RATE,
    WHISPER_BEAM_SIZE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_MODEL,
    WHISPER_TASK,
)

_HALLUCINATION_RE = re.compile(r"^[\s.\-!?,]*$")


class TranscriberWorker:
    """Reads audio segments from transcript_queue, runs faster-whisper,
    pushes {text, timestamp, language} dicts to display_queue."""

    def __init__(self, transcript_queue: queue.Queue, display_queue: queue.Queue):
        self._transcript_q = transcript_queue
        self._display_q = display_queue
        self._model = None
        self._stop = threading.Event()

    def _load_model(self):
        from faster_whisper import WhisperModel

        print(f"[whisper] Loading {WHISPER_MODEL} model (this may download ~500MB on first run)...")
        self._model = WhisperModel(
            WHISPER_MODEL,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        print("[whisper] Model loaded.")

    def run(self):
        """Main loop — call from a daemon thread."""
        while not self._stop.is_set():
            try:
                audio = self._transcript_q.get(timeout=0.1)
            except queue.Empty:
                continue

            if self._model is None:
                self._load_model()

            segments, info = self._model.transcribe(
                audio,
                task=WHISPER_TASK,
                language=None,
                beam_size=WHISPER_BEAM_SIZE,
            )

            lang = info.language or "??"
            for seg in segments:
                duration = seg.end - seg.start
                text = seg.text.strip()
                if duration < MIN_SEGMENT_DURATION:
                    continue
                if not text or _HALLUCINATION_RE.match(text):
                    continue
                self._display_q.put({
                    "text": text,
                    "timestamp": datetime.now(),
                    "language": lang,
                })

    def stop(self):
        self._stop.set()
