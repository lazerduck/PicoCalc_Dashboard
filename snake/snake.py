# snake.py - Classic Snake game for PicoCalc
# Controls: Arrow keys to move, Q to quit
import time
import picocalc
from picocalc import keyboard
import random

# Display setup
fb = picocalc.display
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 320

# Colors
COLOR_BG = 0
COLOR_SNAKE = 3  # Green
COLOR_FOOD = 2   # Red
COLOR_TEXT = 7   # White
COLOR_GAME_OVER = 2

# Game constants
GRID_SIZE = 16  # Size of each grid cell
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 40) // GRID_SIZE  # Leave space for score
OFFSET_Y = 30  # Offset for score display

class Snake:
    def __init__(self):
        # Start in the middle
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)  # Moving right
        self.next_direction = (1, 0)
        self.growing = False
        
    def update(self):
        # Update direction (prevent 180-degree turns)
        if self.next_direction[0] != -self.direction[0] or self.next_direction[1] != -self.direction[1]:
            self.direction = self.next_direction
        
        # Calculate new head position
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check collision with walls
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
        
        # Check collision with self
        if new_head in self.body:
            return False
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Remove tail unless growing
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False
        
        return True
    
    def grow(self):
        self.growing = True
    
    def set_direction(self, direction):
        self.next_direction = direction

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        
    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake.body:
                return (x, y)
    
    def update(self):
        if self.game_over:
            return
        
        # Move snake
        if not self.snake.update():
            self.game_over = True
            return
        
        # Check if snake ate food
        if self.snake.body[0] == self.food:
            self.snake.grow()
            self.score += 10
            self.food = self.spawn_food()
    
    def draw(self):
        fb.fill(COLOR_BG)
        # Draw boundary wall
        wall_color = 1  # Blue
        x0 = 0
        y0 = OFFSET_Y
        x1 = GRID_WIDTH * GRID_SIZE
        y1 = OFFSET_Y + GRID_HEIGHT * GRID_SIZE
        # Top and bottom
        fb.fill_rect(x0, y0, x1, 2, wall_color)
        fb.fill_rect(x0, y1-2, x1, 2, wall_color)
        # Left and right
        fb.fill_rect(x0, y0, 2, y1-y0, wall_color)
        fb.fill_rect(x1-2, y0, 2, y1-y0, wall_color)

        # Draw score
        fb.text(f"Score: {self.score}", 10, 10, COLOR_TEXT)
        fb.text("Q: Quit", SCREEN_WIDTH - 70, 10, COLOR_TEXT)

        # Draw snake
        for segment in self.snake.body:
            x = segment[0] * GRID_SIZE
            y = segment[1] * GRID_SIZE + OFFSET_Y
            fb.fill_rect(x, y, GRID_SIZE - 1, GRID_SIZE - 1, COLOR_SNAKE)

        # Draw food
        fx = self.food[0] * GRID_SIZE
        fy = self.food[1] * GRID_SIZE + OFFSET_Y
        fb.fill_rect(fx, fy, GRID_SIZE - 1, GRID_SIZE - 1, COLOR_FOOD)

        # Draw game over message
        if self.game_over:
            fb.text("GAME OVER", 100, 140, COLOR_GAME_OVER)
            fb.text("Press Q to quit", 80, 160, COLOR_TEXT)

def main():
    game = Game()
    temp = bytearray(1)
    
    # Title screen
    fb.fill(COLOR_BG)
    fb.text("SNAKE", 130, 100, COLOR_TEXT)
    fb.text("Use Arrow Keys", 90, 140, COLOR_TEXT)
    fb.text("Press any key to start", 60, 180, COLOR_TEXT)
    time.sleep(2)
    
    # Wait for key
    while not keyboard.readinto(temp):
        pass
    
    # Game loop
    last_update = time.ticks_ms()
    update_interval = 150  # Move every 150ms
    
    running = True
    while running:
        current_time = time.ticks_ms()
        
        # Handle input (non-blocking)
        if keyboard.readinto(temp):
            key = temp[0]
            if key in (ord('q'), ord('Q')):
                running = False
            elif key == 65:  # Up
                game.snake.set_direction((0, -1))
            elif key == 66:  # Down
                game.snake.set_direction((0, 1))
            elif key == 67:  # Right
                game.snake.set_direction((1, 0))
            elif key == 68:  # Left
                game.snake.set_direction((-1, 0))
        
        # Update game at fixed interval
        if time.ticks_diff(current_time, last_update) >= update_interval:
            game.update()
            game.draw()
            last_update = current_time
            
            # Speed up as score increases
            update_interval = max(80, 150 - (game.score // 50) * 10)
        
        # If game over, wait for quit
        if game.game_over:
            game.draw()
            time.sleep(1)
            while running:
                if keyboard.readinto(temp):
                    key = temp[0]
                    if key in (ord('q'), ord('Q')):
                        running = False
                        break
                time.sleep_ms(50)
        
        time.sleep_ms(10)
    
    # Exit screen
    fb.fill(COLOR_BG)
    fb.text("Thanks for playing!", 80, 140, COLOR_TEXT)
    time.sleep(1)
    fb.fill(COLOR_BG)

if __name__ == "__main__":
    main()
