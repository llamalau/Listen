import collections
import queue
import threading

import numpy as np
import torch
from silero_vad import load_silero_vad

from config import (
    BLOCK_SIZE,
    MIN_SPEECH_BLOCKS,
    PRE_SPEECH_BLOCKS,
    SAMPLE_RATE,
    SILENCE_BLOCKS,
    VAD_THRESHOLD,
)


class VADWorker:
    """Reads audio blocks from audio_queue, detects speech segments, pushes
    complete utterances (as numpy arrays) to transcript_queue."""

    def __init__(self, audio_queue: queue.Queue, transcript_queue: queue.Queue):
        self._audio_q = audio_queue
        self._transcript_q = transcript_queue
        self._model = load_silero_vad()
        self._stop = threading.Event()

    def run(self):
        """Main loop — call from a daemon thread."""
        ring = collections.deque(maxlen=PRE_SPEECH_BLOCKS)
        speech_blocks: list[np.ndarray] = []
        speech_count = 0
        silence_count = 0
        in_speech = False

        while not self._stop.is_set():
            try:
                block = self._audio_q.get(timeout=0.1)
            except queue.Empty:
                continue

            tensor = torch.from_numpy(block)
            prob = self._model(tensor, SAMPLE_RATE).item()

            if not in_speech:
                ring.append(block)
                if prob >= VAD_THRESHOLD:
                    speech_count += 1
                    if speech_count >= MIN_SPEECH_BLOCKS:
                        in_speech = True
                        speech_blocks = list(ring)
                        silence_count = 0
                else:
                    speech_count = 0
            else:
                speech_blocks.append(block)
                if prob < VAD_THRESHOLD:
                    silence_count += 1
                    if silence_count >= SILENCE_BLOCKS:
                        self._emit(speech_blocks)
                        speech_blocks = []
                        speech_count = 0
                        silence_count = 0
                        in_speech = False
                        self._model.reset_states()
                else:
                    silence_count = 0

    def _emit(self, blocks: list[np.ndarray]):
        audio = np.concatenate(blocks)
        if len(audio) > 0:
            self._transcript_q.put(audio)

    def stop(self):
        self._stop.set()
