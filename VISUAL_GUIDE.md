# VISUAL_GUIDE.md - Dashboard UI Layout Guide

## Main Menu Screen

```
┌────────────────────────────────────────┐ 320px wide
│ PicoCalc Dashboard      [🔋][██░] 75% │ ← Title bar with battery
├────────────────────────────────────────┤
│                                        │
│   > Open REPL                          │ ← Selected (yellow)
│     Memory Stats                       │ ← Available (white)
│     Battery Status                     │
│     Run App                            │
│     Edit File                          │
│     Play Music                         │
│     Power Off / Reset                  │
│                                        │
│                                        │
│                                        │
│                                        │
│                                        │
│                                        │
│                                        │
│ UP/DOWN: Navigate | ENTER: Select      │ ← Help text (yellow)
└────────────────────────────────────────┘ 320px tall
```

## Battery Icon Detail

```
Normal Battery (not USB):
┌──────────────────────┬─┐
│████████████░░░░░░░░░░│█│  ← Filled based on %
└──────────────────────┴─┘  ← Terminal bump on right
    24px wide   2px
    12px tall

Colors:
- Green:  > 50% charge
- Yellow: 20-50% charge
- Red:    < 20% charge
- Cyan:   USB powered (always full)

Display: [ICON] 75%
```

## Battery Status Screen

```
┌────────────────────────────────────────┐
│ Battery Status          [🔋][██░] 75%  │
├────────────────────────────────────────┤
│                                        │
│ Voltage:    3.87 V  (3870 mV)         │
│                                        │
│ Power:      Battery                    │
│                                        │
│ Percentage: 75%                        │ ← Color coded
│                                        │
│ Status:     Good                       │ ← Color coded
│                                        │
│ ┌────────────────────────────────────┐ │
│ │███████████████████░░░░░░░░░░░░░░░░│ │ ← Big progress bar
│ │           75%                      │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Battery: 2x 18650 Li-ion (7600mAh)    │ ← Technical info
│ Range: 3.0V - 4.2V per cell           │
│                                        │
│ Press any key to return...             │
└────────────────────────────────────────┘
```

## Memory Stats Screen

```
┌────────────────────────────────────────┐
│ Memory Statistics       [🔋][██░] 75%  │
├────────────────────────────────────────┤
│                                        │
│ Total:          65536 bytes            │
│ Free:           45000 bytes            │
│ Allocated:      20536 bytes            │
│ Free:              68%                 │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │███████████████░░░░░░░░░░░░░░░░░░░│ │ ← Visual bar
│ └────────────────────────────────────┘ │
│ Free          Used                     │
│                                        │
│ Detailed info available in REPL:       │
│ >>> import gc                          │
│ >>> gc.mem_free()                      │
│                                        │
│ Press any key to return...             │
└────────────────────────────────────────┘
```

## File Selector Screen

```
┌────────────────────────────────────────┐
│ Select File to Edit                    │
├────────────────────────────────────────┤
│                                        │
│   > main.py                            │ ← Selected
│     config.json                        │
│     data.csv                           │
│     notes.txt                          │
│     app1.py                            │
│     app2.py                            │
│     music.mp3                          │
│     readme.md                          │
│     test.py                            │
│     utils.py                           │
│                                        │
│ 5/24                                   │ ← Scroll indicator
│                                        │
│                                        │
│ UP/DOWN: Navigate | ENTER: Select...   │
└────────────────────────────────────────┘
```

## Music Player Screen

```
┌────────────────────────────────────────┐
│          Now Playing                   │
│ ────────────────────────────────────   │
│                                        │
│         awesome_song.mp3               │
│                                        │
│ ────────────────────────────────────   │
│                                        │
│                                        │
│                                        │
│                                        │
│                                        │
│                                        │
│                                        │
│                                        │
│ Press any key to stop                  │
└────────────────────────────────────────┘
```

## Color Palette (0-7)

```
0 = BLACK   ████  Background
1 = BLUE    ████  Accents
2 = RED     ████  Errors, Low Battery
3 = GREEN   ████  Success, Good Battery
4 = CYAN    ████  USB Power, Info
5 = MAGENTA ████  (Reserved)
6 = YELLOW  ████  Selected, Warnings
7 = WHITE   ████  Normal Text
```

## Battery Status Colors

| Charge Level | Icon Color | Text Color | Status    |
|--------------|------------|------------|-----------|
| > 50%        | Green      | Green      | Full/Good |
| 20-50%       | Yellow     | Yellow     | Good      |
| 10-20%       | Yellow     | Yellow     | Low       |
| < 10%        | Red        | Red        | Critical  |
| USB          | Cyan       | Cyan       | USB Power |

## Navigation Flow

```
Main Menu
   │
   ├──► REPL ──────────────► Exit to MicroPython
   │
   ├──► Memory Stats ──────► View + Return
   │
   ├──► Battery Status ────► View + Return
   │
   ├──► Run App
   │      └──► File Selector ──► Run .py ──► Return
   │
   ├──► Edit File
   │      └──► File Selector ──► Editor ──► Return
   │
   ├──► Play Music
   │      └──► File Selector ──► Player ──► Return
   │
   └──► Power Off / Reset
          └──► Confirmation ──► Reset
```

## Screen Coordinates

```
┌─(0,0)──────────────────────(320,0)──┐
│ Title Bar (y: 0-24)                 │
│ Separator Line (y: 24)              │
│                                     │
│ Content Area (y: 25-289)            │
│                                     │
│                                     │
│ Help Text (y: 290-310)              │
└─(0,320)───────────────────(320,320)─┘

Common positions:
- Title: (8, 8)
- Battery: (252, 8)  [right-aligned]
- Separator: y=24
- Content starts: y=40
- Line height: 16-20px
- Help text: y=290
```

## Font Metrics

- Character width: 8 pixels
- Character height: 8 pixels
- Max characters per line: 40 chars (320px / 8px)
- Recommended max: 36 chars (with margins)

## Layout Guidelines

1. **Title Bar**: Always 24px tall with separator
2. **Margins**: 8-12px from screen edges
3. **Line Height**: 16-20px for readability
4. **Help Text**: Always at bottom (y=290)
5. **Content Area**: y=32 to y=280
6. **Battery Icon**: Top-right corner (x=252, y=8)
