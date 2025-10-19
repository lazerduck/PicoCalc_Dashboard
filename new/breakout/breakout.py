# breakout.py - Simple Breakout clone for PicoCalc
# Controls: Left/Right arrows to move paddle, Q to quit
import time
import picocalc

# Use PicoCalc keyboard module for non-blocking input
from picocalc import keyboard

# Screen setup
fb = picocalc.display  # 320x320 framebuffer
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 320

# Colors
COLOR_BLACK = 0
COLOR_BLUE = 1
COLOR_RED = 2
COLOR_GREEN = 3
COLOR_CYAN = 4
COLOR_MAGENTA = 5
COLOR_YELLOW = 6
COLOR_WHITE = 7

# Game constants
PADDLE_WIDTH = 50
PADDLE_HEIGHT = 8
PADDLE_Y = SCREEN_HEIGHT - 30
PADDLE_SPEED = 20

BALL_SIZE = 6
BALL_SPEED_X = 3
BALL_SPEED_Y = -3
GAME_SPEED = 1.0  # Multiplier for overall game speed (increase for faster)

BRICK_WIDTH = 38
BRICK_HEIGHT = 12
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_PADDING = 2
BRICK_OFFSET_TOP = 40

# Game state
class Game:
    def __init__(self):
        self.paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
        self.ball_x = SCREEN_WIDTH // 2
        self.ball_y = SCREEN_HEIGHT // 2
        self.ball_dx = BALL_SPEED_X * GAME_SPEED
        self.ball_dy = BALL_SPEED_Y * GAME_SPEED
        self.score = 0
        self.lives = 3
        self.running = True
        self.game_over = False
        self.won = False

        # Store previous positions for erasing
        self.prev_paddle_x = self.paddle_x
        self.prev_ball_x = self.ball_x
        self.prev_ball_y = self.ball_y
        self.prev_score = 0
        self.prev_lives = 3

        # Track if we need full redraw
        self.needs_full_redraw = True

        # Create bricks - list of (x, y, color, active)
        self.bricks = []
        colors = [COLOR_RED, COLOR_MAGENTA, COLOR_YELLOW, COLOR_GREEN, COLOR_CYAN]

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = col * (BRICK_WIDTH + BRICK_PADDING) + 10
                y = row * (BRICK_HEIGHT + BRICK_PADDING) + BRICK_OFFSET_TOP
                color = colors[row % len(colors)]
                self.bricks.append([x, y, color, True])  # x, y, color, active

    def check_input(self):
        """Non-blocking input check using picocalc.keyboard.readinto()"""
        temp = bytearray(1)
        if keyboard.readinto(temp):
            key = temp[0]
            # Arrow keys: 0xAE = left, 0xAF = right (per firmware font table)
            if key == 68:  # Left arrow
                self.paddle_x -= PADDLE_SPEED
            elif key == 67:  # Right arrow
                self.paddle_x += PADDLE_SPEED
            # Q or q to quit
            elif key in (ord('q'), ord('Q')):
                self.running = False
        # Keep paddle on screen
        if self.paddle_x < 0:
            self.paddle_x = 0
        if self.paddle_x > SCREEN_WIDTH - PADDLE_WIDTH:
            self.paddle_x = SCREEN_WIDTH - PADDLE_WIDTH

    def update(self):
        """Update game state"""
        if self.game_over or self.won:
            return

        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Ball collision with walls
        if self.ball_x <= 0 or self.ball_x >= SCREEN_WIDTH - BALL_SIZE:
            self.ball_dx = -self.ball_dx
            self.ball_x = max(0, min(SCREEN_WIDTH - BALL_SIZE, self.ball_x))

        if self.ball_y <= 0:
            self.ball_dy = -self.ball_dy
            self.ball_y = 0

        # Ball falls off bottom - lose life
        if self.ball_y >= SCREEN_HEIGHT:
            self.lives -= 1
            self.needs_full_redraw = True  # Redraw everything when life lost
            if self.lives <= 0:
                self.game_over = True
            else:
                # Reset ball
                self.ball_x = SCREEN_WIDTH // 2
                self.ball_y = SCREEN_HEIGHT // 2
                self.ball_dy = -abs(self.ball_dy)

        # Ball collision with paddle
        if (self.ball_y + BALL_SIZE >= PADDLE_Y and
            self.ball_y < PADDLE_Y + PADDLE_HEIGHT and
            self.ball_x + BALL_SIZE >= self.paddle_x and
            self.ball_x <= self.paddle_x + PADDLE_WIDTH):

            self.ball_dy = -abs(self.ball_dy)  # Always bounce up
            self.ball_y = PADDLE_Y - BALL_SIZE  # Place ball on top of paddle

            # Add spin based on where ball hits paddle
            hit_pos = (self.ball_x + BALL_SIZE/2 - self.paddle_x) / PADDLE_WIDTH
            self.ball_dx = int((hit_pos - 0.5) * 6)  # -3 to +3

        # Ball collision with bricks
        for brick in self.bricks:
            if not brick[3]:  # Skip inactive bricks
                continue

            bx, by, color, active = brick

            # Simple AABB collision
            if (self.ball_x + BALL_SIZE >= bx and
                self.ball_x <= bx + BRICK_WIDTH and
                self.ball_y + BALL_SIZE >= by and
                self.ball_y <= by + BRICK_HEIGHT):

                # Deactivate brick
                brick[3] = False
                self.score += 10

                # Mark that brick needs to be erased
                self.needs_full_redraw = True

                # Bounce ball
                self.ball_dy = -self.ball_dy

                break  # Only hit one brick per frame

        # Check win condition
        active_bricks = sum(1 for b in self.bricks if b[3])
        if active_bricks == 0:
            self.won = True

    def draw(self):
        """Draw everything with partial updates to reduce flicker"""

        # Full redraw needed for bricks being destroyed or game state changes
        if self.needs_full_redraw:
            # Clear screen
            fb.fill(COLOR_BLACK)

            # Draw all bricks
            for brick in self.bricks:
                if brick[3]:  # Only draw active bricks
                    fb.fill_rect(brick[0], brick[1], BRICK_WIDTH, BRICK_HEIGHT, brick[2])

            # Draw score and lives
            fb.text(f"Score:{self.score}", 8, 8, COLOR_WHITE)
            fb.text(f"Lives:{self.lives}", SCREEN_WIDTH - 80, 8, COLOR_WHITE)

            self.needs_full_redraw = False
        else:
            # Partial update - only redraw moving elements

            # Erase previous paddle position if it moved
            if self.prev_paddle_x != self.paddle_x:
                fb.fill_rect(int(self.prev_paddle_x), PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT, COLOR_BLACK)

            # Erase previous ball position
            fb.fill_rect(int(self.prev_ball_x), int(self.prev_ball_y), BALL_SIZE, BALL_SIZE, COLOR_BLACK)

            # Update score if changed
            if self.prev_score != self.score:
                fb.fill_rect(8, 8, 80, 8, COLOR_BLACK)  # Clear old score
                fb.text(f"Score:{self.score}", 8, 8, COLOR_WHITE)
                self.prev_score = self.score

            # Update lives if changed
            if self.prev_lives != self.lives:
                fb.fill_rect(SCREEN_WIDTH - 80, 8, 80, 8, COLOR_BLACK)  # Clear old lives
                fb.text(f"Lives:{self.lives}", SCREEN_WIDTH - 80, 8, COLOR_WHITE)
                self.prev_lives = self.lives

        # Draw paddle at new position
        fb.fill_rect(int(self.paddle_x), PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT, COLOR_WHITE)

        # Draw ball at new position
        fb.fill_rect(int(self.ball_x), int(self.ball_y), BALL_SIZE, BALL_SIZE, COLOR_WHITE)

        # Store positions for next frame
        self.prev_paddle_x = self.paddle_x
        self.prev_ball_x = self.ball_x
        self.prev_ball_y = self.ball_y

        # Draw game over / win message
        if self.game_over:
            self.draw_centered_text("GAME OVER", 140, COLOR_RED)
            self.draw_centered_text("Press Q to quit", 160, COLOR_WHITE)
        elif self.won:
            self.draw_centered_text("YOU WIN!", 140, COLOR_GREEN)
            self.draw_centered_text(f"Score: {self.score}", 160, COLOR_YELLOW)
            self.draw_centered_text("Press Q to quit", 180, COLOR_WHITE)

    def draw_centered_text(self, text, y, color):
        """Draw text centered on screen"""
        x = (SCREEN_WIDTH - len(text) * 8) // 2
        fb.text(text, x, y, color)

