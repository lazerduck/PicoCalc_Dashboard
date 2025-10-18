# nano2.py - A simple text editor for PicoCalc
import picocalc, os, sys, time

fb = picocalc.display
WIDTH, HEIGHT = 320, 320
CHARACTER_WIDTH = 6  # Adjusted for 6px wide font
CHARACTER_HEIGHT = 8  # Adjusted for 8px tall font
CHARS_PER_LINE = 38
LINES_ON_SCREEN = 16



LINES = [""] # default to one empty line
CURSOR_X, CURSOR_Y = 0, 0
CURSOR_COLOR = 2
LAST_FILENAME = ""
line_offset = 0  # horizontal scroll offset for current line

def draw_status_bar(last_key=None):
	# Compose status text
	status = "^S: Save  ^Q: Quit ^L: Load"
	pos = f"Ln {CURSOR_Y+1}, Col {CURSOR_X+1}"
	keyinfo = f"Key: {last_key!r}" if last_key is not None else ""
	# Draw status bar background
	fb.fill_rect(0, HEIGHT-CHARACTER_HEIGHT-2, WIDTH, CHARACTER_HEIGHT+2, 1)  # color 1 for status bar
	fb.text(status, 4, HEIGHT-CHARACTER_HEIGHT, 7)
	# Move keyinfo to the right, just before the cursor position
	keyinfo_x = WIDTH - 4 - len(pos)*CHARACTER_WIDTH - 10*CHARACTER_WIDTH - len(keyinfo)*CHARACTER_WIDTH
	fb.text(keyinfo, max(keyinfo_x, 140), HEIGHT-CHARACTER_HEIGHT, 3)
	fb.text(pos, WIDTH-4-len(pos)*CHARACTER_WIDTH, HEIGHT-CHARACTER_HEIGHT, 6)
	
def insert_char(ch):
	global CURSOR_X, CURSOR_Y, LINES, line_offset
	line = LINES[CURSOR_Y]
	LINES[CURSOR_Y] = line[:CURSOR_X] + ch + line[CURSOR_X:]
	CURSOR_X += 1
	# Scroll right if needed
	if CURSOR_X - line_offset >= CHARS_PER_LINE:
		line_offset += 1
		
def draw_text_area():
	global line_offset
	for i in range(LINES_ON_SCREEN):
		y = i * CHARACTER_HEIGHT + 4
		if i < len(LINES):
			line = LINES[i]
			# Horizontal scroll: show only visible part
			if i == CURSOR_Y:
				visible = line[line_offset:line_offset+CHARS_PER_LINE]
				# Pad if short
				if len(visible) < CHARS_PER_LINE:
					visible = visible + ' ' * (CHARS_PER_LINE - len(visible))
				fb.text(visible, 4, y, 7)
				# Draw cursor
				cursor_screen_x = CURSOR_X - line_offset
				if 0 <= cursor_screen_x < CHARS_PER_LINE:
					fb.fill_rect(4 + cursor_screen_x*CHARACTER_WIDTH, y, CHARACTER_WIDTH, CHARACTER_HEIGHT, CURSOR_COLOR)
					fb.text(visible[cursor_screen_x:cursor_screen_x+1], 4 + cursor_screen_x*CHARACTER_WIDTH, y, 7)
			else:
				# For other lines, just show visible window
				visible = line[line_offset:line_offset+CHARS_PER_LINE]
				if len(visible) < CHARS_PER_LINE:
					visible = visible + ' ' * (CHARS_PER_LINE - len(visible))
				fb.text(visible, 4, y, 7)
		else:
			fb.text(' ' * CHARS_PER_LINE, 4, y, 7)
			
def delete_char():
	global CURSOR_X, CURSOR_Y, LINES, line_offset
	line = LINES[CURSOR_Y]
	if CURSOR_X > 0:
		# Delete character before cursor
		LINES[CURSOR_Y] = line[:CURSOR_X-1] + line[CURSOR_X:]
		CURSOR_X -= 1
		# Scroll left if needed
		if CURSOR_X < line_offset:
			line_offset = max(0, CURSOR_X)
	elif CURSOR_X == 0 and CURSOR_Y > 0:
		# Merge current line into previous line
		prev_line = LINES[CURSOR_Y-1]
		LINES[CURSOR_Y-1] = prev_line + line
		LINES.pop(CURSOR_Y)
		CURSOR_Y -= 1
		CURSOR_X = len(prev_line)
		# Adjust offset for new cursor position
		if CURSOR_X - line_offset >= CHARS_PER_LINE:
			line_offset = CURSOR_X - CHARS_PER_LINE + 1
		elif CURSOR_X < line_offset:
			line_offset = max(0, CURSOR_X)
			
def insert_newline():
	global CURSOR_X, CURSOR_Y, LINES
	line = LINES[CURSOR_Y]
	# Split line at cursor
	before = line[:CURSOR_X]
	after = line[CURSOR_X:]
	LINES.insert(CURSOR_Y + 1, after)
	LINES[CURSOR_Y] = before
	CURSOR_Y += 1
	CURSOR_X = 0
	
