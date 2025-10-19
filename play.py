# play.py - Music player for PicoCalc Dashboard
import time
from ui import *
from fileselect import select_file

def play_music_file():
    """
    Select and play an MP3 file from /sd directory.
    Uses UART for non-blocking keyboard input during playback.
    """
    # Use file selector to choose music file
    path = select_file(
        path="/sd",
        exts=(".mp3",),
        title="Select Music File",
        return_full_path=True
    )
    
    if not path:
        return  # User cancelled
    
    # Extract filename for display
    filename = path.split("/")[-1]
    
    # Try to import required modules
    try:
        import mp3
        import vtterminal
        from machine import UART
    except ImportError as e:
        clear()
        center_text("Music Module Error", 100, COLOR_RED)
        center_text(str(e), 130, COLOR_WHITE)
        center_text("MP3 playback not available", 150, COLOR_WHITE)
        center_text("Press any key...", 290, COLOR_YELLOW)
        wait_key_raw()
        return
    
    # Show initial screen
    clear()
    center_text("Music Player", 60, COLOR_CYAN)
    draw_line_horizontal(80, 40, 280, COLOR_WHITE)
    if len(filename) > 35:
        center_text(filename[:35], 100, COLOR_WHITE)
        center_text(filename[35:], 116, COLOR_WHITE)
    else:
        center_text(filename, 108, COLOR_WHITE)
    draw_line_horizontal(140, 40, 280, COLOR_WHITE)
    center_text("SPACE: Play/Stop | Q: Exit", 260, COLOR_YELLOW)

    # Use PicoCalc keyboard for input
    from picocalc import keyboard
    temp = bytearray(1)
    state = "stopped"
    playing = False
    user_exit = False

    try:
        import mp3
        mp3.init(pin_l=26, pin_r=27)
        mp3.load(path)

        while True:
            clear()
            center_text("Music Player", 60, COLOR_CYAN)
            draw_line_horizontal(80, 40, 280, COLOR_WHITE)
            if len(filename) > 35:
                center_text(filename[:35], 100, COLOR_WHITE)
                center_text(filename[35:], 116, COLOR_WHITE)
            else:
                center_text(filename, 108, COLOR_WHITE)
            draw_line_horizontal(140, 40, 280, COLOR_WHITE)
            center_text(f"State: {state.upper()}", 180, COLOR_YELLOW)
            center_text("SPACE: Play/Stop | Q: Exit", 260, COLOR_YELLOW)

            # Check for key
            if keyboard.readinto(temp):
                key = temp[0]
                if key in (ord('q'), ord('Q')):
                    user_exit = True
                    break
                elif key == 32:  # Space
                    if not playing:
                        mp3.play()
                        state = "playing"
                        playing = True
                    else:
                        mp3.stop()
                        state = "stopped"
                        playing = False

            # If playing, check if finished
            if playing:
                if mp3.state() != "playing":
                    state = "stopped"
                    playing = False
            time.sleep_ms(30)

        # Always stop playback on exit
        mp3.stop()
        clear()
        if user_exit:
            center_text("Exited Music Player", 140, COLOR_CYAN)
        else:
            center_text("Playback Stopped", 140, COLOR_YELLOW)
        center_text("Press any key to return...", 290, COLOR_YELLOW)
        # Wait for key
        while not keyboard.readinto(temp):
            pass

    except Exception as e:
        try:
            mp3.stop()
        except:
            pass
        clear()
        center_text("Playback Error", 100, COLOR_RED)
        center_text(str(e), 130, COLOR_WHITE)
        center_text("Press any key...", 290, COLOR_YELLOW)
        from picocalc import keyboard
        temp = bytearray(1)
        while not keyboard.readinto(temp):
            pass
