# Breakout Game for PicoCalc

A simple but colorful Breakout clone for the PicoCalc!

## 🎮 How to Play

### **Objective**
Break all the colored bricks by bouncing the ball with your paddle. Don't let the ball fall off the bottom!

### **Controls**
- **← Left Arrow** - Move paddle left
- **→ Right Arrow** - Move paddle right  
- **Q** - Quit game

### **Gameplay**
- You have **3 lives**
- Each brick destroyed gives you **10 points**
- Ball bounces off walls, paddle, and bricks
- Hitting the paddle at different positions adds "spin" to the ball
- Game ends when you lose all lives or clear all bricks

## 🎨 Features

- **5 rows of colored bricks** (Red, Magenta, Yellow, Green, Cyan)
- **Score tracking**
- **Lives system**
- **Paddle spin mechanic** - hit the ball with the edge of the paddle to angle it
- **Smooth 30 FPS gameplay**
- **Win/Lose screens**

## 🚀 Running the Game

### From PicoCalc Dashboard Menu:
1. Navigate to "Run App"
2. Select `breakout/breakout.py`
3. Press Enter

### From REPL:
```python
import sys
sys.path.append('/sd/new/breakout')
import breakout
breakout.main()
```

### Standalone:
```python
exec(open('/sd/new/breakout/breakout.py').read())
```

## 🎯 Game Stats

- **Screen**: 320x320 pixels
- **Paddle**: 50x8 pixels
- **Ball**: 6x6 pixels
- **Bricks**: 8 columns × 5 rows (40 total)
- **Starting Lives**: 3
- **Frame Rate**: 30 FPS

## 🛠️ Technical Details

### Game Loop
```
Input Check → Update Physics → Draw Frame (partial update) → Wait for next frame
```

### Anti-Flicker Optimization
To reduce flicker on SPI displays:
- **Partial screen updates** - Only redraws moving elements (ball, paddle)
- **Full redraw only when needed** - Bricks destroyed, lives lost
- **Erase-then-draw** - Clears old position before drawing new
- **30 FPS cap** - Prevents excessive redrawing

### Collision Detection
- **Wall collision**: Simple boundary checks
- **Paddle collision**: AABB (Axis-Aligned Bounding Box)
- **Brick collision**: AABB with one brick per frame

### Paddle Spin
When the ball hits the paddle:
- Center hit: Ball goes straight up
- Edge hit: Ball angles left/right (up to ±3 pixels per frame)

## 🎨 Color Scheme

| Row | Color   | Code |
|-----|---------|------|
| 1   | Red     | 2    |
| 2   | Magenta | 5    |
| 3   | Yellow  | 6    |
| 4   | Green   | 3    |
| 5   | Cyan    | 4    |

## 🐛 Known Limitations

- Input uses `select.select()` which may not work on all MicroPython builds
- If arrow keys don't work, the game may need input system adjustments
- No sound effects (hardware limitation)
- No save/load high scores (could be added)

## 🔧 Customization

Want to modify the game? Edit these constants in `breakout.py`:

```python
# Make paddle bigger/smaller
PADDLE_WIDTH = 50

# Change ball speed
BALL_SPEED_X = 3
BALL_SPEED_Y = -3

# Adjust difficulty
BRICK_ROWS = 5  # More rows = harder

# Starting lives
self.lives = 3
```

## 📊 Scoring

- Break a brick: **+10 points**
- Clear all bricks: **WIN!**
- Lose all lives: **GAME OVER**

Max possible score: **400 points** (40 bricks × 10 points)

## 🎮 Tips & Tricks

1. **Use the edges** - Hit the ball with paddle edges to angle shots
2. **Stay centered** - Keep paddle in middle for better control
3. **Watch the angle** - Ball bounces predictably, plan ahead
4. **Corner shots** - Angle the ball to hit hard-to-reach bricks

## 🚧 Future Enhancements (Ideas)

- Power-ups (multi-ball, wider paddle, laser)
- Multiple levels with different brick patterns
- Difficulty settings (ball speed, lives)
- High score tracking
- Sound effects (if hardware supports)
- Particle effects for brick destruction

## 📝 File Structure

```
breakout/
└── breakout.py    # Main game file (~240 lines)
```

## 🎉 Enjoy!

Have fun breaking those bricks! 🧱💥
