# PicoCalc Dashboard - New UI System

A complete dashboard interface for the PicoCalc with battery monitoring, file management, and app launcher.

## Features

### 🔋 Battery Monitoring
- **Real-time voltage monitoring** via VSYS ADC
- **Visual battery icon** with percentage fill
- **Color-coded status**:
  - 🟢 Green: >50% charge
  - 🟡 Yellow: 20-50% charge
  - 🔴 Red: <20% charge
  - 🔵 Cyan: USB powered
- **USB power detection** (VSYS > 4.5V)
- **Detailed battery page** with voltage, percentage, and status

### 📱 Dashboard Menu
1. **Open REPL** - Exit to MicroPython REPL
2. **Memory Stats** - View RAM usage with visual bar graph
3. **Battery Status** - Detailed battery information
4. **Run App** - Browse and execute Python apps from /sd
5. **Edit File** - Open files in the built-in editor
6. **Play Music** - Browse and play MP3 files from /sd
7. **Power Off / Reset** - System power controls

### 🎨 UI Components
- **320x320 display** optimized layout
- **Battery icon** in title bar (26x12px with terminal bump)
- **Color-coded interface** for easy status recognition
- **Arrow key navigation** (UP/DOWN) with Enter to select
- **Scrollable file browser** for long file lists

## File Structure

```
new/
├── menu.py          # Main dashboard and menu system
├── ui.py            # UI components (battery icon, text, drawing)
├── battery.py       # Battery monitoring module
├── fileselect.py    # File browser/selector
├── loadapp.py       # App loader
├── play.py          # Music player
└── README.md        # This file
```

## Hardware Requirements

- **Raspberry Pi Pico 2** (or compatible)
- **2x 18650 Li-ion batteries** in parallel (7600mAh total)
- **PicoCalc hardware** with:
  - 320x320 display
  - VSYS ADC connection (GPIO29 / ADC3)
  - MP3 playback hardware (optional, for music player)

## Battery Specifications

- **Chemistry**: Li-ion 18650
- **Configuration**: 2S parallel (7600mAh)
- **Voltage Range**: 3.0V - 4.2V per cell
- **USB Detection**: VSYS > 4.5V
- **Percentage Calculation**: Based on voltage discharge curve

### Voltage-to-Percentage Mapping

| Voltage | Percentage |
|---------|-----------|
| 4.2V    | 100%      |
| 4.0V    | 90%       |
| 3.9V    | 80%       |
| 3.8V    | 60%       |
| 3.7V    | 40%       |
| 3.6V    | 20%       |
| 3.4V    | 10%       |
| 3.0V    | 0%        |

## Usage

### Running the Dashboard

```python
# On PicoCalc, run:
import sys
sys.path.append('/sd/new')  # If files are in /sd/new
from menu import main
main()
```

Or set as boot script by adding to `main.py`:

```python
import sys
sys.path.append('/sd/new')
import menu
menu.main()
```

### Using Individual Modules

#### Battery Module
```python
from battery import get_status, get_percentage, get_voltage

# Get complete status
status = get_status()
print(status)
# {'voltage': 3.87, 'voltage_mv': 3870, 'percentage': 65, 
#  'usb_power': False, 'status': 'Good'}

# Quick percentage check
pct = get_percentage()
print(f"Battery: {pct}%")

# Just voltage
v = get_voltage()
print(f"Voltage: {v}V")
```

#### File Selector
```python
from fileselect import select_file

# Select a Python file
path = select_file(path="/sd", exts=(".py",), title="Choose file")

# Select any file
path = select_file(path="/sd", exts=None, title="Choose any file")

# Get just filename (not full path)
name = select_file(path="/sd", return_full_path=False)
```

#### UI Components
```python
from ui import *

# Clear screen
clear()

# Draw text
draw_text("Hello!", 10, 10, COLOR_GREEN)
center_text("Centered!", 100, COLOR_YELLOW)

# Draw battery icon
battery_status = get_battery_status()
draw_battery_status(10, 10, battery_status)

# Draw progress bar
draw_progress_bar(10, 50, 200, 20, 75, COLOR_GREEN)
```

## Controls

- **Arrow Keys**:
  - `UP` (A): Navigate up
  - `DOWN` (B): Navigate down
- **Enter** (`\r` or `\n`): Select/Confirm
- **Q**: Quick quit/cancel

## Customization

### Changing Battery Thresholds

Edit `battery.py`:

```python
# Modify voltage thresholds
self.VOLTAGE_MAX = 4.2  # Fully charged
self.VOLTAGE_MIN = 3.0  # Critically low
self.USB_THRESHOLD = 4.5  # USB detection
```

### Adjusting Color Scheme

Edit `ui.py` color constants:

```python
COLOR_BLACK = 0
COLOR_BLUE = 1
COLOR_RED = 2
COLOR_GREEN = 3
COLOR_CYAN = 4
COLOR_MAGENTA = 5
COLOR_YELLOW = 6
COLOR_WHITE = 7
```

### Modifying Menu Items

Edit `menu.py` in `show_main_menu()`:

```python
menu_items = [
    ("Your Item", "your_code"),
    # ...
]
```

Then add handler in `main()`:

```python
elif choice == "your_code":
    your_function()
```

## Troubleshooting

### Battery Percentage Shows "--"
- Check VSYS ADC connection
- Verify GPIO29 is connected to VSYS
- Check if USB is connected (percentage disabled on USB)

### Import Errors
- Ensure all files are in same directory or adjust `sys.path`
- Verify file names match imports exactly

### Display Issues
- Verify screen is 320x320
- Check `picocalc.display` is available
- Some builds may not support background colors

### Music Playback Fails
- Check `mp3` module is available in your firmware
- Verify MP3 hardware is connected (pins 26, 27)
- Ensure UART0 is available (115200 baud)

## Development

### Adding New Features

1. Add UI components to `ui.py`
2. Create new module for functionality
3. Add menu item in `menu.py`
4. Import and call in main loop

### Testing Battery Module

```python
from battery import BatteryMonitor

monitor = BatteryMonitor()
v = monitor.read_vsys_voltage()
pct = monitor.voltage_to_percentage(v)
print(f"Voltage: {v}V = {pct}%")
```

## License

This code is designed for the PicoCalc platform. Modify and use as needed for your project.

## Credits

Created for PicoCalc - Raspberry Pi Pico 2 based calculator platform.
