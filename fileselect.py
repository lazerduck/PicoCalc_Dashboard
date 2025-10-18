# fileselect.py — generic file selector for MicroPython UIs
#
# Contract
# - Inputs: UI callbacks (draw_text, clear, center, wait_key_raw),
#           optional path, extensions, title, and return_full_path flag.
# - Behavior: Renders a simple scrollable list, handles up/down/enter/cancel.
# - Outputs: Returns selected file (full path or basename) or None if cancelled
#            or if no files match.
#
# Key bindings (match existing PicoCalc conventions):
# - 'A' => up
# - 'B' => down
# - Enter ("\r" or "\n") => select
# - 'q' or 'Q' => cancel
#
# Example usage:
# from fileselect import select_file
# fname = select_file(draw_text, clear, center, wait_key_raw, path="/sd", exts=(".py",))
# if fname:
#     # do something with fname
#     pass

import os
import time
import picocalc

fb = picocalc.display 

def draw_text(s, x, y, fg=7, bg=None):
    try:
        if bg is None:
            fb.text(s, x, y, fg)
        else:
            fb.text(s, x, y, fg, bg)  # will work if your build supports bg
    except TypeError:
        # fallback to simplest form
        fb.text(s, x, y)

def clear():
    fb.fill(0)

def center(text, y, color=7):
    x = max(0, (300 - len(text)*8)//2)  # 300 px usable width; tweak if needed
    draw_text(text, x, y, color)

def wait_key_raw():
    # Reads a single raw key from stdin (blocking)
    # Returns: key code or character
    import sys
    ch = sys.stdin.read(1)
    if ch == '\x1b':  # Escape sequence (arrow keys)
        ch2 = sys.stdin.read(1)
        if ch2 == '[':
            ch3 = sys.stdin.read(1)
            return ch3  # 'A'=up, 'B'=down, 'C'=right, 'D'=left
        return ch2
    return ch

def _normalize_exts(exts):
    if exts is None:
        return None
    if isinstance(exts, str):
        return (exts,)
    try:
        return tuple(exts)
    except TypeError:
        return None


def list_files(path="/sd", exts=(".py",)):
    """List files in path filtered by extensions.

    - path: folder to list
    - exts: string extension, iterable of extensions, or None for no filter
            (e.g., ".py" or (".txt", ".csv"))
    """
    try:
        entries = os.listdir(path)
    except Exception:
        return []

    norm_exts = _normalize_exts(exts)

    def _match(fname):
        if norm_exts is None:
            return True
        for e in norm_exts:
            if fname.endswith(e):
                return True
        return False

    # Filter out hidden-like entries and non-matching names; sort for stability
    files = [f for f in entries if not f.startswith(".") and _match(f)]
    files.sort()
    return files


def select_file(
    *,
    path="/sd",
    exts=(".py",),
    title="Select file",
    return_full_path=True,
    y_start=40,
    line_h=18,
    page_size=7,
):
    """Interactive file selector UI.

    Returns selected path (full or basename) or None if cancelled/empty.

    Parameters
    - draw_text(x: str, x: int, y: int, color: int)
    - clear(): clears screen
    - center(text: str, y: int, color: int): draw centered line
    - wait_key_raw(): returns a raw key code (expects 'A','B','\r','\n','q','Q')

    Optional kwargs
    - path: folder to browse (default: '/sd')
    - exts: string or tuple/list of extensions, or None for all files
    - title: UI title line
    - return_full_path: True => return '/sd/filename.py', False => 'filename.py'
    - y_start: top Y position for list entries
    - line_h: line height in pixels
    - page_size: how many items to show at once
    """
    files = list_files(path, exts)
    if not files:
        clear()
        center("No files found", 64, 2)
        time.sleep(0.75)
        return None

    selected = 0
    top = 0

    while True:
        clear()
        center(title, 16, 7)

        # Clamp window
        if selected < top:
            top = selected
        elif selected >= top + page_size:
            top = selected - page_size + 1

        # Draw visible window
        for i in range(page_size):
            idx = top + i
            if idx >= len(files):
                break
            fname = files[idx]
            is_sel = idx == selected
            color = 6 if is_sel else 7
            prefix = "> " if is_sel else "  "
            y = y_start + i * line_h
            draw_text(prefix + fname, 12, y, color)

        # Footer/help
        draw_text("UP/DOWN: select, Enter: choose, q: cancel", 12, y_start + page_size * line_h + 8, 6)

        k = wait_key_raw()
        if k == "A":  # up
            selected = (selected - 1) % len(files)
        elif k == "B":  # down
            selected = (selected + 1) % len(files)
        elif k in ("\r", "\n"):
            fname = files[selected]
            return (path.rstrip("/") + "/" + fname) if return_full_path else fname
        elif isinstance(k, str) and (k == "q" or k == "Q"):
            return None
        # ignore other keys and redraw
