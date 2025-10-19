# stopwatch.py - Simple Stopwatch for PicoCalc
import time
import picocalc
from picocalc import keyboard

fb = picocalc.display
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 320

COLOR_BG = 0
COLOR_TEXT = 7
COLOR_ACCENT = 3
COLOR_STOP = 2
COLOR_START = 4


def draw_time(ms, running):
    fb.fill(COLOR_BG)
    seconds = ms // 1000
    centis = (ms % 1000) // 10
    mins = seconds // 60
    secs = seconds % 60
    time_str = f"{mins:02}:{secs:02}.{centis:02}"
    fb.text("STOPWATCH", 100, 40, COLOR_ACCENT)
    fb.text(time_str, 100, 120, COLOR_TEXT)
    fb.text("S: Start/Stop  R: Reset  Q: Quit", 30, 200, COLOR_ACCENT)
    if running:
        fb.text("RUNNING", 120, 160, COLOR_START)
    else:
        fb.text("STOPPED", 120, 160, COLOR_STOP)
    fb.show()

def main():
    running = False
    elapsed = 0
    last_tick = time.ticks_ms()
    temp = bytearray(1)
    draw_time(elapsed, running)
    while True:
        if running:
            now = time.ticks_ms()
            elapsed += time.ticks_diff(now, last_tick)
            last_tick = now
            draw_time(elapsed, running)
        else:
            last_tick = time.ticks_ms()
        # Non-blocking key check
        if keyboard.readinto(temp):
            key = temp[0]
            if key in (ord('s'), ord('S')):
                running = not running
                draw_time(elapsed, running)
            elif key in (ord('r'), ord('R')):
                elapsed = 0
                draw_time(elapsed, running)
            elif key in (ord('q'), ord('Q')):
                return
        time.sleep_ms(30)

if __name__ == "__main__":
    main()
