import queue
import signal
import sys
import threading

from audio_capture import AudioCapture
from overlay import Overlay
from transcript_logger import TranscriptLogger
from transcriber import TranscriberWorker
from vad import VADWorker


def main():
    audio_queue = queue.Queue()
    transcript_queue = queue.Queue()
    display_queue = queue.Queue()

    logger = TranscriptLogger()
    capture = AudioCapture(audio_queue)
    vad = VADWorker(audio_queue, transcript_queue)
    transcriber = TranscriberWorker(transcript_queue, display_queue)
    overlay = Overlay(display_queue, on_subtitle=logger.log)

    vad_thread = threading.Thread(target=vad.run, daemon=True, name="vad")
    transcriber_thread = threading.Thread(target=transcriber.run, daemon=True, name="transcriber")

    def shutdown(*_):
        print("\n[main] Shutting down...")
        capture.stop()
        vad.stop()
        transcriber.stop()
        logger.close()
        overlay.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("[main] Starting Listen — speak in any language to see English subtitles.")
    print("[main] Press Ctrl+C to stop.\n")

    capture.start()
    vad_thread.start()
    transcriber_thread.start()

    # tkinter must run on the main thread (macOS requirement)
    try:
        overlay.run()
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
