# tetris.py - Tetris game for PicoCalc Dashboard
# MicroPython, 320x320 display
import time
import random
import ui

try:
    from picocalc import keyboard  # type: ignore
except ImportError:  # Running off-device: provide stub that reports no input
    class _KeyboardStub:
        @staticmethod
        def readinto(buffer):
            return False

    keyboard = _KeyboardStub()

# Grid size
GRID_W = 10
GRID_H = 20
CELL_SIZE = 14  # Each cell is 14x14px
GRID_X = 20     # Left margin
GRID_Y = 10     # Top margin

# Tetromino shapes (4x4 matrices)
TETROMINOES = [
    # I
    [[1, 1, 1, 1]],
    # O
    [[1, 1], [1, 1]],
    # T
    [[0, 1, 0], [1, 1, 1]],
    # S
    [[0, 1, 1], [1, 1, 0]],
    # Z
    [[1, 1, 0], [0, 1, 1]],
    # J
    [[1, 0, 0], [1, 1, 1]],
    # L
    [[0, 0, 1], [1, 1, 1]],
]

# Colors for each tetromino (VT100 palette indices - reliable on hardware)
# I, O, T, S, Z, J, L respectively
TETROMINO_COLORS = [
    ui.COLOR_BRIGHT_GREEN,  # I piece
    ui.COLOR_WHITE,         # O piece
    ui.COLOR_BLUE_GREEN,    # T piece
    ui.COLOR_TEAL,          # S piece
    ui.COLOR_RED,           # Z piece
    ui.COLOR_BLUE,          # J piece
    ui.COLOR_BROWN,         # L piece
]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.current = None
        self.next = self._random_piece()
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.game_over = False
        self.drop_timer = time.ticks_ms()
        self.key_buffer = bytearray(1)
        self.spawn_piece()

    def spawn_piece(self):
        self.current = self.next
        self.next = self._random_piece()
        self.x = GRID_W // 2 - 2
        self.y = 0
        self.rotation = 0
        if self.collision(self.x, self.y, self.rotation):
            self.game_over = True

    def rotate(self):
        new_rot = (self.rotation + 1) % 4
        if not self.collision(self.x, self.y, new_rot):
            self.rotation = new_rot
            return
        # Simple wall kicks: try shifting left/right if rotation collides
        if not self.collision(self.x - 1, self.y, new_rot):
            self.x -= 1
            self.rotation = new_rot
        elif not self.collision(self.x + 1, self.y, new_rot):
            self.x += 1
            self.rotation = new_rot

    def move(self, dx):
        if not self.collision(self.x + dx, self.y, self.rotation):
            self.x += dx

    def drop(self):
        while not self.collision(self.x, self.y + 1, self.rotation):
            self.y += 1
        self.lock_piece()

    def step(self):
        if not self.collision(self.x, self.y + 1, self.rotation):
            self.y += 1
        else:
            self.lock_piece()

    def lock_piece(self):
        if self.current is None:
            return
        shape = self.get_shape(self.current, self.rotation)
        piece_index = self.current
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    gx = self.x + c
                    gy = self.y + r
                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        self.grid[gy][gx] = piece_index + 1
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        new_grid = [list(row) for row in self.grid if any(cell == 0 for cell in row)]
        cleared = GRID_H - len(new_grid)
        if cleared:
            self.score += [0, 40, 100, 300, 1200][cleared] * self.level
            self.lines += cleared
            self.level = 1 + self.lines // 10
            for _ in range(cleared):
                new_grid.insert(0, [0] * GRID_W)
            self.grid = new_grid

    def collision(self, x, y, rot):
        if self.current is None:
            return False
        shape = self.get_shape(self.current, rot)
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    gx = x + c
                    gy = y + r
                    if gx < 0 or gx >= GRID_W or gy >= GRID_H:
                        return True
                    if gy >= 0 and self.grid[gy][gx]:
                        return True
        return False

    def get_shape(self, idx, rot):
        shape = TETROMINOES[idx]
        for _ in range(rot):
            shape = [list(row) for row in zip(*shape[::-1])]
        return shape

    def _random_piece(self):
        return random.randint(0, len(TETROMINOES) - 1)

    def _drop_interval(self):
        base = 700 - (self.level - 1) * 60
        return max(120, base)

    def draw(self):
        ui.clear()
        # Well outline
        well_width = GRID_W * CELL_SIZE
        well_height = GRID_H * CELL_SIZE
        ui.draw_rect(GRID_X - 2, GRID_Y - 2, well_width + 4, well_height + 4, ui.COLOR_WHITE, fill=False)
        # Grid background
        ui.draw_rect(GRID_X, GRID_Y, well_width, well_height, ui.COLOR_BLACK, fill=True)
        # Draw grid
        for r in range(GRID_H):
            for c in range(GRID_W):
                val = self.grid[r][c]
                if val:
                    color = TETROMINO_COLORS[(val - 1) % len(TETROMINO_COLORS)]
                    x = GRID_X + c * CELL_SIZE
                    y = GRID_Y + r * CELL_SIZE
                    ui.draw_rect(x, y, CELL_SIZE, CELL_SIZE, color, fill=True)
        # Draw current piece
        if self.current is not None:
            shape = self.get_shape(self.current, self.rotation)
            color = TETROMINO_COLORS[self.current]
            for r, row in enumerate(shape):
                for c, val in enumerate(row):
                    if val:
                        x = GRID_X + (self.x + c) * CELL_SIZE
                        y = GRID_Y + (self.y + r) * CELL_SIZE
                        ui.draw_rect(x, y, CELL_SIZE, CELL_SIZE, color, fill=True)
        # Grid lines (optional for clarity)
        grid_color = ui.COLOR_BLUE_GREEN
        for r in range(GRID_H + 1):
            y = GRID_Y + r * CELL_SIZE
            ui.draw_line_horizontal(y, GRID_X, GRID_X + GRID_W * CELL_SIZE, grid_color)
        for c in range(GRID_W + 1):
            x = GRID_X + c * CELL_SIZE
            ui.draw_rect(x, GRID_Y, 1, GRID_H * CELL_SIZE, grid_color, fill=True)
        # Draw next piece preview
        ui.draw_text("Next:", 180, 20, ui.COLOR_WHITE)
        if self.next is not None:
            next_shape = self.get_shape(self.next, 0)
            next_color = TETROMINO_COLORS[self.next]
            for r, row in enumerate(next_shape):
                for c, val in enumerate(row):
                    if val:
                        x = 220 + c * CELL_SIZE
                        y = 40 + r * CELL_SIZE
                        ui.draw_rect(x, y, CELL_SIZE, CELL_SIZE, next_color, fill=True)
        # Draw score/level
        ui.draw_text(f"Score: {self.score}", 180, 120, ui.COLOR_WHITE)
        ui.draw_text(f"Level: {self.level}", 180, 140, ui.COLOR_WHITE)
        ui.draw_text(f"Lines: {self.lines}", 180, 160, ui.COLOR_WHITE)
        ui.draw_text("Arrows: move/rotate", 170, 200, ui.COLOR_WHITE)
        ui.draw_text("Space/Enter: drop", 170, 214, ui.COLOR_WHITE)
        ui.draw_text("Q: quit", 170, 228, ui.COLOR_WHITE)
        if self.game_over:
            ui.center_text("GAME OVER", 160, ui.COLOR_RED)
            ui.center_text("Press Q or Enter", 178, ui.COLOR_WHITE)

    def run(self):
        running = True
        self.drop_timer = time.ticks_ms()
        last_draw = 0
        self.draw()
        while running and not self.game_over:
            now = time.ticks_ms()
            # Handle input
            soft_drop = False
            hard_drop = False
            while keyboard.readinto(self.key_buffer):
                key = self.key_buffer[0]
                if key in (ord('q'), ord('Q')):
                    running = False
                    break
                if key == 67:  # Right arrow
                    self.move(1)
                elif key == 68:  # Left arrow
                    self.move(-1)
                elif key == 65 or key in (ord('w'), ord('W'), ord('x'), ord('X')):  # Up / rotate
                    self.rotate()
                elif key == 66:  # Down arrow
                    soft_drop = True
                elif key in (32, 13):  # Space or Enter for hard drop
                    hard_drop = True
                elif key in (ord('p'), ord('P')):
                    self._pause()
            if not running:
                break

            if hard_drop:
                self.drop()
                self.drop_timer = time.ticks_ms()
            else:
                interval = self._drop_interval()
                if soft_drop:
                    self.step()
                    self.drop_timer = time.ticks_ms()
                elif time.ticks_diff(now, self.drop_timer) >= interval:
                    self.step()
                    self.drop_timer = time.ticks_ms()

            # Redraw at ~20fps
            if time.ticks_diff(now, last_draw) >= 50:
                self.draw()
                last_draw = now

            time.sleep_ms(10)

        # Final draw to show game over state or exit
        self.draw()
        if self.game_over and running:
            # Wait for confirmation to exit
            while True:
                if keyboard.readinto(self.key_buffer):
                    key = self.key_buffer[0]
                    if key in (ord('q'), ord('Q'), 13, 32):
                        break
                time.sleep_ms(30)

    def _pause(self):
        self.draw()
        ui.center_text("PAUSED", 150, ui.COLOR_WHITE)
        ui.center_text("Press P to resume", 170, ui.COLOR_WHITE)
        while True:
            if keyboard.readinto(self.key_buffer):
                key = self.key_buffer[0]
                if key in (ord('p'), ord('P')):
                    self.drop_timer = time.ticks_ms()
                    break
            time.sleep_ms(40)

# Entry point
if __name__ == "__main__":
    game = Tetris()
    game.run()
