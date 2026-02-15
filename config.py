import os

# --- Audio ---
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"
BLOCK_DURATION_MS = 32  # minimum for Silero VAD at 16kHz (512 samples)
BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_DURATION_MS / 1000)  # 512 samples

# --- VAD ---
VAD_THRESHOLD = 0.5
MIN_SPEECH_DURATION_MS = 250
SILENCE_DURATION_MS = 700
PRE_SPEECH_BUFFER_MS = 300
# Number of blocks for each duration
MIN_SPEECH_BLOCKS = int(MIN_SPEECH_DURATION_MS / BLOCK_DURATION_MS)
SILENCE_BLOCKS = int(SILENCE_DURATION_MS / BLOCK_DURATION_MS)
PRE_SPEECH_BLOCKS = int(PRE_SPEECH_BUFFER_MS / BLOCK_DURATION_MS)

# --- Whisper ---
WHISPER_MODEL = "small"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_BEAM_SIZE = 3
WHISPER_TASK = "translate"
MIN_SEGMENT_DURATION = 0.5  # seconds, filter hallucinations

# --- Overlay ---
OVERLAY_WIDTH = 600
OVERLAY_HEIGHT = 80
OVERLAY_BG = "#1a1a1a"
OVERLAY_BG_ALPHA = 0.85
OVERLAY_FG = "#ffffff"
OVERLAY_FONT_SIZE = 16
OVERLAY_FONT_FAMILY = "Helvetica"
OVERLAY_MAX_LINES = 3
OVERLAY_HIDE_AFTER_S = 8
OVERLAY_POLL_MS = 100
OVERLAY_PADDING = 10  # pixels from screen edge

# --- Transcript ---
TRANSCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcripts")
