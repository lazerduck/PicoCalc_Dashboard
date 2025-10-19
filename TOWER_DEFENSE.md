# Tower Defense Game

A tower defense game for PicoCalc where you defend against waves of enemies by strategically placing towers.

## How to Play

### Objective
Survive 10 waves of enemies by placing towers to defend your base. If too many enemies reach the end of the path, you lose!

### Controls
- **Arrow Keys**: Move cursor to select where to place towers
- **ENTER**: Place the currently selected tower at cursor position
- **TAB**: Cycle through different tower types
- **SPACE**: Start the next wave
- **Q**: Quit game

### Tower Types

#### 1. Basic Tower (Blue) - $50
- **Damage**: 20
- **Fire Rate**: Medium (30 frames)
- **Range**: 2.5 cells
- **Best for**: Balanced defense, general purpose

#### 2. Fast Tower (Green) - $40
- **Damage**: 8
- **Fire Rate**: Fast (10 frames)
- **Range**: 2.0 cells
- **Best for**: Quick attacks, early waves, cost-effective

#### 3. Splash Tower (Magenta) - $80
- **Damage**: 15 (to all nearby enemies)
- **Fire Rate**: Slow (40 frames)
- **Range**: 2.0 cells, 1.5 cell splash radius
- **Best for**: Grouped enemies, choke points

### Game Mechanics

#### Starting Resources
- **Money**: $100
- **Lives**: 20

#### Waves
- 10 waves total to win
- Each wave spawns more enemies (5 + wave × 3)
- Enemies get stronger each wave:
  - HP increases by 10 per wave
  - Speed increases slightly per wave
  - Reward increases by $5 per wave

#### Money System
- Earn money by destroying enemies
- Base reward: $15 + $5 per wave level
- Use money to build towers
- No refunds for towers!

#### Strategy Tips
1. **Start with Fast Towers**: They're cheap and effective early on
2. **Place at corners**: Enemies spend more time in range
3. **Use Splash Towers wisely**: Great at choke points where enemies bunch up
4. **Don't overspend**: Always keep some money for the next wave
5. **Plan ahead**: Each wave gets harder, so upgrade your defense gradually

### Display Information

**Top Bar**:
- `W:X` - Current wave number
- `$:X` - Current money
- `L:X` - Lives remaining

**Second Line**:
- Current tower type and cost
- `TAB:Switch` - Reminder to switch tower types

**Visual Elements**:
- **Yellow path**: Where enemies walk
- **Blue squares**: Basic towers
- **Green squares**: Fast towers
- **Magenta squares**: Splash towers
- **Red squares**: Enemies
- **White square**: Cursor for tower placement
- **Green bars**: Enemy health

## Winning and Losing

- **Win**: Survive all 10 waves!
- **Lose**: Run out of lives (enemies reaching the end)

## Technical Details

- **Display**: 320×320 pixels
- **Grid**: 16×15 cells (20px each)
- **Frame Rate**: ~20 FPS
- **Path**: Pre-defined snake pattern

## File Location

Place `tower_defense.py` in your PicoCalc `/sd` directory and run it via the "Run App" menu option.
