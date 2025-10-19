# ARCHITECTURE.md - System Architecture

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    PicoCalc Hardware                │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │ Pico 2   │  │ 320x320  │  │ 2x 18650 Li-ion │  │
│  │ RP2040   │──│ Display  │  │ (7600mAh)       │  │
│  │          │  └──────────┘  └─────────────────┘  │
│  │ GPIO29   │──[VSYS ADC]──[Battery Voltage]      │
│  │ Pins26/27│──[MP3 Audio]                         │
│  └──────────┘                                       │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              MicroPython Firmware                   │
│  ┌──────────────────────────────────────────────┐  │
│  │ Built-in Modules: machine, gc, sys, os       │  │
│  │ Custom Modules: picocalc, mp3, vtterminal    │  │
│  │ Functions: edit()                            │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│            Dashboard Core Modules (/sd/new/)        │
│                                                     │
│  ┌──────────────┐    ┌──────────────┐             │
│  │  battery.py  │    │    ui.py     │             │
│  ├──────────────┤    ├──────────────┤             │
│  │ - ADC Read   │    │ - Drawing    │             │
│  │ - Voltage    │    │ - Text       │             │
│  │ - Percentage │    │ - Colors     │             │
│  │ - USB Detect │    │ - Battery    │             │
│  └──────┬───────┘    │   Icon       │             │
│         │            │ - Progress   │             │
│         │            │   Bar        │             │
│         │            └──────┬───────┘             │
│         │                   │                     │
│         └──────┬────────────┘                     │
│                ▼                                   │
│  ┌────────────────────────────────────┐           │
│  │          menu.py                   │           │
│  ├────────────────────────────────────┤           │
│  │ - Main Menu                        │           │
│  │ - Navigation                       │           │
│  │ - Page Manager                     │           │
│  │   • Memory Stats                   │           │
│  │   • Battery Details                │           │
│  │   • App Launcher                   │           │
│  │   • File Editor                    │           │
│  │   • Music Player                   │           │
│  │   • Power Menu                     │           │
│  └─────┬──────────────────────────────┘           │
│        │                                           │
│        ├──────────┬──────────┬──────────┐         │
│        ▼          ▼          ▼          ▼         │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │fileselect│ │ loadapp │ │  play   │ │  test  │ │
│  │   .py    │ │   .py   │ │  .py    │ │  .py   │ │
│  ├──────────┤ ├─────────┤ ├─────────┤ ├────────┤ │
│  │ Browse   │ │ Select  │ │ Select  │ │ Unit   │ │
│  │ Filter   │ │ & Run   │ │ & Play  │ │ Tests  │ │
│  │ Scroll   │ │ Python  │ │ MP3     │ │ for    │ │
│  │ Select   │ │ Apps    │ │ Files   │ │ all    │ │
│  └──────────┘ └─────────┘ └─────────┘ └────────┘ │
└─────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Battery Monitoring Flow
```
Hardware ADC → battery.py → ui.py → Display
     │              │          │
  GPIO29      Read voltage  Draw icon
  (VSYS)      Calculate %   Show color
                USB detect   Update text
```

### Menu Navigation Flow
```
User Input → menu.py → ui.py → Display
    │           │         │
  Arrows    Navigation  Drawing
  Enter     Selection   Refresh
  Q key     Action      Update
```

### File Selection Flow
```
menu.py → fileselect.py → os.listdir() → Display
   │            │              │
Request      Browse           Files
Path         Filter           List
Callback     Select           Show
   │            │              │
   └────────────┴──────────────┘
                │
            Return path
```

### App Execution Flow
```
menu.py → loadapp.py → fileselect.py → exec()
   │          │              │            │
Launch    Request file   User selects  Run code
          Read file      Return path   Show result
```

## 🏗️ Module Dependencies

```
menu.py
  ├── ui.py
  │   └── picocalc.display
  ├── battery.py
  │   └── machine.ADC
  ├── fileselect.py
  │   ├── ui.py
  │   └── os
  ├── loadapp.py
  │   ├── ui.py
  │   └── fileselect.py
  └── play.py
      ├── ui.py
      ├── fileselect.py
      ├── mp3
      ├── vtterminal
      └── machine.UART

test_dashboard.py
  ├── battery.py
  ├── ui.py
  ├── fileselect.py
  └── menu.py
```

## 📊 Function Call Hierarchy

