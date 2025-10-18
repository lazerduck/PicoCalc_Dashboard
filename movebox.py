# movebox.py — Simple animated moving square demo for PicoCalc
import picocalc, time

fb = picocalc.display  # framebuf-like screen

WIDTH, HEIGHT = 320, 320
BOX_SIZE = 32
COLOR = 4  # blue-ish
BG = 0

x, y = 0, 0
vx, vy = 2, 2

for _ in range(80):
    fb.fill(BG)
    fb.fill_rect(x, y, BOX_SIZE, BOX_SIZE, COLOR)
    # Draw border
    fb.rect(0, 0, WIDTH, HEIGHT, 7)
    fb.text("movebox.py", 8, 8, 7)
    # If your display needs flushing, add fb.show() here
    time.sleep(0.04)
    x += vx
    y += vy
    if x + BOX_SIZE >= WIDTH or x <= 0:
        vx = -vx
    if y + BOX_SIZE >= HEIGHT or y <= 0:
        vy = -vy
