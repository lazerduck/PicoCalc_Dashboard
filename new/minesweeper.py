# minesweeper.py - Minesweeper for PicoCalc
import time
import random
import picocalc
from picocalc import keyboard

fb = picocalc.display
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 320

COLOR_BG = 0
COLOR_GRID = 1
COLOR_TEXT = 7
COLOR_MINE = 2
COLOR_FLAG = 3
COLOR_SAFE = 4

CELL_SIZE = 20
GRID_W = 12  # 12x12 grid
GRID_H = 12
NUM_MINES = 20


def draw_cell(x, y, value, revealed, flagged):
    px = x * CELL_SIZE
    py = y * CELL_SIZE + 20
    # Cell background
    if revealed:
        fb.fill_rect(px, py, CELL_SIZE, CELL_SIZE, COLOR_SAFE)
    else:
        fb.fill_rect(px, py, CELL_SIZE, CELL_SIZE, COLOR_BG)
    # Cell border
    fb.rect(px, py, CELL_SIZE, CELL_SIZE, COLOR_GRID)
    # Content
    if revealed:
        if value == -1:
            fb.text("*", px + 6, py + 2, COLOR_MINE)
        elif value > 0:
            fb.text(str(value), px + 6, py + 2, COLOR_TEXT)
    elif flagged:
        fb.text("F", px + 6, py + 2, COLOR_FLAG)

def draw_grid(grid, revealed, flagged, cursor):
    for y in range(GRID_H):
        for x in range(GRID_W):
            draw_cell(x, y, grid[y][x], revealed[y][x], flagged[y][x])
    # Draw cursor
    cx, cy = cursor
    px = cx * CELL_SIZE
    py = cy * CELL_SIZE + 20
    fb.rect(px, py, CELL_SIZE, CELL_SIZE, COLOR_FLAG)
    fb.show()

def place_mines(grid, first_x, first_y):
    # Place NUM_MINES mines, avoiding (first_x, first_y)
    positions = [(x, y) for x in range(GRID_W) for y in range(GRID_H)
                 if not (x == first_x and y == first_y)]
    # Manual shuffle for MicroPython
    n = len(positions)
    for i in range(n-1, 0, -1):
        j = random.randint(0, i)
        positions[i], positions[j] = positions[j], positions[i]
    for i in range(NUM_MINES):
        x, y = positions[i]
        grid[y][x] = -1
    # Fill in numbers
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x] == -1:
                continue
            count = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                        if grid[ny][nx] == -1:
                            count += 1
            grid[y][x] = count

def reveal(grid, revealed, flagged, x, y):
    if flagged[y][x] or revealed[y][x]:
        return
    revealed[y][x] = True
    if grid[y][x] == 0:
        # Flood fill
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    if not revealed[ny][nx]:
                        reveal(grid, revealed, flagged, nx, ny)

def check_win(grid, revealed, flagged):
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x] != -1 and not revealed[y][x]:
                return False
    return True

def main():
    grid = [[0]*GRID_W for _ in range(GRID_H)]
    revealed = [[False]*GRID_W for _ in range(GRID_H)]
    flagged = [[False]*GRID_W for _ in range(GRID_H)]
    cursor = [0, 0]
    mines_placed = False
    game_over = False
    win = False
    temp = bytearray(1)
    fb.fill(COLOR_BG)
    fb.text("MINESWEEPER", 90, 2, COLOR_TEXT)
    fb.text("Arrows: Move  Space: Reveal  F: Flag  Q: Quit", 10, 300, COLOR_TEXT)
    draw_grid(grid, revealed, flagged, cursor)
    while True:
        if keyboard.readinto(temp):
            key = temp[0]
            if key == 27:  # ESC sequence for arrows
                seq = bytearray(2)
                if keyboard.readinto(seq):
                    if seq[0] == ord('['):
                        if seq[1] == ord('A') and cursor[1] > 0:
                            cursor[1] -= 1
                        elif seq[1] == ord('B') and cursor[1] < GRID_H-1:
                            cursor[1] += 1
                        elif seq[1] == ord('C') and cursor[0] < GRID_W-1:
                            cursor[0] += 1
                        elif seq[1] == ord('D') and cursor[0] > 0:
                            cursor[0] -= 1
            elif key in (ord('q'), ord('Q')):
                return
            elif key == ord(' '):  # Reveal
                if not mines_placed:
                    place_mines(grid, cursor[0], cursor[1])
                    mines_placed = True
                if not flagged[cursor[1]][cursor[0]] and not revealed[cursor[1]][cursor[0]]:
                    if grid[cursor[1]][cursor[0]] == -1:
                        revealed[cursor[1]][cursor[0]] = True
                        game_over = True
                        win = False
                    else:
                        reveal(grid, revealed, flagged, cursor[0], cursor[1])
            elif key in (ord('f'), ord('F')):  # Flag
                if not revealed[cursor[1]][cursor[0]]:
                    flagged[cursor[1]][cursor[0]] = not flagged[cursor[1]][cursor[0]]
        draw_grid(grid, revealed, flagged, cursor)
        if not game_over and mines_placed and check_win(grid, revealed, flagged):
            game_over = True
            win = True
        if game_over:
            fb.text("YOU WIN!" if win else "BOOM!", 120, 160, COLOR_MINE if not win else COLOR_FLAG)
            fb.text("Press Q to quit", 100, 200, COLOR_TEXT)
            fb.show()
            while True:
                if keyboard.readinto(temp):
                    key = temp[0]
                    if key in (ord('q'), ord('Q')):
                        return
                time.sleep_ms(30)
        time.sleep_ms(30)

if __name__ == "__main__":
    main()
