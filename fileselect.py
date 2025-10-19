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
        Enter: Select file or enter directory
        Left arrow: Go up to parent directory
        Q: Cancel
    """
    current_path = path
    
    while True:
        try:
            # Get list of files and directories
            all_items = os.listdir(current_path)
        except Exception as e:
            clear()
            center_text("Error reading directory", 100, COLOR_RED)
            center_text(str(e), 120, COLOR_RED)
            center_text("Press any key...", 280, COLOR_YELLOW)
            wait_key_raw()
            return None
        
        # Separate directories and files
        dirs = []
        files = []
        
        for item in all_items:
            item_path = current_path + ('/' if not current_path.endswith('/') else '') + item
            try:
                # Check if it's a directory
                os.listdir(item_path)
                dirs.append(item)
            except:
                # It's a file
                if exts:
                    for ext in exts:
                        if item.endswith(ext):
                            files.append(item)
                            break
                else:
                    files.append(item)
        
        # Sort and combine: directories first, then files
        dirs.sort()
        files.sort()
        items = [(d, True) for d in dirs] + [(f, False) for f in files]
        
        if not items:
            clear()
            center_text("No files found", 100, COLOR_YELLOW)
            if exts:
                ext_text = ", ".join(exts)
                center_text(f"Extensions: {ext_text}", 120, COLOR_WHITE)
            center_text("Press LEFT to go back or Q to cancel", 280, COLOR_YELLOW)
            wait_key_raw()
            # Don't return, allow navigation back
            if current_path != path and current_path != "/sd":
                # Go up one level
                current_path = '/'.join(current_path.rstrip('/').split('/')[:-1])
                if not current_path:
                    current_path = "/sd"
                continue
            return None
        
        # Selection state
        selected = 0
        scroll_offset = 0
        
        while True:
            clear()
            
            # Draw title bar with current path
            draw_text(title, 8, 8, COLOR_WHITE)
            # Show current path (truncated if needed)
            path_display = current_path
            if len(path_display) > 38:
                path_display = "..." + path_display[-35:]
            draw_text(path_display, 8, 20, COLOR_CYAN)
            draw_line_horizontal(32, 0, 320, COLOR_WHITE)
            
            # Calculate visible range
            if selected < scroll_offset:
                scroll_offset = selected
            elif selected >= scroll_offset + max_visible:
                scroll_offset = selected - max_visible + 1
            
            # Draw file/directory list
            y_start = 40
            line_height = 16
            
            for i in range(max_visible):
                idx = scroll_offset + i
                if idx >= len(items):
                    break
                
                y = y_start + i * line_height
                is_selected = (idx == selected)
                
                # Get item name and type
                item_name, is_dir = items[idx]
                
                # Truncate long filenames
                display_name = item_name
                prefix = "[DIR] " if is_dir else ""
                max_chars = 33 if is_dir else 36
                if len(item_name) > max_chars:
                    display_name = item_name[:max_chars-3] + "..."
                
                draw_menu_item(prefix + display_name, 8, y, is_selected)
            
            # Draw scroll indicator if needed
            if len(items) > max_visible:
                scroll_text = f"{selected + 1}/{len(items)}"
                draw_text(scroll_text, 8, 270, COLOR_CYAN)
            
            # Draw help text
            help_y = 290
            draw_text("UP/DN: Nav | ENTER: Select | LEFT: Up | Q: Quit", 8, help_y, COLOR_YELLOW)
            
            # Wait for input
            key = wait_key_raw()
            
            if key == 'A':  # Up
                selected = (selected - 1) % len(items)
            elif key == 'B':  # Down
                selected = (selected + 1) % len(items)
            elif key in ('\r', '\n'):  # Enter
                item_name, is_dir = items[selected]
                if is_dir:
                    # Navigate into directory
                    current_path = current_path + ('/' if not current_path.endswith('/') else '') + item_name
                    break  # Break inner loop to refresh listing
                else:
                    # Return selected file
                    if return_full_path:
                        # Ensure proper path separator
                        if current_path.endswith('/'):
                            return current_path + item_name
                        else:
                            return current_path + '/' + item_name
                    else:
                        return item_name
            elif key == 'D':  # Left arrow - go up one directory
                if current_path != path and current_path != "/sd":
                    # Go up one level
                    current_path = '/'.join(current_path.rstrip('/').split('/')[:-1])
                    if not current_path:
                        current_path = "/sd"
                    break  # Break inner loop to refresh listing
            elif key in ('q', 'Q'):  # Cancel
                return None
    
    return None