def main():
    """Main game loop"""
    game = Game()

    # Title screen
    fb.fill(COLOR_BLACK)
    game.draw_centered_text("BREAKOUT", 100, COLOR_CYAN)
    game.draw_centered_text("Use Arrow Keys", 140, COLOR_WHITE)
    game.draw_centered_text("Press any key to start", 180, COLOR_YELLOW)
    time.sleep(2)
    # Wait for any key using keyboard.readinto
    temp = bytearray(1)
    while not keyboard.readinto(temp):
        pass

    # Game loop
    last_time = time.ticks_ms()
    frame_time = 1000 // 30  # 30 FPS

    while game.running:
        current_time = time.ticks_ms()

        # Check input
        game.check_input()

        # Update game state
        game.update()

        # Draw everything
        game.draw()

        # Frame timing
        elapsed = time.ticks_diff(current_time, last_time)
        if elapsed < frame_time:
            time.sleep_ms(frame_time - elapsed)
        last_time = current_time

    # Goodbye screen
    fb.fill(COLOR_BLACK)
    game.draw_centered_text("Thanks for playing!", 140, COLOR_CYAN)
    time.sleep(1)

    # Clear screen before returning to menu
    fb.fill(COLOR_BLACK)

# Run game
if __name__ == "__main__":
    main()
