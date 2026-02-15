# Listen — Real-Time Multilingual Transcription Overlay

## What This Is
A persistent macOS overlay that captures microphone audio, detects speech via Silero VAD, translates any language to English via faster-whisper, and displays floating subtitles. Also logs timestamped transcripts to daily files.

## Architecture
```
Mic → [Audio Thread: sounddevice] → audio_queue
  → [VAD Thread: silero-vad] → transcript_queue
  → [Whisper Thread: faster-whisper] → display_queue
  → [Main Thread: tkinter overlay + transcript_logger]
```

All worker threads are daemon threads. tkinter runs on the main thread (macOS requirement). Three `queue.Queue`s connect the stages.

## File Map
| File | Role |
|------|------|
| `config.py` | All constants — audio (16kHz, 512-sample/32ms blocks), VAD thresholds, Whisper model settings, overlay dimensions/styling, transcript dir |
| `audio_capture.py` | `sounddevice.InputStream` callback → `audio_queue`. Simple start/stop. |
| `vad.py` | Silero VAD state machine. States: SILENCE ↔ SPEECH. 300ms pre-buffer, 250ms min speech, 700ms silence triggers emit. Resets VAD state between segments. |
| `transcriber.py` | Lazy-loads faster-whisper `small` model (`int8`). Runs `task="translate"` with `language=None` (auto-detect). Filters hallucinations (short segments, empty/dot-only text). Emits `{text, timestamp, language}` dicts. |
| `overlay.py` | Borderless always-on-top semi-transparent tkinter window. Bottom-right, above Dock. Polls display_queue every 100ms via `root.after()`. Shows last 3 lines, auto-hides after 8s. Fires `on_subtitle` callback for logging. |
| `transcript_logger.py` | Writes `[HH:MM:SS] (lang_code) text` to `transcripts/YYYY-MM-DD.txt`. Auto-rotates at midnight. Creates `YYYY-MM-DD_todos.md` template. Flushes after every write. |
| `main.py` | Wires queues + threads + signal handlers. Ctrl+C for graceful shutdown. |

## Key Technical Decisions
- **Block size is 512 samples (32ms)** — Silero VAD v6 requires `sr / chunk_size <= 31.25`, so minimum at 16kHz is 512 samples. The plan said 30ms/480 but that crashes.
- **Whisper `small` model with `int8`** — ~1.5GB RAM. If the Mac Mini is tight on memory, change `WHISPER_MODEL` to `"tiny"` or `"base"` in `config.py`.
- **First run downloads ~500MB** model from HuggingFace automatically.
- **macOS will prompt for microphone permission** on first launch.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Dependencies
- `faster-whisper` — CTranslate2-based Whisper (brings ctranslate2, tokenizers, huggingface-hub)
- `sounddevice` — PortAudio wrapper for mic capture
- `silero-vad` — ONNX/Torch VAD model
- `numpy` — audio array handling
- `tkinter` — comes with Python, used for overlay

## Verification Checklist
1. `python main.py` → speak English → overlay shows text
2. Speak Hindi/Telugu/Spanish → overlay shows English translation
3. Stop speaking → overlay auto-hides after 8s
4. Check `transcripts/YYYY-MM-DD.txt` for timestamped entries
5. Ctrl+C → clean shutdown, no data loss

## Common Issues
- **"Input audio chunk is too short"** — block size < 512 at 16kHz. Already fixed in config.
- **No overlay on macOS** — tkinter must run on main thread. Already handled in main.py.
- **High RAM** — switch to `tiny` model in config.py (~400MB instead of 1.5GB).
