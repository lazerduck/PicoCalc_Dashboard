# ui.py - UI components and helpers for PicoCalc Dashboard
import picocalc
import sys

fb = picocalc.display  # 320x320 framebuffer

# ============ Color Definitions ============
COLOR_BLACK = 0
COLOR_BLUE = 1
COLOR_RED = 2
COLOR_GREEN = 3
COLOR_CYAN = 4
COLOR_MAGENTA = 5
COLOR_YELLOW = 6
COLOR_WHITE = 7

# ============ Text Rendering ============
def draw_text(s, x, y, fg=COLOR_WHITE, bg=None):
    """
    Draw text with foreground and optional background color.
    Handles builds that may not support background color.
    """
    try:
        if bg is None:
            fb.text(s, x, y, fg)
        else:
            fb.text(s, x, y, fg, bg)
    except TypeError:
        # Fallback for builds without bg color support
        fb.text(s, x, y, fg)

def center_text(text, y, color=COLOR_WHITE):
    """Center text horizontally at given y position"""
    # Each character is 8 pixels wide
    text_width = len(text) * 8
    x = max(0, (320 - text_width) // 2)
    draw_text(text, x, y, color)

# ============ Drawing Primitives ============
def clear():
    """Clear the screen to black"""
    fb.fill(COLOR_BLACK)

def draw_line_horizontal(y, x1=0, x2=320, color=COLOR_WHITE):
    """Draw a horizontal line"""
    try:
        fb.hline(x1, y, x2 - x1, color)
    except AttributeError:
        # Fallback: use thin rectangle
        fb.fill_rect(x1, y, x2 - x1, 1, color)

def draw_rect(x, y, w, h, color=COLOR_WHITE, fill=False):
    """Draw a rectangle (optionally filled)"""
    if fill:
        fb.fill_rect(x, y, w, h, color)
    else:
        try:
            fb.rect(x, y, w, h, color)
        except AttributeError:
            # Fallback: draw 4 lines
            fb.fill_rect(x, y, w, 1, color)  # top
            fb.fill_rect(x, y + h - 1, w, 1, color)  # bottom
            fb.fill_rect(x, y, 1, h, color)  # left
            fb.fill_rect(x + w - 1, y, 1, h, color)  # right

# ============ Battery Icon ============
def draw_battery_icon(x, y, percentage, usb_power=False):
    """
    Draw a battery icon with percentage fill and terminal bump.
    
    Args:
        x, y: Top-left corner of battery body
        percentage: 0-100 (None if USB powered)
        usb_power: True if on USB power
    
    Icon size: 24x12 pixels (body) + 2px terminal = 26x12 total
    """
    # Battery dimensions
    body_w = 24
    body_h = 12
    terminal_w = 2
    terminal_h = 6
    
    # Determine battery color based on charge level
    if usb_power:
        outline_color = COLOR_CYAN
        fill_color = COLOR_CYAN
        fill_percentage = 100
    elif percentage is None:
        outline_color = COLOR_WHITE
        fill_color = COLOR_WHITE
        fill_percentage = 0
    else:
        # Color coding: Green (>50%), Yellow (20-50%), Red (<20%)
        if percentage > 50:
            outline_color = COLOR_GREEN
            fill_color = COLOR_GREEN
        elif percentage > 20:
            outline_color = COLOR_YELLOW
            fill_color = COLOR_YELLOW
        else:
            outline_color = COLOR_RED
            fill_color = COLOR_RED
        fill_percentage = max(0, min(100, percentage))
    
    # Draw battery body outline
    draw_rect(x, y, body_w, body_h, outline_color, fill=False)
    
    # Draw positive terminal (small bump on right side)
    terminal_y = y + (body_h - terminal_h) // 2
    fb.fill_rect(x + body_w, terminal_y, terminal_w, terminal_h, outline_color)
    
    # Draw battery fill level
    if fill_percentage > 0:
        # Leave 2px margin inside battery
        fill_w = int((body_w - 4) * fill_percentage / 100)
        if fill_w > 0:
            fb.fill_rect(x + 2, y + 2, fill_w, body_h - 4, fill_color)

def draw_battery_status(x, y, battery_status):
    """
    Draw battery icon with percentage text.
    
    Args:
        x, y: Top-left position
        battery_status: Dict from battery.get_status()
    
    Layout: [ICON] 99%
    Total width: ~60 pixels
    """
    percentage = battery_status.get("percentage")
    usb_power = battery_status.get("usb_power", False)
    
    # Draw icon
    draw_battery_icon(x, y, percentage, usb_power)
    
    # Draw percentage text
    if usb_power:
        text = "USB"
        color = COLOR_CYAN
    elif percentage is not None:
        text = f"{int(percentage)}%"
        # Match icon color
        if percentage > 50:
            color = COLOR_GREEN
        elif percentage > 20:
            color = COLOR_YELLOW
        else:
            color = COLOR_RED
    else:
        text = "--"
        color = COLOR_WHITE
    
    # Position text to the right of icon (icon is ~26px wide)
    text_x = x + 30
    text_y = y + 2  # Vertically center with icon
    draw_text(text, text_x, text_y, color)

# ============ Input Handling ============
def wait_key_raw():
    """
    Read a single raw key from stdin (blocking).
    
    Returns:
        'A' = up arrow
        'B' = down arrow
        'C' = right arrow
        'D' = left arrow
        '\r' or '\n' = enter
        Other characters as-is
    """
    ch = sys.stdin.read(1)
    if ch == '\x1b':  # Escape sequence (arrow keys)
        ch2 = sys.stdin.read(1)
        if ch2 == '[':
            ch3 = sys.stdin.read(1)
            return ch3  # 'A'=up, 'B'=down, 'C'=right, 'D'=left
        return ch2
    return ch

# ============ UI Layout Components ============
def draw_title_bar(title, battery_status=None):
    """
    Draw title bar with title text and optional battery indicator.
    
    Args:
        title: Title text (left side)
        battery_status: Optional battery status dict (right side)
    """
    # Title text on left
    draw_text(title, 8, 8, COLOR_WHITE)
    
    # Battery on right if provided
    if battery_status:
        # Position battery icon in top-right corner
        # Screen width = 320, icon+text ~= 60px, margin = 8px
        battery_x = 320 - 68
        draw_battery_status(battery_x, 8, battery_status)
    
    # Horizontal line separator
    draw_line_horizontal(24, 0, 320, COLOR_WHITE)

def draw_menu_item(text, x, y, selected=False, color=None):
    """
    Draw a menu item with optional selection highlight.
    
    Args:
        text: Menu item text
        x, y: Position
        selected: If True, draw with selection indicator
        color: Override color (default: YELLOW if selected, WHITE otherwise)
    """
    if color is None:
        color = COLOR_YELLOW if selected else COLOR_WHITE
    
    prefix = "> " if selected else "  "
    draw_text(prefix + text, x, y, color)

def draw_progress_bar(x, y, width, height, percentage, color=COLOR_WHITE, bg_color=COLOR_BLACK):
    """
    Draw a progress bar.
    
    Args:
        x, y: Top-left corner
        width, height: Dimensions
        percentage: Fill percentage (0-100)
        color: Fill color
        bg_color: Background color
    """
    # Draw outline
    draw_rect(x, y, width, height, COLOR_WHITE, fill=False)
    
    # Fill background
    if bg_color != COLOR_BLACK:
        fb.fill_rect(x + 1, y + 1, width - 2, height - 2, bg_color)
    
    # Draw fill
    fill_width = int((width - 2) * max(0, min(100, percentage)) / 100)
    if fill_width > 0:
        fb.fill_rect(x + 1, y + 1, fill_width, height - 2, color)
