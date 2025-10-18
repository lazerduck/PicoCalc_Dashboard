# loadapp.py — PicoCalc app loader/file explorer
import os, sys, time
from fileselect import select_file

def run_app(fb, draw_text, clear, center, wait_key_raw):
    # Use the generic file selector; returns full path or None
    path = select_file(
        path="/sd",
        exts=(".py",),
        title="Select app to run",
        return_full_path=True,
    )

    if not path:
        return

    fname = path.split("/")[-1]
    clear(); center(f"Running {fname}...", 64, 7)
    time.sleep(0.5)
    try:
        with open(path) as f:
            code = f.read()
        exec(code, {})
    except Exception as e:
        clear(); center("Error running app", 64, 2); center(str(e), 90, 2); time.sleep(1)
    return