### Main Entry Point
```
main()
  └─► show_main_menu(battery_status)
       ├─► draw_title_bar()
       │    ├─► draw_text()
       │    ├─► draw_battery_status()
       │    │    └─► draw_battery_icon()
       │    └─► draw_line_horizontal()
       ├─► draw_menu_item() (×7)
       └─► wait_key_raw()
            └─► Return choice
```

### Battery Status Page
```
show_battery_details()
  ├─► get_battery_status()
  │    └─► BatteryMonitor.get_status()
  │         ├─► read_vsys_voltage()
  │         │    └─► ADC.read_u16()
  │         ├─► is_usb_powered()
  │         └─► voltage_to_percentage()
  ├─► draw_title_bar()
  ├─► draw_text() (×N)
  ├─► draw_progress_bar()
  └─► wait_key_raw()
```

### File Selection
```
select_file(path, exts, title)
  ├─► os.listdir(path)
  ├─► Filter by extensions
  ├─► Sort files
  └─► Loop:
       ├─► clear()
       ├─► draw_title_bar()
       ├─► draw_menu_item() (×visible)
       ├─► wait_key_raw()
       └─► Return selected path
```

## 💾 Memory Layout

```
┌─────────────────────────────────────┐
│         RAM (256KB typical)         │
├─────────────────────────────────────┤
│ MicroPython Runtime                 │ ~50-100KB
├─────────────────────────────────────┤
│ Framebuffer (320x320x1bit)          │ ~13KB
├─────────────────────────────────────┤
│ Dashboard Modules (loaded)          │ ~15KB
│  - menu.py                          │
│  - ui.py                            │
│  - battery.py                       │
│  - fileselect.py (when used)        │
├─────────────────────────────────────┤
│ Free Memory (gc.mem_free())         │ ~100KB+
│  - User apps                        │
│  - Temporary data                   │
│  - Stack/heap                       │
└─────────────────────────────────────┘

Storage (/sd card):
┌─────────────────────────────────────┐
│ /sd/new/                            │
│  ├── battery.py          (~7KB)     │
│  ├── ui.py               (~9KB)     │
│  ├── menu.py             (~15KB)    │
│  ├── fileselect.py       (~5KB)     │
│  ├── loadapp.py          (~2KB)     │
│  ├── play.py             (~4KB)     │
│  ├── test_dashboard.py   (~7KB)     │
│  └── docs/*.md           (~50KB)    │
├─────────────────────────────────────┤
│ /sd/ (user files)                   │
│  ├── *.py (apps)                    │
│  ├── *.mp3 (music)                  │
│  └── *.txt (data)                   │
└─────────────────────────────────────┘
```

## ⚡ Execution Flow

### Boot Sequence
```
1. Power On / Reset
   ↓
2. MicroPython Boots
   ↓
3. Run /sd/main.py (if exists)
   ↓
4. Import dashboard modules
   │  sys.path.append('/sd/new')
   │  from menu import main
   ↓
5. Initialize
   │  - Hide cursor
   │  - Read battery
   │  - Clear screen
   ↓
6. Show Main Menu
   │  - Draw UI
   │  - Wait for input
   ↓
7. User Selection
   │  ├─► Memory Stats → Show → Return
   │  ├─► Battery → Show → Return
   │  ├─► Run App → Select → Execute → Return
   │  ├─► Edit File → Select → Edit → Return
   │  ├─► Play Music → Select → Play → Return
   │  ├─► REPL → Exit dashboard
   │  └─► Reset → Reboot
   ↓
8. Loop to step 6 (unless REPL/Reset)
```

### Event Loop
```
while True:
    ┌─────────────────────────────────┐
    │ Read Battery Status             │
    ├─────────────────────────────────┤
    │ Draw Screen                     │
    │  - Clear                        │
    │  - Title bar (with battery)     │
    │  - Menu items                   │
    │  - Help text                    │
    ├─────────────────────────────────┤
    │ Wait for Input (blocking)       │
    │  - Arrow keys                   │
    │  - Enter key                    │
    │  - Q key                        │
    ├─────────────────────────────────┤
    │ Process Input                   │
    │  - Update selection             │
    │  - Execute action               │
    │  - Show result                  │
    ├─────────────────────────────────┤
    │ Update State                    │
    └─────────────────────────────────┘
    Loop back to top
```

## 🎨 UI Component Hierarchy

