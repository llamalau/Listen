import queue
import numpy as np
import sounddevice as sd
from config import SAMPLE_RATE, CHANNELS, DTYPE, BLOCK_SIZE


class AudioCapture:
    def __init__(self, audio_queue: queue.Queue):
        self._queue = audio_queue
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[audio] {status}")
        self._queue.put(indata[:, 0].copy())

    def start(self):
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=BLOCK_SIZE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
