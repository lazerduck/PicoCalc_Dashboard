# SETUP.md - Installation and Setup Guide

## Quick Start

### 1. Upload Files to PicoCalc

Upload all files from the `new/` folder to your PicoCalc's `/sd/new/` directory:

```
/sd/new/
├── battery.py
├── fileselect.py
├── loadapp.py
├── menu.py
├── play.py
├── ui.py
├── test_dashboard.py
├── README.md
├── SETUP.md
└── VISUAL_GUIDE.md
```

### 2. Test the Installation

Connect to your PicoCalc's REPL and run:

```python
import sys
sys.path.append('/sd/new')

# Run the test suite
import test_dashboard
test_dashboard.test_all()
```

This will verify:
- Battery module can read VSYS voltage
- UI components render correctly
- File selector works
- Menu system imports properly

### 3. Launch the Dashboard

If tests pass, launch the dashboard:

```python
from menu import main
main()
```

### 4. Set as Boot Script (Optional)

To make the dashboard launch automatically on boot, create or edit `/sd/main.py`:

```python
# /sd/main.py - PicoCalc boot script
import sys
sys.path.append('/sd/new')

try:
    from menu import main
    main()
except Exception as e:
    print("Dashboard failed to start:")
    print(e)
    import sys
    sys.print_exception(e)
```

## Detailed Setup

### Prerequisites

**Hardware:**
- Raspberry Pi Pico 2 (or Pico W)
- PicoCalc board with:
  - 320x320 display
  - 2x 18650 batteries (parallel)
  - VSYS connected to ADC
  - Optional: MP3 playback hardware

**Firmware:**
- MicroPython 1.20+ (or custom PicoCalc firmware)
- `picocalc` module available
- `machine`, `gc`, `sys`, `os` modules

**Optional Modules:**
- `mp3` module (for music playback)
- `vtterminal` module (for music playback)
- Built-in `edit()` function (for file editor)

### File Upload Methods

#### Method 1: Using mpremote (Recommended)

```bash
# Upload entire new/ folder
mpremote connect COM4 fs cp -r new/ :/sd/new/

# Or upload files individually
mpremote connect COM4 fs cp new/menu.py :/sd/new/menu.py
mpremote connect COM4 fs cp new/ui.py :/sd/new/ui.py
mpremote connect COM4 fs cp new/battery.py :/sd/new/battery.py
# ... etc
```

#### Method 2: Using Thonny

1. Open Thonny IDE
2. Connect to PicoCalc
3. Create `/sd/new/` folder
4. Upload each file to `/sd/new/`

#### Method 3: Using rshell

```bash
rshell -p COM4
> mkdir /sd/new
> cp new/*.py /sd/new/
> exit
```

### Configuration

#### Adjust Battery Parameters

Edit `/sd/new/battery.py` if your battery setup differs:

```python
# Battery capacity (if not 2x 18650 @ 3800mAh each)
# This is informational only, doesn't affect calculations

# Voltage thresholds
self.VOLTAGE_MAX = 4.2  # Max cell voltage
self.VOLTAGE_MIN = 3.0  # Min safe voltage
self.USB_THRESHOLD = 4.5  # USB detection threshold

# Voltage divider ratio (hardware dependent)
self.VSYS_DIVIDER = 3.0  # Pico default is 3:1
```

#### Customize Menu

Edit `/sd/new/menu.py` to add/remove menu items:

```python
def show_main_menu(battery_status):
    menu_items = [
        ("Your Custom Item", "custom"),
        # Add more items here
    ]
    # ...

def main():
    # ...
    elif choice == "custom":
        your_custom_function()
```

#### Change Colors

Edit `/sd/new/ui.py` if your display uses different color values:

```python
# Standard 3-bit color palette (0-7)
COLOR_BLACK = 0
COLOR_BLUE = 1
COLOR_RED = 2
COLOR_GREEN = 3
COLOR_CYAN = 4
COLOR_MAGENTA = 5
COLOR_YELLOW = 6
COLOR_WHITE = 7
```

## Troubleshooting

### "Import picocalc could not be resolved"

**Issue:** The `picocalc` module is specific to PicoCalc firmware and won't be available in standard MicroPython.

