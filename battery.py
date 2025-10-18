# main.py — PicoCalc boot dashboard (patched: text fg only)
import sys, time, gc
import picocalc

fb = picocalc.display  # framebuf-like screen

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

def wait_key(prompt="Press a key..."):
    center(prompt, 200, 6)
    ch = sys.stdin.read(1)
    return ch

def show_menu():
    clear()
    title("PicoCalc Dashboard")
    line()
    draw_text("1) Open REPL",        12, 36, 7)
    draw_text("2) Memory stats",     12, 54, 7)
    draw_text("3) Battery status",   12, 72, 7)
    draw_text("q) Power off / reset",12, 90, 7)
    draw_text("Choose:",             12, 116, 6)
    return wait_key("1/2/3 or q")

def show_mem():
    clear()
    title("Memory")
    line()
    free_b = gc.mem_free()
    alloc_b = gc.mem_alloc()
    total_b = free_b + alloc_b
    draw_text(f"Total: {total_b} B", 12, 42, 7)
    draw_text(f"Free : {free_b} B",  12, 60, 7)
    draw_text(f"Alloc: {alloc_b} B", 12, 78, 7)
    center("See REPL for details", 108, 6)
    print("[mem] total:", total_b, "free:", free_b, "alloc:", alloc_b)
    try:
        import micropython
        micropython.mem_info()
    except Exception:
        pass
    wait_key("Press any key")

def show_battery():
    clear()
    title("Battery")
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
    wait_key("Press any key")

# ---------------- main ----------------
def main():
    while True:
        ch = show_menu()
        if ch == "1":
            clear(); center("Exiting to REPL...", 64, 7); time.sleep(0.3)
            return
        elif ch == "2":
            show_mem()
        elif ch == "3":
            show_battery()
        elif ch in ("q","Q"):
            clear(); center("Resetting...", 64, 7); time.sleep(0.5)
            try:
                import machine
                machine.reset()
            except Exception:
                sys.exit()
        # ignore others and re-show menu

main()
