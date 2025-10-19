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
        import sys
        with open(path, 'r') as f:
            code = f.read()
        # Execute in isolated namespace
        exec(code, {'__name__': '__main__'})
    except Exception as e:
        # Log exception to file using sys.print_exception
        try:
            with open('/sd/app_error.log', 'w') as logf:
                sys.print_exception(e, logf)
        except Exception:
            pass
        # Show error
        clear()
        center_text("Error Running App", 100, COLOR_RED)
        # Show exception type and message
        error_text = '{}: {}'.format(type(e).__name__, e)
        y = 130
        max_chars = 38
        while error_text:
            line = error_text[:max_chars]
            error_text = error_text[max_chars:]
            center_text(line, y, COLOR_WHITE)
            y += 16
            if y > 250:
                break
        center_text("Press any key...", 290, COLOR_YELLOW)
        wait_key_raw()
