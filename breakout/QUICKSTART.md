# Breakout - Quick Reference

## 🎮 Controls
- **←** Move Left
- **→** Move Right  
- **Q** Quit

## 🎯 Quick Start
From dashboard: `Run App` → Select `breakout/breakout.py`

## ⚙️ Easy Tweaks

### Make it easier:
```python
PADDLE_WIDTH = 70        # Bigger paddle
BALL_SPEED_X = 2         # Slower ball
BALL_SPEED_Y = -2
self.lives = 5           # More lives
```

### Make it harder:
```python
PADDLE_WIDTH = 40        # Smaller paddle
BALL_SPEED_X = 4         # Faster ball
BALL_SPEED_Y = -4
BRICK_ROWS = 7           # More bricks
```

### Make it faster/slower:
```python
GAME_SPEED = 1.5  # 50% faster
GAME_SPEED = 0.7  # 30% slower
```

## 🎨 Add more brick rows:
```python
BRICK_ROWS = 6
colors = [COLOR_RED, COLOR_MAGENTA, COLOR_YELLOW, 
          COLOR_GREEN, COLOR_CYAN, COLOR_BLUE]
```

## 📊 Scoring
- Each brick: 10 points
- Max score (default): 400 points

## 🐛 Troubleshooting

**Paddle won't move?**
- Check if UART(0) is correct port
- Try different baud rate: `UART(0, 9600)`

**Too fast/slow?**
- Adjust `GAME_SPEED` constant
- Adjust frame rate in main loop

**Ball goes through paddle?**
- Ball speed too high
- Reduce BALL_SPEED_X/Y values

## 🎉 Have Fun!
