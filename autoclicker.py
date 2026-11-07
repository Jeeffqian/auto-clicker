"""
Auto Clicker — up to 300 CPS, LMB or RMB.

Controls:
  - Choose button: Left (LMB) or Right (RMB)
  - CPS slider: 1 - 300 clicks per second
  - Press F6 (or the Start/Stop button) to toggle clicking
  - Clicking happens at the current mouse cursor position

macOS note: the first time you run this, macOS will ask for
Accessibility permission (System Settings > Privacy & Security >
Accessibility) for your terminal/Python. Grant it or the clicks
won't register.
"""

import threading
import time
import tkinter as tk
from tkinter import ttk

from pynput import keyboard, mouse

MAX_CPS = 300
TOGGLE_KEY = keyboard.Key.f6


class ClickEngine:
    """Background thread that fires mouse clicks at a target CPS."""

    def __init__(self):
        self._mouse = mouse.Controller()
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.cps = 10
        self.button = mouse.Button.left
        self.clicks_done = 0

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def set_cps(self, cps):
        with self._lock:
            self.cps = max(1, min(MAX_CPS, int(cps)))

    def set_button(self, button):
        with self._lock:
            self.button = button

    def start(self):
        if self.running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _loop(self):
        """Click loop with drift-corrected timing for stable CPS."""
        next_tick = time.perf_counter()
        while not self._stop_event.is_set():
            with self._lock:
                cps, button = self.cps, self.button
            interval = 1.0 / cps

            self._mouse.click(button)
            self.clicks_done += 1

            next_tick += interval
            delay = next_tick - time.perf_counter()
            if delay > 0:
                # Sleep in small slices so stop() reacts fast
                self._stop_event.wait(delay)
            else:
                # Fell behind (e.g. timer resolution limits) — resync
                next_tick = time.perf_counter()


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.engine = ClickEngine()

        root.title("Auto Clicker")
        root.geometry("340x300")
        root.resizable(False, False)

        pad = {"padx": 16, "pady": 6}

        title = ttk.Label(root, text="Auto Clicker", font=("Helvetica", 16, "bold"))
        title.pack(**pad)

        # --- Mouse button selection ---
        btn_frame = ttk.LabelFrame(root, text="Mouse Button")
        btn_frame.pack(fill="x", **pad)
        self.button_var = tk.StringVar(value="left")
        ttk.Radiobutton(
            btn_frame, text="Left (LMB)", value="left",
            variable=self.button_var, command=self._on_button_change,
        ).pack(side="left", padx=16, pady=8)
        ttk.Radiobutton(
            btn_frame, text="Right (RMB)", value="right",
            variable=self.button_var, command=self._on_button_change,
        ).pack(side="left", padx=16, pady=8)

        # --- CPS slider ---
        cps_frame = ttk.LabelFrame(root, text="Speed (clicks per second)")
        cps_frame.pack(fill="x", **pad)
        self.cps_var = tk.IntVar(value=10)
        self.cps_label = ttk.Label(cps_frame, text="10 CPS")
        self.cps_label.pack(pady=(8, 0))
        self.cps_scale = ttk.Scale(
            cps_frame, from_=1, to=MAX_CPS, orient="horizontal",
            command=self._on_cps_change,
        )
        self.cps_scale.set(10)
        self.cps_scale.pack(fill="x", padx=12, pady=(0, 8))

        # --- Start/stop button + status ---
        self.toggle_btn = ttk.Button(root, text="Start (F6)", command=self.toggle)
        self.toggle_btn.pack(**pad)

        self.status_var = tk.StringVar(value="Status: stopped")
        ttk.Label(root, textvariable=self.status_var).pack()

        # --- Global hotkey listener (F6) ---
        self._kb_listener = keyboard.Listener(on_press=self._on_key_press)
        self._kb_listener.start()

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._refresh_status()

    # ---------- UI callbacks ----------

    def _on_button_change(self):
        choice = self.button_var.get()
        self.engine.set_button(
            mouse.Button.left if choice == "left" else mouse.Button.right
        )

    def _on_cps_change(self, value):
        cps = int(float(value))
        self.cps_var.set(cps)
        self.engine.set_cps(cps)
        self.cps_label.config(text=f"{cps} CPS")

    def _on_key_press(self, key):
        if key == TOGGLE_KEY:
            # Marshal back into the Tk main thread
            self.root.after(0, self.toggle)

    def toggle(self):
        if self.engine.running:
            self.engine.stop()
            self.toggle_btn.config(text="Start (F6)")
        else:
            self.engine.start()
            self.toggle_btn.config(text="Stop (F6)")

    def _refresh_status(self):
        state = "RUNNING" if self.engine.running else "stopped"
        self.status_var.set(
            f"Status: {state}   |   clicks sent: {self.engine.clicks_done}"
        )
        self.root.after(200, self._refresh_status)

    def _on_close(self):
        self.engine.stop()
        self._kb_listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    AutoClickerApp(root)
    root.mainloop()
