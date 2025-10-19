# loadapp.py - App loader for PicoCalc Dashboard
import time
from ui import *
from fileselect import select_file

def run_app():
    """
    Select and run a Python app from /sd directory.
    """
    # Use file selector to choose app
    path = select_file(
        path="/sd",
        exts=(".py",),
        title="Select App to Run",
        return_full_path=True
    )
    
    if not path:
        return  # User cancelled
    
    # Extract filename for display
    filename = path.split("/")[-1]
    
    # Show loading message
    clear()
    center_text(f"Running {filename}...", 140, COLOR_YELLOW)
    center_text("Please wait...", 160, COLOR_WHITE)
    time.sleep(0.3)
    
    # Run the app
    try:
        with open(path, 'r') as f:
            code = f.read()
        
        # Execute in isolated namespace
        exec(code, {'__name__': '__main__'})
        
    except Exception as e:
        # Show error
        clear()
        center_text("Error Running App", 100, COLOR_RED)
        
        # Display error message (may be long)
        error_text = str(e)
        y = 130
        # Split long errors into multiple lines
        max_chars = 38
        while error_text:
            line = error_text[:max_chars]
            error_text = error_text[max_chars:]
            center_text(line, y, COLOR_WHITE)
            y += 16
            if y > 250:  # Don't overflow screen
                break
        
        center_text("Press any key...", 290, COLOR_YELLOW)
        wait_key_raw()
