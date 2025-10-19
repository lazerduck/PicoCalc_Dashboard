# 2048.py - Simple 2048 game for PicoCalc
# Controls: Arrow keys to move, Q to quit
import time
import picocalc
from picocalc import keyboard

# Display setup
fb = picocalc.display
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 320

# Colors
COLOR_BG = 0
COLOR_TILE = 3
COLOR_TEXT = 7
COLOR_EMPTY = 1
COLOR_WIN = 6
COLOR_LOSE = 2

# Game constants
GRID_SIZE = 4
TILE_SIZE = 60
GRID_OFFSET_X = 20
GRID_OFFSET_Y = 40

import random

def draw_grid(grid, score, state):
    fb.fill(COLOR_BG)
    # Draw tiles
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            val = grid[y][x]
            tx = GRID_OFFSET_X + x * TILE_SIZE
            ty = GRID_OFFSET_Y + y * TILE_SIZE
            color = COLOR_TILE if val else COLOR_EMPTY
            fb.fill_rect(tx, ty, TILE_SIZE-4, TILE_SIZE-4, color)
            if val:
                fb.text(str(val), tx+TILE_SIZE//2-8, ty+TILE_SIZE//2-8, COLOR_TEXT)
    # Draw score
    fb.text(f"Score: {score}", 10, 10, COLOR_TEXT)
    # Draw state
    if state == "win":
        fb.text("YOU WIN!", 120, 10, COLOR_WIN)
    elif state == "lose":
        fb.text("GAME OVER", 120, 10, COLOR_LOSE)
    fb.text("Q: Quit", 10, 300, COLOR_TEXT)
    fb.text("Arrows: Move", 120, 300, COLOR_TEXT)

def add_tile(grid):
    empty = [(y, x) for y in range(GRID_SIZE) for x in range(GRID_SIZE) if grid[y][x] == 0]
    if empty:
        y, x = random.choice(empty)
        grid[y][x] = 2 if random.random() < 0.9 else 4

def move_grid(grid, direction):
    moved = False
    total_score = 0
    def slide(row):
        new_row = [v for v in row if v]
        score_gained = 0
        i = 0
        while i < len(new_row)-1:
            if new_row[i] == new_row[i+1]:
                new_row[i] *= 2
                score_gained += new_row[i]
                new_row.pop(i+1)
                i += 1
            i += 1
        new_row += [0]*(GRID_SIZE-len(new_row))
        return new_row, score_gained
    if direction == 'up':
        for x in range(GRID_SIZE):
            col = [grid[y][x] for y in range(GRID_SIZE)]
            new_col, score_gained = slide(col)
            if col != new_col:
                moved = True
            total_score += score_gained
            for y in range(GRID_SIZE):
                grid[y][x] = new_col[y]
    elif direction == 'down':
        for x in range(GRID_SIZE):
            col = [grid[y][x] for y in range(GRID_SIZE)][::-1]
            new_col, score_gained = slide(col)
            new_col = new_col[::-1]
            if [grid[y][x] for y in range(GRID_SIZE)] != new_col:
                moved = True
            total_score += score_gained
            for y in range(GRID_SIZE):
                grid[y][x] = new_col[y]
    elif direction == 'left':
        for y in range(GRID_SIZE):
            row = grid[y]
            new_row, score_gained = slide(row)
            if row != new_row:
                moved = True
            total_score += score_gained
            grid[y] = new_row
    elif direction == 'right':
        for y in range(GRID_SIZE):
            row = grid[y][::-1]
            new_row, score_gained = slide(row)
            new_row = new_row[::-1]
            if grid[y] != new_row:
                moved = True
            total_score += score_gained
            grid[y] = new_row
    return moved, total_score

def check_win(grid):
    for row in grid:
        if 2048 in row:
            return True
    return False

def check_lose(grid):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] == 0:
                return False
            for dy, dx in ((0,1),(1,0)):
                ny, nx = y+dy, x+dx
                if ny<GRID_SIZE and nx<GRID_SIZE and grid[y][x]==grid[ny][nx]:
                    return False
    return True

def main():
    grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
    score = 0
    state = "playing"
    add_tile(grid)
    add_tile(grid)
    temp = bytearray(1)
    while True:
        draw_grid(grid, score, state)
        if state != "playing":
            time.sleep(1)
            break
        # Input
        moved, s = False, 0  # Always initialize
        if keyboard.readinto(temp):
            key = temp[0]
            if key in (ord('q'), ord('Q')):
                break
            elif key == 65: # Up
                moved, s = move_grid(grid, 'up')
            elif key == 66: # Down
                moved, s = move_grid(grid, 'down')
            elif key == 67: # Right
                moved, s = move_grid(grid, 'right')
            elif key == 68: # Left
                moved, s = move_grid(grid, 'left')
        if moved:
            add_tile(grid)
            score += s
        if check_win(grid):
            state = "win"
        elif check_lose(grid):
            state = "lose"
        time.sleep_ms(60)
    fb.fill(COLOR_BG)
    fb.text("Thanks for playing!", 80, 140, COLOR_TEXT)
    time.sleep(1)
    fb.fill(COLOR_BG)

if __name__ == "__main__":
    main()