**Solution:** These import errors are expected when editing on a PC. The code will work on actual PicoCalc hardware.

### Battery shows "--" or incorrect values

**Possible causes:**
1. VSYS not connected to GPIO29
2. Incorrect voltage divider ratio
3. USB cable connected (disables percentage)

**Debug:**
```python
from battery import BatteryMonitor
monitor = BatteryMonitor()
raw = monitor.vsys_adc.read_u16()
voltage = monitor.read_vsys_voltage()
print(f"Raw ADC: {raw}, Voltage: {voltage}V")
```

Expected values:
- Battery: 3.0-4.2V
- USB: ~5V (or higher)

### Display not updating

**Check:**
1. Screen resolution is 320x320
2. `picocalc.display` is available
3. Framebuffer methods exist (`fill`, `text`, `fill_rect`)

**Test:**
```python
import picocalc
fb = picocalc.display
fb.fill(0)  # Clear to black
fb.text("Test", 10, 10, 7)  # White text
```

### File selector shows no files

**Check:**
1. SD card is mounted at `/sd`
2. Files exist in the target directory
3. File extensions match filter

**Debug:**
```python
import os
print(os.listdir('/sd'))  # List all files
```

### Music player fails

**Requirements:**
- `mp3` module in firmware
- MP3 hardware connected (pins 26, 27)
- UART0 available

**Test:**
```python
import mp3
mp3.init(pin_l=26, pin_r=27)
print("MP3 module OK")
```

### Editor crashes

The built-in `edit()` function must be available in your firmware. If not available:

**Option 1:** Use alternative editor
- Install `nano.py` or similar text editor
- Modify `menu.py` to use it instead

**Option 2:** Use external editor
- Edit files on PC, then upload

## Performance Optimization

### Reduce Memory Usage

```python
# In menu.py, add periodic garbage collection
import gc
gc.collect()  # After each menu operation
```

### Speed Up File Listing

Modify `fileselect.py` to cache directory listings:

```python
_dir_cache = {}

def select_file(path="/sd", ...):
    if path in _dir_cache:
        files = _dir_cache[path]
    else:
        files = os.listdir(path)
        _dir_cache[path] = files
    # ...
```

## Advanced Usage

### Custom Battery Monitoring

Create custom monitoring with alerts:

```python
from battery import get_status

def check_battery_alert():
    status = get_status()
    pct = status.get('percentage')
    
    if pct and pct < 10:
        # Low battery warning
        from ui import *
        clear()
        center_text("⚠️ LOW BATTERY ⚠️", 140, COLOR_RED)
        center_text(f"{pct}% remaining", 160, COLOR_RED)
        wait_key_raw()
```

### Background Battery Monitoring

Use threading (if available):

```python
import _thread
from battery import get_status

def battery_monitor_thread():
    while True:
        status = get_status()
        if status['percentage'] < 10:
            # Trigger alert
            pass
        time.sleep(60)  # Check every minute

_thread.start_new_thread(battery_monitor_thread, ())
```

### Custom App Launcher

Create a launcher for specific apps:

```python
def quick_launch_apps():
    apps = {
        '1': '/sd/calculator.py',
        '2': '/sd/game.py',
        '3': '/sd/notes.py',
    }
    
    clear()
    center_text("Quick Launch", 60)
    # ... draw menu ...
    choice = wait_key_raw()
    
    if choice in apps:
        exec(open(apps[choice]).read())
```

## Next Steps

1. **Test thoroughly** on your hardware
2. **Customize colors** and layout to your preference  
3. **Add custom apps** to `/sd` directory
4. **Create shortcuts** for frequently used functions
5. **Report issues** and suggest improvements

## Support

For issues specific to:
- **PicoCalc hardware**: Contact PicoCalc support
- **MicroPython**: Check MicroPython documentation
- **This dashboard**: Check README.md and VISUAL_GUIDE.md

## Updates

To update the dashboard:
1. Backup your `/sd/new/` folder
2. Upload new versions
3. Retest with `test_dashboard.py`
4. Restore any custom modifications

## Contributing

Improvements welcome! Consider adding:
- More menu options
- Better battery algorithms
- Custom themes
- App marketplace
- Settings persistence
- WiFi status (for Pico W)
