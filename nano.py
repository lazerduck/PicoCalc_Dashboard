# nano.py — Minimal text editor for PicoCalc
import picocalc, os, sys, time

fb = picocalc.display
WIDTH, HEIGHT = 320, 320
LINES_ON_SCREEN = 16
CHARS_PER_LINE = 38
BG = 0
FG = 7
CURSOR_COLOR = 2

# Helper to draw text line
def draw_line(text, y, cursor_x=None):
    fb.fill_rect(0, y, WIDTH, 16, BG)
    fb.text(text, 4, y, FG)
    if cursor_x is not None:
        # Adjust cursor to 8x8 and align with font
        fb.fill_rect(4 + cursor_x*6, y, 6, 8, CURSOR_COLOR)
        fb.text(text[cursor_x:cursor_x+1], 4 + cursor_x*6, y, FG)

# Main editor function
def edit_file(filename):
    # Load file
    try:
        with open(filename) as f:
            lines = f.read().splitlines()
    except Exception:
        lines = ['']
    if not lines:
        lines = ['']
    cursor_y, cursor_x = 0, 0
    top_line = 0
    status = f"nano.py - {filename}"
    while True:
        fb.fill(BG)
        fb.text(status, 4, 4, FG)
        # Draw lines
        for i in range(LINES_ON_SCREEN):
            idx = top_line + i
            if idx < len(lines):
                line = lines[idx]
                # Pad line to CHARS_PER_LINE manually (MicroPython safe)
                if len(line) < CHARS_PER_LINE:
                    line = line + ' ' * (CHARS_PER_LINE - len(line))
                else:
                    line = line[:CHARS_PER_LINE]
                draw_line(line, 24 + i*18, cursor_x if i == cursor_y else None)
            else:
                draw_line(' ' * CHARS_PER_LINE, 24 + i*18)
        fb.text("^S: Save  ^Q: Quit", 4, HEIGHT-20, 6)
        # Get key
        k = sys.stdin.read(1)
        if k == '\x1b':
            k2 = sys.stdin.read(1)
            if k2 == '[':
                k3 = sys.stdin.read(1)
                if k3 == 'A':  # up
                    if cursor_y > 0:
                        cursor_y -= 1
                    elif top_line > 0:
                        top_line -= 1
                elif k3 == 'B':  # down
                    if cursor_y < LINES_ON_SCREEN-1 and top_line+cursor_y+1 < len(lines):
                        cursor_y += 1
                    elif top_line+LINES_ON_SCREEN < len(lines):
                        top_line += 1
                elif k3 == 'C':  # right
                    if cursor_x < len(lines[top_line+cursor_y]):
                        cursor_x += 1
                elif k3 == 'D':  # left
                    if cursor_x > 0:
                        cursor_x -= 1
        elif k == '\r':  # Enter
            insert_at = top_line + cursor_y
            lines.insert(insert_at + 1, '')
            if cursor_y < LINES_ON_SCREEN - 1:
                cursor_y += 1
            else:
                top_line += 1
            cursor_x = 0
        elif k == '\x7f':  # Backspace
            line = lines[top_line+cursor_y]
            if cursor_x > 0:
                lines[top_line+cursor_y] = line[:cursor_x-1] + line[cursor_x:]
                cursor_x -= 1
            elif cursor_x == 0 and top_line+cursor_y > 0:
                prev = lines.pop(top_line+cursor_y)
                cursor_y = max(cursor_y-1, 0)
                cursor_x = len(lines[top_line+cursor_y])
                lines[top_line+cursor_y] += prev
        elif k == '\x11':  # Ctrl-Q
            break
        elif k == '\x13':  # Ctrl-S
            try:
                with open(filename, 'w') as f:
                    f.write('\n'.join(lines))
                status = f"Saved {filename}"
            except Exception as e:
                status = f"Save error: {e}"
        elif 32 <= ord(k) <= 126:  # printable
            line = lines[top_line+cursor_y]
            lines[top_line+cursor_y] = line[:cursor_x] + k + line[cursor_x:]
            cursor_x += 1
            if cursor_x > CHARS_PER_LINE-1:
                cursor_x = CHARS_PER_LINE-1
        # Clamp cursor
        cursor_x = min(cursor_x, len(lines[top_line+cursor_y]))
        cursor_x = max(cursor_x, 0)
        if cursor_y > len(lines)-1:
            cursor_y = len(lines)-1


# Entry point for app loader or direct exec
def main(filename="/sd/test.txt"):
    edit_file(filename)


main()
