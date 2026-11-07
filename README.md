# Auto Clicker

A simple cross-platform auto clicker with a GUI — up to **300 clicks per second**, with your choice of **left (LMB)** or **right (RMB)** mouse button.

## Features

- Adjustable speed: 1–300 CPS (clicks per second)
- LMB / RMB selection
- Global **F6** hotkey to start/stop from anywhere
- Start/Stop button in the GUI
- Live click counter
- Clicks at the current cursor position — works in any app

## Requirements

- Python 3.8+
- `pynput`

## Install & Run

```bash
pip install -r requirements.txt
python autoclicker.py
```

## Platform Notes

### macOS
macOS requires Accessibility permission for the terminal (or app) running the script:

1. Run the script once.
2. Go to **System Settings → Privacy & Security → Accessibility**.
3. Enable your terminal app (Terminal, iTerm, VS Code, etc.).
4. Restart the script.

Alternatively, double-click `AutoClicker.command` to launch without typing commands.

### Windows
Works out of the box. If the F6 hotkey doesn't register in some games, run the terminal as Administrator.

### Linux
Works on X11. Wayland restricts synthetic input — use an X11 session.

## Files

| File | Purpose |
|---|---|
| `autoclicker.py` | The auto clicker (GUI + engine) |
| `AutoClicker.command` | macOS double-click launcher |
| `autoclicker.html` | In-browser demo version (clicks only inside the page) |
| `requirements.txt` | Python dependencies |

## Disclaimer

For personal/educational use. Some games and apps prohibit automation — check their terms of service.
