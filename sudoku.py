# sudoku.py - Sudoku game for PicoCalc
import time
import random
from ui import *
from battery import get_status as get_battery_status

def shuffle(lst):
    """Fisher-Yates shuffle for MicroPython."""
    for i in range(len(lst) - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]

class SudokuGame:
    def __init__(self, difficulty="medium"):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.given = [[False for _ in range(9)] for _ in range(9)]
        self.cursor_row = 0
        self.cursor_col = 0
        self.difficulty = difficulty
        self.start_time = time.time()
        self.completed = False
        
    def generate_puzzle(self):
        """Generate a new Sudoku puzzle."""
        # Try up to 3 times to generate a valid puzzle
        for attempt in range(3):
            # Reset grid
            self.grid = [[0 for _ in range(9)] for _ in range(9)]
            
            # First, generate a complete valid solution
            self._fill_diagonal_boxes()
            if not self._solve():
                continue  # Retry if solve failed
            
            # Successfully generated, break out
            break
        
        # Remove numbers based on difficulty
        clues = {"easy": 40, "medium": 32, "hard": 26}
        num_clues = clues.get(self.difficulty, 32)
        cells_to_remove = 81 - num_clues
        
        # Randomly remove cells
        removed = 0
        attempts = 0
        max_attempts = 200
        
        while removed < cells_to_remove and attempts < max_attempts:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            
            if self.grid[row][col] != 0:
                backup = self.grid[row][col]
                self.grid[row][col] = 0
                
                # Simple check: just remove it (proper unique solution check is complex)
                removed += 1
            
            attempts += 1
        
        # Mark given cells
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] != 0:
                    self.given[r][c] = True
    
    def _fill_diagonal_boxes(self):
        """Fill the three diagonal 3x3 boxes with random valid numbers."""
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            shuffle(nums)
            idx = 0
            for r in range(3):
                for c in range(3):
                    self.grid[box + r][box + c] = nums[idx]
                    idx += 1
    
    def _solve(self):
        """Solve the Sudoku using iterative backtracking (no recursion)."""
        # Find all empty cells
        empty_cells = []
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    empty_cells.append((r, c))
        
        if not empty_cells:
            return True
        
        # Iterative backtracking using a stack
        cell_idx = 0
        attempts = [0] * len(empty_cells)  # Track which number we're trying for each cell
        
        while 0 <= cell_idx < len(empty_cells):
            row, col = empty_cells[cell_idx]
            
            # Clear current cell
            self.grid[row][col] = 0
            
            # Try numbers from attempts[cell_idx] + 1 to 9
            found = False
            for num in range(attempts[cell_idx] + 1, 10):
                if self._is_valid(row, col, num):
                    self.grid[row][col] = num
                    attempts[cell_idx] = num
                    found = True
                    break
            
            if found:
                # Move to next cell
                cell_idx += 1
            else:
                # Backtrack
                attempts[cell_idx] = 0
                cell_idx -= 1
                
                # Safety check - if we backtracked too far, give up
                if cell_idx < 0:
                    return False
        
        return True
    
    def _find_empty(self):
        """Find an empty cell (0)."""
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return (r, c)
        return None
    
    def _is_valid(self, row, col, num):
        """Check if placing num at (row, col) is valid."""
        # Check row
        if num in self.grid[row]:
            return False
        
        # Check column
        for r in range(9):
            if self.grid[r][col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.grid[r][c] == num:
                    return False
        
        return True
    
    def get_conflicts(self, row, col):
        """Get list of conflicting cells for the cell at (row, col)."""
        if self.grid[row][col] == 0:
            return []
        
        num = self.grid[row][col]
        conflicts = []
        
        # Check row
        for c in range(9):
            if c != col and self.grid[row][c] == num:
                conflicts.append((row, c))
        
        # Check column
        for r in range(9):
            if r != row and self.grid[r][col] == num:
                conflicts.append((r, col))
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and self.grid[r][c] == num:
                    conflicts.append((r, c))
        
        return conflicts
    
    def is_complete(self):
        """Check if puzzle is complete and valid."""
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return False
                if self.get_conflicts(r, c):
                    return False
        return True
    
    def set_cell(self, row, col, num):
        """Set a cell value if it's not a given cell."""
        if not self.given[row][col]:
            self.grid[row][col] = num

def draw_sudoku(game):
    """Draw the Sudoku grid and numbers."""
    clear()
    
    # Grid parameters - centered on screen
    grid_size = 315
    cell_size = 35
    grid_x = 2
    grid_y = 2  # Start at top of screen
    
    # Draw grid lines
    for i in range(10):
        thickness = 2 if i % 3 == 0 else 1
        color = COLOR_WHITE
        
        # Vertical lines
        x = grid_x + i * cell_size
        for t in range(thickness):
            fb.vline(x + t, grid_y, grid_size, color)
        
        # Horizontal lines
        y = grid_y + i * cell_size
        for t in range(thickness):
            fb.hline(grid_x, y + t, grid_size, color)
    
    # Highlight selected cell's row, column, and box
    sel_row, sel_col = game.cursor_row, game.cursor_col
    
    # Highlight row
    y = grid_y + sel_row * cell_size + 1
    fb.fill_rect(grid_x + 1, y, grid_size - 2, cell_size - 1, COLOR_BLUE)
    
    # Highlight column
    x = grid_x + sel_col * cell_size + 1
    fb.fill_rect(x, grid_y + 1, cell_size - 1, grid_size - 2, COLOR_BLUE)
    
    # Highlight 3x3 box
    box_row, box_col = 3 * (sel_row // 3), 3 * (sel_col // 3)
    bx = grid_x + box_col * cell_size + 1
    by = grid_y + box_row * cell_size + 1
    fb.fill_rect(bx, by, 3 * cell_size - 1, 3 * cell_size - 1, COLOR_BLUE)
    
    # Redraw grid lines over highlights
    for i in range(10):
        thickness = 2 if i % 3 == 0 else 1
        color = COLOR_WHITE
        x = grid_x + i * cell_size
        for t in range(thickness):
            fb.vline(x + t, grid_y, grid_size, color)
        y = grid_y + i * cell_size
        for t in range(thickness):
            fb.hline(grid_x, y + t, grid_size, color)
    
    # Draw numbers (with black background to ensure they're visible over highlights)
    for r in range(9):
        for c in range(9):
            num = game.grid[r][c]
            if num != 0:
                x = grid_x + c * cell_size + 12
                y = grid_y + r * cell_size + 12
                
                # Determine color
                if game.given[r][c]:
                    color = COLOR_WHITE  # Given numbers: light gray/white
                elif game.get_conflicts(r, c):
                    color = COLOR_RED  # Conflicts: red
                else:
                    color = COLOR_CYAN  # Player numbers: bright green (cyan is actually green on this display)
                
                # Draw with explicit black background to cover blue highlights
                draw_text(str(num), x, y, color, COLOR_BLACK)
    
    # Highlight selected cell
    x = grid_x + sel_col * cell_size
    y = grid_y + sel_row * cell_size
    draw_rect(x + 1, y + 1, cell_size - 2, cell_size - 2, COLOR_YELLOW, fill=False)
    draw_rect(x + 2, y + 2, cell_size - 4, cell_size - 4, COLOR_YELLOW, fill=False)
    
    # Show info below grid
    info_y = grid_y + grid_size + 2
    
    # Show timer and difficulty on one line
    elapsed = int(time.time() - game.start_time)
    mins = elapsed // 60
    secs = elapsed % 60
    timer_text = f"{mins:02d}:{secs:02d}"
    diff_text = f"{game.difficulty[0].upper()}{game.difficulty[1:]}"
    
    draw_text(diff_text, 4, info_y, COLOR_CYAN)  # Bright green
    draw_text(timer_text, 280, info_y, COLOR_CYAN)  # Bright green
    
    # Help text (compact, no room for full text)
    # Leave blank or minimal - players will learn controls

def select_difficulty():
    """Show difficulty selection menu."""
    options = ["Easy", "Medium", "Hard"]
    selected = 1  # Default to medium
    
    while True:
        clear()
        draw_text("Select Difficulty", 8, 60, COLOR_CYAN)
        draw_line_horizontal(80, 0, 320, COLOR_WHITE)
        
        for i, opt in enumerate(options):
            y = 120 + i * 30
            draw_menu_item(opt, 12, y, selected=(i == selected))
        
        draw_text("UP/DOWN: Select | ENTER: Start | Q: Cancel", 8, 290, COLOR_YELLOW)
        
        key = wait_key_raw()
        if key == 'A':
            selected = (selected - 1) % len(options)
        elif key == 'B':
            selected = (selected + 1) % len(options)
        elif key in ('\r', '\n'):
            return options[selected].lower()
        elif key in ('q', 'Q'):
            return None

def play_sudoku():
    """Main Sudoku game loop."""
    # Select difficulty
    difficulty = select_difficulty()
    if not difficulty:
        return
    
    # Show generating message
    clear()
    center_text("Generating puzzle...", 140, COLOR_YELLOW)
    center_text("Please wait...", 160, COLOR_WHITE)
    
    # Create and generate puzzle
    game = SudokuGame(difficulty)
    game.generate_puzzle()
    
    # Game loop
    running = True
    while running:
        draw_sudoku(game)
        
        # Check if completed
        if game.is_complete() and not game.completed:
            game.completed = True
            elapsed = int(time.time() - game.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            
            clear()
            center_text("Congratulations!", 120, COLOR_GREEN)
            center_text("Puzzle Complete!", 150, COLOR_GREEN)
            center_text(f"Time: {mins:02d}:{secs:02d}", 180, COLOR_CYAN)
            draw_text("Press any key to continue...", 8, 290, COLOR_YELLOW)
            wait_key_raw()
            return
        
        key = wait_key_raw()
        
        if key == 'A':  # Up
            game.cursor_row = (game.cursor_row - 1) % 9
        elif key == 'B':  # Down
            game.cursor_row = (game.cursor_row + 1) % 9
        elif key == 'D':  # Left
            game.cursor_col = (game.cursor_col - 1) % 9
        elif key == 'C':  # Right
            game.cursor_col = (game.cursor_col + 1) % 9
        elif key in '123456789':
            num = int(key)
            game.set_cell(game.cursor_row, game.cursor_col, num)
        elif key in ('0', '\x7f', '\x08'):  # 0, delete, backspace
            game.set_cell(game.cursor_row, game.cursor_col, 0)
        elif key in ('q', 'Q'):
            running = False
        
        time.sleep(0.01)

if __name__ == "__main__":
    play_sudoku()
