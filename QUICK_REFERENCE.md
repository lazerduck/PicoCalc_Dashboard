# QUICK_REFERENCE.md - Quick Reference Card

## 🚀 Quick Start

```python
import sys
sys.path.append('/sd/new')
from menu import main
main()
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| ↑ (A) | Navigate Up |
| ↓ (B) | Navigate Down |
| Enter | Select / Confirm |
| Q | Quick Quit / Cancel |

## 📁 Module Overview

```python
# Battery Module
from battery import get_status, get_percentage, get_voltage

status = get_status()  # Complete battery info
pct = get_percentage()  # Just percentage
v = get_voltage()      # Just voltage

# UI Module
from ui import *

clear()                                    # Clear screen
draw_text("Hello", 10, 10, COLOR_GREEN)   # Draw text
center_text("Centered", 100, COLOR_WHITE) # Center text
draw_battery_status(x, y, battery_status) # Battery icon
draw_progress_bar(x, y, w, h, pct, color) # Progress bar
key = wait_key_raw()                      # Wait for keypress

# File Selector
from fileselect import select_file

path = select_file(path="/sd", exts=(".py",), 
                   title="Select File", return_full_path=True)

# App Launcher
from loadapp import run_app
run_app()

# Music Player
from play import play_music_file
play_music_file()
```

## 🎨 Colors

```python
COLOR_BLACK = 0    # Background
COLOR_BLUE = 1     # Accents
COLOR_RED = 2      # Errors, Low Battery
COLOR_GREEN = 3    # Success, High Battery
COLOR_CYAN = 4     # USB Power, Info
COLOR_MAGENTA = 5  # Reserved
COLOR_YELLOW = 6   # Selected, Warnings
COLOR_WHITE = 7    # Normal Text
```

## 🔋 Battery Status

```python
status = get_status()

# Returns:
{
  'voltage': 3.87,        # Volts
  'voltage_mv': 3870,     # Millivolts
  'percentage': 65,       # 0-100 (None if USB)
  'usb_power': False,     # True if on USB
  'status': 'Good'        # Full/Good/Low/Critical/USB Power
}
```

## 📏 Screen Layout

```
Screen: 320x320 pixels
Font: 8x8 pixels per character
Max chars per line: 40 (36 recommended with margins)

Standard Layout:
┌─────────────────────────────┐
│ Title [Battery Icon] XX%    │ y: 0-24
├─────────────────────────────┤ y: 24 (separator)
│                             │
│ Content Area                │ y: 32-280
│                             │
│ Help Text                   │ y: 290-310
└─────────────────────────────┘
```

## 🔧 Common Tasks

### Display Battery Percentage
```python
from battery import get_percentage
pct = get_percentage()
print(f"Battery: {pct}%")
```

### Show Custom Screen
```python
from ui import *
from battery import get_status

clear()
battery = get_status()
draw_title_bar("My Screen", battery)
center_text("Hello World!", 100, COLOR_CYAN)
wait_key_raw()
```

### Select and Load File
```python
from fileselect import select_file

path = select_file(path="/sd", exts=(".py",))
if path:
    with open(path) as f:
        code = f.read()
    exec(code)
```

### Draw Progress Bar
```python
from ui import draw_progress_bar, COLOR_GREEN

# Draw 75% full green bar
draw_progress_bar(x=10, y=100, width=200, height=20, 
                  percentage=75, color=COLOR_GREEN)
```

## 🎯 Menu Options

1. **Open REPL** → Exit to MicroPython
2. **Memory Stats** → View RAM usage
3. **Battery Status** → Detailed battery info
4. **Servo Control** → Control up to 6 servos simultaneously
5. **GPIO Control** → Configure GP2, GP3, GP4, GP5, GP21, GP28
6. **File Manager** → Browse, rename, delete files and create folders
7. **Run App** → Browse/run .py files
8. **Edit File** → Open text editor
9. **Play Music** → Browse/play .mp3 files
10. **Power Off / Reset** → System controls

### GPIO Control Keys
- UP/DOWN: Select a GPIO row
- LEFT/RIGHT: Cycle mode (IN → OUT → PWM)
- ENTER: Toggle OUT (on/off)
- + / -: Increase/decrease PWM duty
- Q: Exit

### Servo Control Keys
- UP/DOWN: Select a servo
- LEFT/RIGHT: Adjust angle (-5° / +5°)
- Q: Exit

### File Manager Keys
- UP/DOWN: Navigate files/folders
- ENTER: Show action menu (Rename, Delete)
- RIGHT: Navigate into folder
- LEFT: Go up to parent directory
- N: Create new folder
- Q: Exit

## 🐛 Troubleshooting

### Battery shows "--"
```python
# Debug voltage reading
from battery import BatteryMonitor
m = BatteryMonitor()
print(f"Raw: {m.vsys_adc.read_u16()}")
print(f"Voltage: {m.read_vsys_voltage()}V")
```

### Display not updating
```python
# Force display update (if available)
import picocalc
picocalc.display.show()  # Or similar
```

### Import errors on PC
- Normal! Code is for PicoCalc hardware
- `picocalc`, `mp3`, etc. only exist on device

### File not found
```python
# List files
import os
print(os.listdir('/sd'))
```

## 📊 Battery Charge Levels

| Icon Color | Percentage | Status |
|-----------|-----------|--------|
| 🟢 Green | > 50% | Good |
| 🟡 Yellow | 20-50% | Medium |
| 🔴 Red | < 20% | Low |
| 🔵 Cyan | N/A | USB Power |

## 💾 File Upload Commands

```bash
# Upload entire folder
mpremote connect COM4 fs cp -r new/ :/sd/new/

# Upload single file
mpremote connect COM4 fs cp new/menu.py :/sd/new/menu.py

# List files on device
mpremote connect COM4 fs ls /sd/new

# Enter REPL
mpremote connect COM4
```

## 🧪 Testing

```python
# Run all tests
import sys
sys.path.append('/sd/new')
import test_dashboard
test_dashboard.test_all()

# Test individual modules
test_dashboard.test_battery()
test_dashboard.test_ui()
test_dashboard.test_fileselect()
test_dashboard.test_menu()
```

## 📖 Documentation Files

- **README.md** - Full documentation & API reference
- **SETUP.md** - Installation & configuration guide
- **VISUAL_GUIDE.md** - UI layouts & design specs
- **PROJECT_SUMMARY.md** - Complete project overview
- **QUICK_REFERENCE.md** - This file

## 🎓 Tips

1. **Always import from correct path:**
   ```python
   import sys
   sys.path.append('/sd/new')
   ```

2. **Clear screen before drawing:**
   ```python
   from ui import clear
   clear()
   ```

3. **Handle errors gracefully:**
   ```python
   try:
       # Your code
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **Collect garbage regularly:**
   ```python
   import gc
   gc.collect()
   ```

5. **Check battery before intensive tasks:**
   ```python
   from battery import get_percentage
   if get_percentage() < 20:
       print("Low battery warning!")
   ```

## 🔗 Quick Links

| File | Purpose |
|------|---------|
| `menu.py` | Main entry point |
| `ui.py` | UI components |
| `battery.py` | Battery monitoring |
| `fileselect.py` | File browser |
| `loadapp.py` | App launcher |
| `play.py` | Music player |
| `test_dashboard.py` | Test suite |

---

**Need more help?** Check README.md or SETUP.md for detailed information.
