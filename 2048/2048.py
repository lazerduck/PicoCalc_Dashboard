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
COLOR_TEXT = 7
COLOR_EMPTY = 1
COLOR_WIN = 6
COLOR_LOSE = 2

# Tile colors based on value (4-bit color palette)
def get_tile_color(value):
    if value == 0:
        return COLOR_BG  # Black for empty tiles
    elif value == 2:
        return 3  # Green
    elif value == 4:
        return 2  # Red
    elif value == 8:
        return 6  # Yellow
    elif value == 16:
        return 5  # Magenta
    elif value == 32:
        return 4  # Cyan
    elif value == 64:
        return 1  # Blue
    elif value == 128:
        return 3  # Green (cycle)
    elif value == 256:
        return 2  # Red
    elif value == 512:
        return 6  # Yellow
    elif value == 1024:
        return 5  # Magenta
    elif value == 2048:
        return 4  # Cyan
    else:
        return 7  # White for very high values

# Game constants
GRID_SIZE = 4
TILE_SIZE = 60
GRID_OFFSET_X = 20
GRID_OFFSET_Y = 40

import random

def draw_grid(grid, score, state):
    fb.fill(COLOR_BG)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            val = grid[y][x]
            tx = GRID_OFFSET_X + x * TILE_SIZE
            ty = GRID_OFFSET_Y + y * TILE_SIZE
            color = get_tile_color(val)
            fb.fill_rect(tx, ty, TILE_SIZE-4, TILE_SIZE-4, color)
            if val:
                fb.text(str(val), tx+TILE_SIZE//2-8, ty+TILE_SIZE//2-8, COLOR_TEXT)
    fb.text(f"Score: {score}", 10, 10, COLOR_TEXT)
    if state == "win":
        fb.text("YOU WIN!", 120, 10, COLOR_WIN)
    elif state == "lose":
        fb.text("GAME OVER", 120, 10, COLOR_LOSE)
    fb.text("Q: Quit", 10, 300, COLOR_TEXT)
    fb.text("Arrows: Move", 120, 300, COLOR_TEXT)

def draw_grid_with_offsets(grid, score, state, offsets=None):
    fb.fill(COLOR_BG)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            val = grid[y][x]
            dx, dy = 0, 0
            if offsets and (y, x) in offsets:
                dx, dy = offsets[(y, x)]
            tx = GRID_OFFSET_X + x * TILE_SIZE + dx
            ty = GRID_OFFSET_Y + y * TILE_SIZE + dy
            color = get_tile_color(val)
            fb.fill_rect(tx, ty, TILE_SIZE-4, TILE_SIZE-4, color)
            if val:
                fb.text(str(val), tx+TILE_SIZE//2-8, ty+TILE_SIZE//2-8, COLOR_TEXT)
    fb.text(f"Score: {score}", 10, 10, COLOR_TEXT)
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
    prev_grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
    while True:
        draw_grid(grid, score, state)
        if state != "playing":
            time.sleep(1)
            break
        # Input
        moved, s = False, 0  # Always initialize
        direction = None
        if keyboard.readinto(temp):
            key = temp[0]
            if key in (ord('q'), ord('Q')):
                break
            elif key == 65: # Up
                direction = 'up'
            elif key == 66: # Down
                direction = 'down'
            elif key == 67: # Right
                direction = 'right'
            elif key == 68: # Left
                direction = 'left'
        if direction:
            # Copy grid for animation
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    prev_grid[y][x] = grid[y][x]
            moved, s = move_grid(grid, direction)
            if moved:
                # Animate the slide
                frames = 4  # Reduced from 5 to lower frame rate
                for frame in range(1, frames+1):
                    offsets = {}
                    # Calculate offset based on direction only
                    # Tiles slide from their "before" position in the direction of movement
                    if direction == 'up':
                        for y in range(GRID_SIZE):
                            for x in range(GRID_SIZE):
                                if grid[y][x] != 0:
                                    # Find how far this tile should have slid from
                                    # Only animate if grid changed
                                    if prev_grid[y][x] != grid[y][x]:
                                        # Tile came from below
                                        dy = int((TILE_SIZE) * (frames-frame) / frames)
                                        offsets[(y, x)] = (0, dy)
                    elif direction == 'down':
                        for y in range(GRID_SIZE):
                            for x in range(GRID_SIZE):
                                if grid[y][x] != 0:
                                    if prev_grid[y][x] != grid[y][x]:
                                        dy = int(-(TILE_SIZE) * (frames-frame) / frames)
                                        offsets[(y, x)] = (0, dy)
                    elif direction == 'left':
                        for y in range(GRID_SIZE):
                            for x in range(GRID_SIZE):
                                if grid[y][x] != 0:
                                    if prev_grid[y][x] != grid[y][x]:
                                        dx = int((TILE_SIZE) * (frames-frame) / frames)
                                        offsets[(y, x)] = (dx, 0)
                    elif direction == 'right':
                        for y in range(GRID_SIZE):
                            for x in range(GRID_SIZE):
                                if grid[y][x] != 0:
                                    if prev_grid[y][x] != grid[y][x]:
                                        dx = int(-(TILE_SIZE) * (frames-frame) / frames)
                                        offsets[(y, x)] = (dx, 0)
                    draw_grid_with_offsets(grid, score, state, offsets)
                    time.sleep_ms(100)  # Increased from 20ms to reduce flicker
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
