import os
from datetime import date, datetime

from config import TRANSCRIPT_DIR


class TranscriptLogger:
    """Appends timestamped subtitle entries to daily transcript files."""

    def __init__(self):
        os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
        self._current_date: date | None = None
        self._file = None
        self._ensure_file()

    def _ensure_file(self):
        today = date.today()
        if self._current_date == today and self._file is not None:
            return

        if self._file is not None:
            self._file.close()

        self._current_date = today
        date_str = today.isoformat()

        transcript_path = os.path.join(TRANSCRIPT_DIR, f"{date_str}.txt")
        is_new = not os.path.exists(transcript_path)
        self._file = open(transcript_path, "a", encoding="utf-8")
        if is_new:
            self._file.write(f"# Transcript for {date_str}\n\n")
            self._file.flush()

        todo_path = os.path.join(TRANSCRIPT_DIR, f"{date_str}_todos.md")
        if not os.path.exists(todo_path):
            with open(todo_path, "w", encoding="utf-8") as f:
                f.write(f"# TODOs from {date_str}\n\n## Tasks\n- [ ] \n\n## Notes\n- \n")

    def log(self, entry: dict):
        """Write a subtitle entry. Called from overlay's on_subtitle callback."""
        self._ensure_file()
        ts: datetime = entry["timestamp"]
        lang = entry.get("language", "??")
        text = entry["text"]
        self._file.write(f"[{ts.strftime('%H:%M:%S')}] ({lang}) {text}\n")
        self._file.flush()

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None
