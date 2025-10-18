# main.py — PicoCalc boot dashboard (patched: text fg only)
import sys, time, gc
import picocalc
from fileselect import select_file

fb = picocalc.display  # framebuf-like screen
picocalc.terminal.wr("\x1b[?25l")  # hide cursor

# -------- text helper (handles fg-only vs fg+bg builds) --------
def draw_text(s, x, y, fg=7, bg=None):
    try:
        if bg is None:
            fb.text(s, x, y, fg)
        else:
            fb.text(s, x, y, fg, bg)  # will work if your build supports bg
    except TypeError:
        # fallback to simplest form
        fb.text(s, x, y)

# ---------------- UI helpers ----------------
def clear():
    fb.fill(0)

def title(t):
    draw_text(t, 8, 8, 7)

def line(y=22):
    # if your port lacks hline, draw a 1-pixel tall fill_rect
    try:
        fb.hline(8, y, 300, 7)
    except AttributeError:
        fb.fill_rect(8, y, 300, 1, 7)

def center(text, y, color=7):
    x = max(0, (300 - len(text)*8)//2)  # 300 px usable width; tweak if needed
    draw_text(text, x, y, color)

def _battery_label():
    try:
        import battery
        s = battery.status(avg_draw_mA=180, ir_milliohm=120, capacity_mAh=7600)
        if s.get("usb_power"):
            return "USB"
        pct = s.get("percent")
        if pct is None:
            return "--%"
        try:
            pct = int(pct)
        except Exception:
            return "--%"
        pct = max(0, min(100, pct))
        return f"{pct}%"
    except Exception:
        return "--%"

def draw_battery_top_right(color=6):
    label = _battery_label()
    # Right-align within 300 px width, with ~8 px margin
    x = max(0, 300 - len(label)*8 - 8)
    draw_text(label, x, 8, color)

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

def show_menu():
    menu_items = [
        ("Open REPL", "1"),
        ("Memory stats", "2"),
        ("Battery status", "3"),
        ("Run App", "4"),
        ("Edit file", "5"),
        ("Play music", "6"),
        ("Power off / reset", "q"),
    ]
    selected = 0
    while True:
        clear()
        title("PicoCalc Dashboard")
        draw_battery_top_right()
        line()
        y0 = 36
        for i, (label, _) in enumerate(menu_items):
            color = 6 if i == selected else 7
            prefix = "> " if i == selected else "  "
            draw_text(prefix + label, 12, y0 + i*18, color)
        draw_text("Use UP/DOWN, Enter to select", 12, 176, 6)
        # Wait for key
        k = wait_key_raw()
        if k == 'A':  # up
            selected = (selected - 1) % len(menu_items)
        elif k == 'B':  # down
            selected = (selected + 1) % len(menu_items)
        elif k in ('\r', '\n'):  # Enter
            return menu_items[selected][1]
        elif k in ('q', 'Q'):  # allow q to quit
            return 'q'

def show_mem():
    clear()
    title("Memory")
    draw_battery_top_right()
    line()
    free_b = gc.mem_free()
    alloc_b = gc.mem_alloc()
    total_b = free_b + alloc_b
    pct_free = int(100 * free_b / total_b) if total_b else 0
    # Layout
    draw_text(f"Total: {total_b} B", 12, 38, 7)
    draw_text(f"Free : {free_b} B",  12, 56, 7)
    draw_text(f"Alloc: {alloc_b} B", 12, 74, 7)
    draw_text(f"Free: {pct_free}%", 180, 56, 6)
    # Bar graph
    x, y, w, h = 12, 98, 200, 16
    try:
        fb.rect(x, y, w, h, 7)
    except Exception:
        fb.fill_rect(x, y, w, 1, 7); fb.fill_rect(x, y+h-1, w, 1, 7)
        fb.fill_rect(x, y, 1, h, 7); fb.fill_rect(x+w-1, y, 1, h, 7)
    free_w = int((w-2) * free_b / total_b) if total_b else 0
    alloc_w = (w-2) - free_w
    # Free memory bar (green-ish)
    fb.fill_rect(x+1, y+1, free_w, h-2, 3)
    # Allocated memory bar (red-ish)
    fb.fill_rect(x+1+free_w, y+1, alloc_w, h-2, 2)
    draw_text("Free", x+4, y+h+2, 3)
    draw_text("Used", x+w-40, y+h+2, 2)
    center("See REPL for details", 130, 6)
    wait_key_raw()

def show_battery():
    clear()
    title("Battery")
    draw_battery_top_right()
    line()
    try:
        import battery  # your /sd/battery.py (2P version)
        s = battery.status(avg_draw_mA=180, ir_milliohm=120, capacity_mAh=7600)
        mv = s.get("vsys_mV")
        if s.get("usb_power"):
            center("USB power detected", 54, 6)
            draw_text(f"VSYS : {mv} mV", 12, 78, 7)
            draw_text("(percent disabled on USB)", 12, 96, 7)
        else:
            pct = s.get("percent", 0)
            hrs = s.get("hours_left")
            draw_text(f"Voltage : {mv} mV", 12, 54, 7)
            draw_text(f"Charge  : {pct} %", 12, 72, 7)
            if hrs is not None:
                draw_text(f"Est. hrs: {hrs}", 12, 90, 7)
            # simple bar
            x, y, w, h = 12, 110, 120, 12
            try:
                fb.rect(x, y, w, h, 7)
            except Exception:
                fb.fill_rect(x, y, w, 1, 7); fb.fill_rect(x, y+h-1, w, 1, 7)
                fb.fill_rect(x, y, 1, h, 7); fb.fill_rect(x+w-1, y, 1, h, 7)
            fillw = int((w-2) * max(0, min(100, pct)) / 100)
            fb.fill_rect(x+1, y+1, fillw, h-2, 7)
    except Exception as e:
        center("Battery info N/A", 64, 6)
        draw_text(str(e), 12, 90, 7)
        draw_text("Ensure /sd/battery.py is present", 12, 108, 7)
    wait_key_raw()

# ---------------- main ----------------
def main():
    while True:
        ch = show_menu()
        if ch == "1":
            picocalc.terminal.wr("\x1b[?25h") 
            clear(); center("Exiting to REPL...", 64, 7); time.sleep(0.3)
            return
        elif ch == "2":
            show_mem()
        elif ch == "3":
            show_battery()
        elif ch == "4":
            try:
                import loadapp
                loadapp.run_app(fb, draw_text, clear, center, wait_key_raw)
                center("App finished. Press any key...", 120, 6)
                wait_key_raw()
            except Exception as e:
                clear(); center("App loader error", 64, 2); center(str(e), 90, 2); time.sleep(1)
        elif ch == "5":
            try:
                path = select_file(path="/sd", exts=(".py", ".txt", ".json", ".csv", ".log"), title="Select file to edit", return_full_path=True)
                if not path:
                    continue
                # Prefer firmware-baked edit(), fallback to bundled nano
                edit(path)

                center("Editor closed. Press any key...", 120, 6)
                wait_key_raw()
            except Exception as e:
                clear(); center("Editor error", 64, 2); center(str(e), 90, 2); time.sleep(1)
        elif ch == "6":
            try:
                path = select_file(path="/sd", exts=(".mp3",), title="Select music file", return_full_path=True)
                if not path:
                    continue
                import play
                play.play_music(path)
                center("Music playback finished. Press any key...", 120, 6)
                wait_key_raw()
            except Exception as e:
                clear(); center("Editor error", 64, 2); center(str(e), 90, 2); time.sleep(1)
        elif ch in ("q","Q"):
            clear(); center("Resetting...", 64, 7); time.sleep(0.5)
            try:
                import machine
                machine.reset()
            except Exception:
                sys.exit()
        # ignore others and re-show menu

main()
