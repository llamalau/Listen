import queue
import tkinter as tk

from config import (
    OVERLAY_BG,
    OVERLAY_FG,
    OVERLAY_FONT_FAMILY,
    OVERLAY_FONT_SIZE,
    OVERLAY_POLL_MS,
)


class Overlay:
    """Scrollable transcript window using tkinter. Must run on the main thread."""

    def __init__(self, display_queue: queue.Queue, on_subtitle=None):
        self._display_q = display_queue
        self._on_subtitle = on_subtitle

        self._root = tk.Tk()
        self._root.title("Listen")
        self._root.geometry("500x350")
        self._root.configure(bg=OVERLAY_BG)
        self._root.minsize(300, 150)

        self._text = tk.Text(
            self._root,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE),
            fg=OVERLAY_FG,
            bg=OVERLAY_BG,
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=10,
            pady=10,
            insertbackground=OVERLAY_FG,
        )
        scrollbar = tk.Scrollbar(self._root, command=self._text.yview)
        self._text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._text.pack(fill="both", expand=True)

        self._root.after(OVERLAY_POLL_MS, self._poll)

    def _poll(self):
        while True:
            try:
                entry = self._display_q.get_nowait()
            except queue.Empty:
                break

            ts = entry["timestamp"].strftime("%H:%M:%S")
            lang = entry.get("language", "??")
            line = f"[{ts}] ({lang}) {entry['text']}\n"

            self._text.configure(state="normal")
            self._text.insert("end", line)
            self._text.configure(state="disabled")
            self._text.see("end")

            if self._on_subtitle:
                self._on_subtitle(entry)

        self._root.after(OVERLAY_POLL_MS, self._poll)

    def run(self):
        self._root.mainloop()

    def stop(self):
        self._root.quit()