```
Screen (320x320)
  └─► Title Bar (y: 0-24)
       ├─► Title Text (left)
       ├─► Battery Icon (right)
       │    ├─► Outline (26x12px)
       │    ├─► Terminal (2x6px)
       │    ├─► Fill (dynamic %)
       │    └─► Percentage Text
       └─► Separator Line
  └─► Content Area (y: 32-280)
       ├─► Menu Items
       │    ├─► Prefix ("> " or "  ")
       │    └─► Text (colored)
       ├─► Info Text
       ├─► Progress Bars
       │    ├─► Outline
       │    ├─► Background
       │    └─► Fill (colored)
       └─► Lists
            ├─► Scrollable Items
            └─► Scroll Indicator
  └─► Footer (y: 290-310)
       └─► Help Text
```

## 🔌 Hardware Interface Layer

```
┌───────────────────────────────────────┐
│         Dashboard Software            │
└─────────────┬─────────────────────────┘
              │
    ┌─────────┴──────────┬──────────────┐
    ▼                    ▼              ▼
┌─────────┐      ┌─────────────┐   ┌─────────┐
│ Display │      │   Battery   │   │  Audio  │
│ (320x320)│      │  (VSYS ADC) │   │(Pins 26/27)
└────┬────┘      └──────┬──────┘   └────┬────┘
     │                  │                │
     ▼                  ▼                ▼
┌────────────────────────────────────────────┐
│       picocalc.display                     │
│       machine.ADC(29)                      │
│       mp3.init()                           │
└────────────────────────────────────────────┘
```

## 🧩 Module Interactions

```
User Action → menu.py
                │
    ┌───────────┼───────────┬───────────┐
    ▼           ▼           ▼           ▼
battery.py   ui.py    fileselect.py  loadapp.py
    │           │           │           │
    ▼           ▼           ▼           ▼
Hardware    Display     Filesystem    exec()
(ADC)       (FB)        (SD card)     (Python)
```

## 📈 Performance Characteristics

| Operation | Time | Memory | Notes |
|-----------|------|--------|-------|
| Battery read | ~10ms | ~1KB | 10 samples averaged |
| Screen clear | ~5ms | 0 | Hardware operation |
| Draw text | <1ms | 0 | Per character |
| File list | 10-100ms | ~2KB | Depends on file count |
| Menu render | ~20ms | ~2KB | Full screen update |
| App exec | Variable | Variable | User code dependent |

## 🔐 Error Handling Strategy

```
┌─────────────────────────────────┐
│     Try Operation               │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    │ Success?│
    └────┬────┘
         │
    ┌────┴────┐
    ▼         ▼
   YES       NO
    │         │
    │    ┌────┴─────────────────┐
    │    │ Catch Exception      │
    │    ├──────────────────────┤
    │    │ - Clear screen       │
    │    │ - Show error message │
    │    │ - Display details    │
    │    │ - Wait for key       │
    │    │ - Return to menu     │
    │    └──────────────────────┘
    │         │
    └────┬────┘
         ▼
    Continue
```

## 🎯 Design Patterns Used

1. **Singleton Pattern**: BatteryMonitor instance
2. **Factory Pattern**: get_monitor() function
3. **Callback Pattern**: UI event handlers
4. **State Machine**: Menu navigation
5. **Template Method**: Screen rendering
6. **Strategy Pattern**: Color selection based on state
7. **Observer Pattern**: Battery status updates

## 🚦 State Diagram

```
┌─────────┐
│  START  │
└────┬────┘
     ▼
┌─────────┐
│ Main    │◄─────────────┐
│ Menu    │              │
└────┬────┘              │
     │                   │
     ├─► REPL ──────► Exit
     │                   │
     ├─► Memory ────────►┤
     │                   │
     ├─► Battery ───────►┤
     │                   │
     ├─► Run App ───────►┤
     │      └─► File Select ─► Execute
     │                   │
     ├─► Edit ──────────►┤
     │      └─► File Select ─► Editor
     │                   │
     ├─► Music ─────────►┤
     │      └─► File Select ─► Player
     │                   │
     └─► Power ─────────►┤
            └─► Confirm ─► Reset
```

---

This architecture is designed for:
- ✅ **Modularity** - Each component is independent
- ✅ **Maintainability** - Clear separation of concerns
- ✅ **Extensibility** - Easy to add new features
- ✅ **Performance** - Minimal memory footprint
- ✅ **Reliability** - Comprehensive error handling
