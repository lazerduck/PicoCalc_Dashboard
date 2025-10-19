# tower_defense.py - Tower Defense game for PicoCalc
# Controls: Arrow keys to move cursor, ENTER to place tower/cycle tower type, Q to quit
import time
import picocalc
from picocalc import keyboard
import random

# Display setup
fb = picocalc.display
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 320

# Colors (using VT100 color indices)
COLOR_BG = 0          # Black
COLOR_BLUE = 1        # Blue
COLOR_RED = 2         # Red
COLOR_GREEN = 3       # Green/Teal
COLOR_CYAN = 4        # Bright Green (displayed as cyan)
COLOR_MAGENTA = 5     # Blue-Green
COLOR_YELLOW = 6      # Brown/Yellow
COLOR_WHITE = 7       # White

# Game constants
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE  # 16 cells
GRID_HEIGHT = (SCREEN_HEIGHT - 20) // GRID_SIZE  # 15 cells (reserve 20px for UI)

# Tower types
TOWER_BASIC = 0
TOWER_FAST = 1
TOWER_SPLASH = 2

# Tower properties: (cost, damage, fire_rate, range, name)
TOWER_PROPS = {
    TOWER_BASIC: (50, 20, 30, 2.5, "Basic"),
    TOWER_FAST: (40, 8, 10, 2.0, "Fast"),
    TOWER_SPLASH: (80, 15, 40, 2.0, "Splash"),
}

# Mob properties
MOB_HP_BASE = 30
MOB_SPEED_BASE = 0.5  # cells per update
MOB_REWARD = 15

class Mob:
    def __init__(self, wave_num, path):
        self.path = path
        self.path_idx = 0
        self.hp = MOB_HP_BASE + wave_num * 10
        self.max_hp = self.hp
        self.speed = MOB_SPEED_BASE + wave_num * 0.05
        self.reward = MOB_REWARD + wave_num * 5
        # Position on path (fractional)
        self.progress = 0.0
        self.alive = True
        self.reached_end = False
        
    def get_position(self):
        """Get current grid position"""
        if self.path_idx >= len(self.path):
            return self.path[-1]
        return self.path[self.path_idx]
    
    def update(self):
        """Move along the path"""
        if not self.alive:
            return
        
        self.progress += self.speed
        while self.progress >= 1.0 and self.path_idx < len(self.path) - 1:
            self.progress -= 1.0
            self.path_idx += 1
        
        if self.path_idx >= len(self.path) - 1 and self.progress >= 1.0:
            self.reached_end = True
            self.alive = False
    
    def take_damage(self, damage):
        """Apply damage to mob"""
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        cost, damage, fire_rate, range_val, name = TOWER_PROPS[tower_type]
        self.damage = damage
        self.fire_rate = fire_rate
        self.range = range_val
        self.name = name
        self.cooldown = 0
    
    def update(self):
        """Update tower cooldown"""
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def can_fire(self):
        """Check if tower can fire"""
        return self.cooldown == 0
    
    def fire(self, target):
        """Fire at target"""
        self.cooldown = self.fire_rate
        return self.damage
    
    def in_range(self, target_x, target_y):
        """Check if target is in range"""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        return dist <= self.range

