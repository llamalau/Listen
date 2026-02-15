import queue
import time
import tkinter as tk

from config import (
    OVERLAY_BG,
    OVERLAY_BG_ALPHA,
    OVERLAY_FG,
    OVERLAY_FONT_FAMILY,
    OVERLAY_FONT_SIZE,
    OVERLAY_HEIGHT,
    OVERLAY_HIDE_AFTER_S,
    OVERLAY_MAX_LINES,
    OVERLAY_PADDING,
    OVERLAY_POLL_MS,
    OVERLAY_WIDTH,
)


class Overlay:
    """Floating subtitle overlay using tkinter. Must run on the main thread."""

    def __init__(self, display_queue: queue.Queue, on_subtitle=None):
        self._display_q = display_queue
        self._on_subtitle = on_subtitle  # callback(entry_dict)
        self._lines: list[str] = []
        self._last_update = 0.0
        self._visible = False

        self._root = tk.Tk()
        self._root.title("Listen")
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", OVERLAY_BG_ALPHA)
        self._root.configure(bg=OVERLAY_BG)

        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = screen_w - OVERLAY_WIDTH - OVERLAY_PADDING
        y = screen_h - OVERLAY_HEIGHT - OVERLAY_PADDING - 60  # above Dock
        self._root.geometry(f"{OVERLAY_WIDTH}x{OVERLAY_HEIGHT}+{x}+{y}")

        self._label = tk.Label(
            self._root,
            text="",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE),
            fg=OVERLAY_FG,
            bg=OVERLAY_BG,
            wraplength=OVERLAY_WIDTH - 20,
            justify="left",
            anchor="sw",
        )
        self._label.pack(fill="both", expand=True, padx=10, pady=5)

        self._hide()
        self._root.after(OVERLAY_POLL_MS, self._poll)

    def _poll(self):
        changed = False
        while True:
            try:
                entry = self._display_q.get_nowait()
            except queue.Empty:
                break
            self._lines.append(entry["text"])
            if len(self._lines) > OVERLAY_MAX_LINES:
                self._lines = self._lines[-OVERLAY_MAX_LINES:]
            self._last_update = time.time()
            changed = True
            if self._on_subtitle:
                self._on_subtitle(entry)

        if changed:
            self._label.config(text="\n".join(self._lines))
            self._show()
        elif self._visible and (time.time() - self._last_update > OVERLAY_HIDE_AFTER_S):
            self._lines.clear()
            self._hide()

        self._root.after(OVERLAY_POLL_MS, self._poll)

    def _show(self):
        if not self._visible:
            self._root.deiconify()
            self._visible = True

    def _hide(self):
        self._root.withdraw()
        self._visible = False

    def run(self):
        self._root.mainloop()

    def stop(self):
        self._root.quit()