def move_cursor(key):
	global CURSOR_X, CURSOR_Y, LINES, line_offset
	# Accepts k3 ('A', 'B', 'C', 'D') and moves cursor
	if key == 'A':  # Up
		if CURSOR_Y > 0:
			CURSOR_Y -= 1
		CURSOR_X = min(CURSOR_X, len(LINES[CURSOR_Y]))
	elif key == 'B':  # Down
		if CURSOR_Y < len(LINES) - 1:
			CURSOR_Y += 1
		CURSOR_X = min(CURSOR_X, len(LINES[CURSOR_Y]))
	elif key == 'C':  # Right
		CURSOR_X += 1
		# Scroll right if needed
		if CURSOR_X - line_offset >= CHARS_PER_LINE:
			line_offset += 1
	elif key == 'D':  # Left
		if CURSOR_X > 0:
			CURSOR_X -= 1
		# Scroll left if needed
		if CURSOR_X < line_offset:
			line_offset = max(0, CURSOR_X)
			
def prompt_filename(mode="Save as"):
	# Simple filename prompt at bottom
	global LAST_FILENAME
	filename = LAST_FILENAME or ""
	while True:
		fb.fill_rect(0, HEIGHT-CHARACTER_HEIGHT-2, WIDTH, CHARACTER_HEIGHT+2, 1)
		fb.text(f"{mode}: /sd/" + filename, 4, HEIGHT-CHARACTER_HEIGHT, 7)
		k = sys.stdin.read(1)
		if k in ('\r', '\n'):
			return filename
		elif k == '\x7f':
			filename = filename[:-1]
		elif 32 <= ord(k) <= 126:
			filename += k

def save_file():
	import os
	global LAST_FILENAME
	fname = prompt_filename()
	if fname:
		LAST_FILENAME = fname
	if not fname:
		return
	fullpath = "/sd/" + fname
	exists = False
	try:
		exists = fname in os.listdir("/sd")
	except Exception:
		pass
	if exists:
		# Prompt for overwrite confirmation
		fb.fill_rect(0, HEIGHT-CHARACTER_HEIGHT-2, WIDTH, CHARACTER_HEIGHT+2, 1)
		fb.text(f"Overwrite {fname}? (y/n)", 4, HEIGHT-CHARACTER_HEIGHT, 2)
		while True:
			kconf = sys.stdin.read(1)
			if kconf.lower() == 'y':
				break
			elif kconf.lower() == 'n':
				fb.fill_rect(0, HEIGHT-CHARACTER_HEIGHT-2, WIDTH, CHARACTER_HEIGHT+2, 1)
				fb.text("Save cancelled", 4, HEIGHT-CHARACTER_HEIGHT, 2)
				time.sleep(1)
				return
	try:
		with open(fullpath, "w") as f:
			f.write("\n".join(LINES))
		status_msg = f"Saved as {fullpath}"
	except Exception as e:
		status_msg = f"Save error: {e}"
	# Show status message for a moment
	fb.fill_rect(0, HEIGHT-CHARACTER_HEIGHT-2, WIDTH, CHARACTER_HEIGHT+2, 1)
	fb.text(status_msg, 4, HEIGHT-CHARACTER_HEIGHT, 2)
	time.sleep(1)
	
def load_file():
	global LAST_FILENAME
	fname = prompt_filename("Load from")
	if not fname:
		return
	fullpath = "/sd/" + fname
	try:
		with open(fullpath) as f:
			content = f.read()
		lines = content.split("\n")
		if not lines:
			lines = [""]
		global LINES, CURSOR_X, CURSOR_Y
		LINES = lines
		CURSOR_X, CURSOR_Y = 0, 0
		LAST_FILENAME = fname
		status_msg = f"Loaded {fullpath}"
	except Exception as e:
		status_msg = f"Load error: {e}"
	fb.fill_rect(0, HEIGHT-CHARACTER_HEIGHT-2, WIDTH, CHARACTER_HEIGHT+2, 1)
	fb.text(status_msg, 4, HEIGHT-CHARACTER_HEIGHT, 2)
	time.sleep(1)

# Example usage in main loop (to be expanded)
def main():
	global CURSOR_X, CURSOR_Y, LINES
	last_key = None
	while True:
		fb.fill(0)
		draw_text_area()
		draw_status_bar(last_key)
		k = sys.stdin.read(1)
		last_key = k
		# Handle arrow keys (escape sequence)
		if k == '\x1b':
			k2 = sys.stdin.read(1)
			last_key += k2
			if k2 == '[':
				k3 = sys.stdin.read(1)
				last_key += k3
				move_cursor(k3)
		# Basic text entry: printable chars
		elif 32 <= ord(k) <= 126:
			insert_char(k)
		elif k == '\x7f':  # Backspace
			delete_char()
		elif k in ('\r', '\n'):  # Enter (handle both CR and LF)
			insert_newline()
		elif k == '\x13':  # Ctrl-S
			save_file()
		elif k == '\x0c':  # Ctrl-L
			load_file()
		elif k == '\x11':  # Ctrl-Q
			break

main()