class Game:
    def __init__(self):
        # Create path for mobs (snake pattern)
        self.path = self.create_path()
        
        # Game state
        self.money = 100
        self.lives = 20
        self.wave = 0
        self.score = 0
        
        # Game objects
        self.towers = []
        self.mobs = []
        self.projectiles = []
        
        # UI state
        self.cursor_x = 5
        self.cursor_y = 5
        self.selected_tower_type = TOWER_BASIC
        self.game_over = False
        self.won = False
        
        # Wave management
        self.wave_active = False
        self.mobs_spawned = 0
        self.mobs_to_spawn = 0
        self.spawn_timer = 0
        
        # Create occupied grid for tower placement
        self.occupied = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        for x, y in self.path:
            self.occupied[y][x] = True
    
    def create_path(self):
        """Create a snake-like path for mobs"""
        path = []
        # Start from left edge
        x, y = 0, 2
        path.append((x, y))
        
        # Move right
        for i in range(12):
            x += 1
            path.append((x, y))
        
        # Move down
        for i in range(3):
            y += 1
            path.append((x, y))
        
        # Move left
        for i in range(10):
            x -= 1
            path.append((x, y))
        
        # Move down
        for i in range(3):
            y += 1
            path.append((x, y))
        
        # Move right to exit
        for i in range(13):
            x += 1
            path.append((x, y))
        
        return path
    
    def start_wave(self):
        """Start a new wave"""
        if self.wave_active:
            return
        
        self.wave += 1
        self.wave_active = True
        self.mobs_to_spawn = 5 + self.wave * 3
        self.mobs_spawned = 0
        self.spawn_timer = 0
    
    def spawn_mob(self):
        """Spawn a new mob"""
        mob = Mob(self.wave, self.path)
        self.mobs.append(mob)
        self.mobs_spawned += 1
    
    def update(self):
        """Update game state"""
        if self.game_over or self.won:
            return
        
        # Check for wave completion
        if not self.wave_active and len(self.mobs) == 0:
            if self.wave >= 10:
                self.won = True
                return
        
        # Wave spawning
        if self.wave_active:
            if self.mobs_spawned < self.mobs_to_spawn:
                self.spawn_timer += 1
                if self.spawn_timer >= 30:  # Spawn every 30 frames
                    self.spawn_mob()
                    self.spawn_timer = 0
            elif len(self.mobs) == 0:
                self.wave_active = False
        
        # Update towers
        for tower in self.towers:
            tower.update()
            
            # Find target and fire
            if tower.can_fire():
                target = None
                for mob in self.mobs:
                    if mob.alive:
                        mx, my = mob.get_position()
                        if tower.in_range(mx, my):
                            target = mob
                            break
                
                if target:
                    damage = tower.fire(target)
                    
                    # Apply damage
                    if tower.type == TOWER_SPLASH:
                        # Splash damage to nearby mobs
                        tx, ty = target.get_position()
                        for mob in self.mobs:
                            if mob.alive:
                                mx, my = mob.get_position()
                                dx = mx - tx
                                dy = my - ty
                                dist = (dx * dx + dy * dy) ** 0.5
                                if dist <= 1.5:
                                    if mob.take_damage(damage):
                                        self.money += mob.reward
                                        self.score += mob.reward
                    else:
                        # Single target damage
                        if target.take_damage(damage):
                            self.money += target.reward
                            self.score += target.reward
        
        # Update mobs
        for mob in self.mobs[:]:
            mob.update()
            if mob.reached_end:
                self.lives -= 1
                self.mobs.remove(mob)
                if self.lives <= 0:
                    self.game_over = True
            elif not mob.alive:
                self.mobs.remove(mob)
    
    def place_tower(self, x, y, tower_type):
        """Try to place a tower at (x, y)"""
        # Check if valid position
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        
        if self.occupied[y][x]:
            return False
        
        # Check if can afford
        cost = TOWER_PROPS[tower_type][0]
        if self.money < cost:
            return False
        
        # Place tower
        tower = Tower(x, y, tower_type)
        self.towers.append(tower)
        self.occupied[y][x] = True
        self.money -= cost
        return True
    
    def handle_input(self):
        """Handle keyboard input"""
        temp = bytearray(10)
        if keyboard.readinto(temp):
            ch = temp[0]
            
            # Check for arrow keys (ANSI escape sequences)
            if ch == 27:  # ESC
                if temp[1] == 91:  # [
                    if temp[2] == 65:  # A - Up
                        self.cursor_y = max(0, self.cursor_y - 1)
                    elif temp[2] == 66:  # B - Down
                        self.cursor_y = min(GRID_HEIGHT - 1, self.cursor_y + 1)
                    elif temp[2] == 67:  # C - Right
                        self.cursor_x = min(GRID_WIDTH - 1, self.cursor_x + 1)
                    elif temp[2] == 68:  # D - Left
                        self.cursor_x = max(0, self.cursor_x - 1)
            elif ch == 13 or ch == 10:  # Enter
                self.place_tower(self.cursor_x, self.cursor_y, self.selected_tower_type)
            elif ch == 9:  # Tab - cycle tower type
                self.selected_tower_type = (self.selected_tower_type + 1) % 3
            elif ch == ord(' '):  # Space - start wave
                self.start_wave()
            elif ch == ord('q') or ch == ord('Q'):
                return False
        
        return True
    
    def draw(self):
        """Draw the game"""
        fb.fill(COLOR_BG)
        
        # Draw path
        for x, y in self.path:
            px = x * GRID_SIZE
            py = y * GRID_SIZE + 20
            fb.fill_rect(px, py, GRID_SIZE, GRID_SIZE, COLOR_YELLOW)
        
        # Draw towers
        for tower in self.towers:
            px = tower.x * GRID_SIZE + GRID_SIZE // 2 - 3
            py = tower.y * GRID_SIZE + 20 + GRID_SIZE // 2 - 3
            if tower.type == TOWER_BASIC:
                fb.fill_rect(px, py, 6, 6, COLOR_BLUE)
            elif tower.type == TOWER_FAST:
                fb.fill_rect(px, py, 6, 6, COLOR_GREEN)
            elif tower.type == TOWER_SPLASH:
                fb.fill_rect(px, py, 6, 6, COLOR_MAGENTA)
        
        # Draw mobs
        for mob in self.mobs:
            if mob.alive:
                mx, my = mob.get_position()
                px = mx * GRID_SIZE + GRID_SIZE // 2 - 3
                py = my * GRID_SIZE + 20 + GRID_SIZE // 2 - 3
                fb.fill_rect(px, py, 6, 6, COLOR_RED)
                
                # HP bar
                hp_pct = mob.hp / mob.max_hp
                bar_w = int(GRID_SIZE * 0.8 * hp_pct)
                if bar_w > 0:
                    bar_x = mx * GRID_SIZE + 2
                    bar_y = my * GRID_SIZE + 20 + 2
                    fb.fill_rect(bar_x, bar_y, bar_w, 2, COLOR_GREEN)
        
        # Draw cursor
        cx = self.cursor_x * GRID_SIZE
        cy = self.cursor_y * GRID_SIZE + 20
        fb.rect(cx, cy, GRID_SIZE, GRID_SIZE, COLOR_WHITE)
        
        # Draw UI
        cost = TOWER_PROPS[self.selected_tower_type][0]
        name = TOWER_PROPS[self.selected_tower_type][4]
        
        ui_text = "W:{} $:{} L:{}".format(
            self.wave, self.money, self.lives
        )
        fb.text(ui_text, 2, 2, COLOR_WHITE)
        
        # Draw tower info
        tower_info = "[{}:${}] TAB:Switch".format(name, cost)
        fb.text(tower_info, 2, 12, COLOR_CYAN)
        
        # Draw instructions
        if not self.wave_active and len(self.mobs) == 0:
            fb.text("SPACE: Start Wave", 180, 2, COLOR_YELLOW)
        
        # Game over / won
        if self.game_over:
            fb.text("GAME OVER!", 100, 150, COLOR_RED)
            fb.text("Score: {}".format(self.score), 110, 170, COLOR_WHITE)
        elif self.won:
            fb.text("YOU WIN!", 110, 150, COLOR_GREEN)
            fb.text("Score: {}".format(self.score), 110, 170, COLOR_WHITE)
        
        fb.show()

def main():
    """Main game loop"""
    game = Game()
    
    # Draw initial screen
    game.draw()
    time.sleep(0.5)
    
    running = True
    frame_time = 1.0 / 20  # 20 FPS
    
    while running:
        frame_start = time.ticks_ms()
        
        # Handle input
        if not game.handle_input():
            break
        
        # Update game
        game.update()
        
        # Draw
        game.draw()
        
        # Frame limiting
        elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
        sleep_time = frame_time - elapsed / 1000.0
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    # Show cursor on exit
    try:
        picocalc.terminal.wr("\x1b[?25h")
    except:
        pass

if __name__ == "__main__":
    main()
