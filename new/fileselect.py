# fileselect.py - File selector for PicoCalc Dashboard
import os
from ui import *

def select_file(path="/sd", exts=None, title="Select File", return_full_path=True, max_visible=10):
    """
    Display a file selector and return the selected file.
    
    Args:
        path: Directory to browse
        exts: Tuple of allowed extensions (e.g., (".py", ".txt")) or None for all
        title: Title to display
        return_full_path: If True, return full path; if False, return filename only
        max_visible: Maximum number of visible items
    
    Returns:
        Selected file path/name, or None if cancelled
    
    Controls:
        Up/Down arrows: Navigate
        Enter: Select
        Q: Cancel
    """
    try:
        # Get list of files
        all_items = os.listdir(path)
    except Exception as e:
        clear()
        center_text("Error reading directory", 100, COLOR_RED)
        center_text(str(e), 120, COLOR_RED)
        center_text("Press any key...", 280, COLOR_YELLOW)
        wait_key_raw()
        return None
    
    # Filter by extensions if specified
    if exts:
        files = []
        for item in all_items:
            for ext in exts:
                if item.endswith(ext):
                    files.append(item)
                    break
    else:
        files = all_items
    
    # Sort files
    files.sort()
    
    if not files:
        clear()
        center_text("No files found", 100, COLOR_YELLOW)
        if exts:
            ext_text = ", ".join(exts)
            center_text(f"Extensions: {ext_text}", 120, COLOR_WHITE)
        center_text("Press any key...", 280, COLOR_YELLOW)
        wait_key_raw()
        return None
    
    # Selection state
    selected = 0
    scroll_offset = 0
    
    while True:
        clear()
        
        # Draw title bar (no battery here to save space)
        draw_text(title, 8, 8, COLOR_WHITE)
        draw_line_horizontal(24, 0, 320, COLOR_WHITE)
        
        # Calculate visible range
        if selected < scroll_offset:
            scroll_offset = selected
        elif selected >= scroll_offset + max_visible:
            scroll_offset = selected - max_visible + 1
        
        # Draw file list
        y_start = 32
        line_height = 16
        
        for i in range(max_visible):
            idx = scroll_offset + i
            if idx >= len(files):
                break
            
            y = y_start + i * line_height
            is_selected = (idx == selected)
            
            # Truncate long filenames
            filename = files[idx]
            max_chars = 36  # ~36 chars fit in 320px with 8px font
            if len(filename) > max_chars:
                filename = filename[:max_chars-3] + "..."
            
            draw_menu_item(filename, 8, y, is_selected)
        
        # Draw scroll indicator if needed
        if len(files) > max_visible:
            scroll_text = f"{selected + 1}/{len(files)}"
            draw_text(scroll_text, 8, 280, COLOR_CYAN)
        
        # Draw help text
        help_y = 300
        draw_text("UP/DOWN: Navigate | ENTER: Select | Q: Cancel", 8, help_y, COLOR_YELLOW)
        
        # Wait for input
        key = wait_key_raw()
        
        if key == 'A':  # Up
            selected = (selected - 1) % len(files)
        elif key == 'B':  # Down
            selected = (selected + 1) % len(files)
        elif key in ('\r', '\n'):  # Enter
            # Return selected file
            filename = files[selected]
            if return_full_path:
                # Ensure proper path separator
                if path.endswith('/'):
                    return path + filename
                else:
                    return path + '/' + filename
            else:
                return filename
        elif key in ('q', 'Q'):  # Cancel
            return None
    
    return None
