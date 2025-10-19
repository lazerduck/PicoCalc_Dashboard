# graph.py - Simple Graphing Calculator for PicoCalc
# Enter y=f(x) at the bottom, graph is drawn above
import time
import picocalc
from picocalc import keyboard
import math

# Display setup
fb = picocalc.display
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 320
GRAPH_HEIGHT = 280
INPUT_HEIGHT = 40

COLOR_BG = 0
COLOR_AXES = 1
COLOR_GRAPH = 3
COLOR_TEXT = 7
COLOR_ERROR = 2

# Graph area: x in [-10, 10], y in [-10, 10] (default)
XMIN, XMAX = -10, 10
YMIN, YMAX = -10, 10

# Parametric mode t range
TMIN, TMAX = -10, 10

 # Map x in [-10,10] to pixel in [0,319]
def x_to_px(x):
    return int((x - XMIN) / (XMAX - XMIN) * (SCREEN_WIDTH - 1))

def px_to_x(px):
    return XMIN + px * (XMAX - XMIN) / (SCREEN_WIDTH - 1)

def y_to_py(y):
    # y=YMAX at top, y=YMIN at bottom
    return int((YMAX - y) / (YMAX - YMIN) * (GRAPH_HEIGHT - 1))

def py_to_y(py):
    return YMAX - py * (YMAX - YMIN) / (GRAPH_HEIGHT - 1)

def draw_axes():
    # Draw axes
    # Y axis
    x0 = x_to_px(0)
    fb.fill_rect(x0, 0, 1, GRAPH_HEIGHT, COLOR_AXES)
    # X axis
    y0 = y_to_py(0)
    fb.fill_rect(0, y0, SCREEN_WIDTH, 1, COLOR_AXES)

    # Draw border
    fb.rect(0, 0, SCREEN_WIDTH, GRAPH_HEIGHT, COLOR_AXES)

def draw_input_line(expr, error=None, mode='normal', expr2=None):
    # Clear input area
    fb.fill_rect(0, GRAPH_HEIGHT, SCREEN_WIDTH, INPUT_HEIGHT, COLOR_BG)
    if mode == 'param':
        fb.text('x(t)=' + (expr or ''), 4, GRAPH_HEIGHT + 4, COLOR_TEXT)
        if expr2 is not None:
            fb.text('y(t)=' + expr2, 4, GRAPH_HEIGHT + 16, COLOR_TEXT)
    else:
        fb.text('y = ' + expr, 4, GRAPH_HEIGHT + 4, COLOR_TEXT)
    if error:
        fb.text(error, 200, GRAPH_HEIGHT + 4, COLOR_ERROR)

def graph_equation(expr):
    fb.fill(COLOR_BG)
    draw_axes()
    # Try to compile the expression
    try:
        code = compile(expr, '<expr>', 'eval')
    except Exception as e:
        draw_input_line(expr, 'Syntax Error')
        fb.show()
        return
    # Draw graph pixel by pixel, updating every 100ms
    points = []
    for px in range(SCREEN_WIDTH):
        x = px_to_x(px)
        try:
            # Provide a safe eval environment with math functions and common built-ins
            env = {'x': x}
            extra = [
                ('abs', abs), ('min', min), ('max', max), ('pow', pow), ('round', round),
                ('int', int), ('float', float), ('sin', math.sin), ('cos', math.cos), ('tan', math.tan),
                ('asin', math.asin), ('acos', math.acos), ('atan', math.atan), ('atan2', math.atan2),
                ('log', math.log), ('log10', math.log10), ('exp', math.exp), ('sqrt', math.sqrt),
                ('pi', math.pi), ('e', math.e), ('floor', math.floor), ('ceil', math.ceil),
                ('sinh', math.sinh), ('cosh', math.cosh), ('tanh', math.tanh),
                ('degrees', math.degrees), ('radians', math.radians),
                ('math', math)
            ]
            for k, v in extra:
                env[k] = v
            y = eval(code, env)
        except Exception:
            continue
        if not isinstance(y, (int, float)) or math.isnan(y) or math.isinf(y):
            continue
        py = y_to_py(y)
        if 0 <= py < GRAPH_HEIGHT:
            points.append((px, py))
        # Draw in batches for animation
        if px % 16 == 0:
            for ppx, ppy in points:
                fb.pixel(ppx, ppy, COLOR_GRAPH)
            fb.show()
            time.sleep_ms(100)
            points = []
    # Draw any remaining points
    for ppx, ppy in points:
        fb.pixel(ppx, ppy, COLOR_GRAPH)
    fb.show()

def graph_parametric(expr_x, expr_y):
    fb.fill(COLOR_BG)
    draw_axes()
    # Try to compile the expressions
    try:
        code_x = compile(expr_x, '<expr_x>', 'eval')
        code_y = compile(expr_y, '<expr_y>', 'eval')
    except Exception as e:
        draw_input_line(expr_x, 'Syntax Error', mode='param', expr2=expr_y)
        fb.show()
        return
    points = []
    N = SCREEN_WIDTH  # Number of steps
    for i in range(N):
        t = TMIN + (TMAX - TMIN) * i / (N - 1)
        try:
            env = {'t': t}
            extra = [
                ('abs', abs), ('min', min), ('max', max), ('pow', pow), ('round', round),
                ('int', int), ('float', float), ('sin', math.sin), ('cos', math.cos), ('tan', math.tan),
                ('asin', math.asin), ('acos', math.acos), ('atan', math.atan), ('atan2', math.atan2),
                ('log', math.log), ('log10', math.log10), ('exp', math.exp), ('sqrt', math.sqrt),
                ('pi', math.pi), ('e', math.e), ('floor', math.floor), ('ceil', math.ceil),
                ('sinh', math.sinh), ('cosh', math.cosh), ('tanh', math.tanh),
                ('degrees', math.degrees), ('radians', math.radians),
                ('math', math)
            ]
            for k, v in extra:
                env[k] = v
            x = eval(code_x, env)
            y = eval(code_y, env)
        except Exception:
            continue
        if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
            continue
        if math.isnan(x) or math.isinf(x) or math.isnan(y) or math.isinf(y):
            continue
        px = x_to_px(x)
        py = y_to_py(y)
        if 0 <= px < SCREEN_WIDTH and 0 <= py < GRAPH_HEIGHT:
            points.append((px, py))
        # Draw in batches for animation
        if i % 16 == 0:
            for ppx, ppy in points:
                fb.pixel(ppx, ppy, COLOR_GRAPH)
            fb.show()
            time.sleep_ms(100)
            points = []
    for ppx, ppy in points:
        fb.pixel(ppx, ppy, COLOR_GRAPH)
    fb.show()

def main():
    mode = 'normal'  # 'normal' or 'param'
    expr = "sin(x)*cos(x/2) + exp(-x**2/10)"
    expr2 = "sin(t)"  # default y(t) for parametric
    input_buffer = list(expr)
    input_buffer2 = list(expr2)
    cursor = len(input_buffer)
    cursor2 = len(input_buffer2)
    temp = bytearray(1)

    while True:
        fb.fill(COLOR_BG)
        draw_axes()
        if mode == 'param':
            draw_input_line(''.join(input_buffer), mode='param', expr2=''.join(input_buffer2))
        else:
            draw_input_line(''.join(input_buffer))
        fb.show()
        # Input loop for editing
        editing = True
        editing_y = False  # For parametric: editing y(t)
        while editing:
            if keyboard.readinto(temp):
                key = temp[0]
                # Handle ANSI escape sequence for arrow keys (ESC [ C or ESC [ D)
                if key == 27:  # ESC
                    # Read next two bytes for full sequence
                    seq = bytearray(2)
                    if keyboard.readinto(seq):
                        if seq[0] == ord('['):
                            if seq[1] == ord('C'):  # Right arrow
                                if mode == 'param' and editing_y:
                                    if cursor2 < len(input_buffer2):
                                        cursor2 += 1
                                else:
                                    if cursor < len(input_buffer):
                                        cursor += 1
                            elif seq[1] == ord('D'):  # Left arrow
                                if mode == 'param' and editing_y:
                                    if cursor2 > 0:
                                        cursor2 -= 1
                                else:
                                    if cursor > 0:
                                        cursor -= 1
                    continue  # Don't insert ESC or '['
                if key in (ord('\r'), ord('\n')):
                    if mode == 'param' and not editing_y:
                        editing_y = True
                        continue
                    editing = False
                elif key in (8, 127):  # Backspace
                    if mode == 'param' and editing_y:
                        if cursor2 > 0:
                            input_buffer2.pop(cursor2-1)
                            cursor2 -= 1
                    else:
                        if cursor > 0:
                            input_buffer.pop(cursor-1)
                            cursor -= 1
                elif key == 3:  # Ctrl+C (clear input)
                    if mode == 'param' and editing_y:
                        input_buffer2 = []
                        cursor2 = 0
                    else:
                        input_buffer = []
                        cursor = 0
                elif key in (ord('q'), ord('Q')):
                    return
                elif key == ord('m'):  # Toggle mode
                    if mode == 'normal':
                        mode = 'param'
                        editing_y = False
                        input_buffer = list("cos(2*t)*(1+0.5*sin(5*t))")
                        input_buffer2 = list("sin(2*t)*(1+0.5*sin(5*t))")
                        cursor = len(input_buffer)
                        cursor2 = len(input_buffer2)
                    else:
                        mode = 'normal'
                        input_buffer = list(expr)
                        cursor = len(input_buffer)
                elif 32 <= key <= 126:
                    if mode == 'param' and editing_y:
                        input_buffer2.insert(cursor2, chr(key))
                        cursor2 += 1
                    else:
                        input_buffer.insert(cursor, chr(key))
                        cursor += 1
            # Draw cursor
            if mode == 'param':
                draw_input_line(''.join(input_buffer), mode='param', expr2=''.join(input_buffer2))
                if editing_y:
                    # Cursor for y(t) on second line
                    cursor_x = 4 + 6 * len('y(t)=' + ''.join(input_buffer2[:cursor2]))
                    cursor_y = GRAPH_HEIGHT + 16
                else:
                    # Cursor for x(t) on first line
                    cursor_x = 4 + 6 * len('x(t)=' + ''.join(input_buffer[:cursor]))
                    cursor_y = GRAPH_HEIGHT + 4
                fb.fill_rect(cursor_x, cursor_y, 6, 8, COLOR_TEXT)
            else:
                draw_input_line(''.join(input_buffer))
                cursor_x = 4 + 6 * len('y = ' + ''.join(input_buffer[:cursor]))
                fb.fill_rect(cursor_x, GRAPH_HEIGHT + 4, 6, 8, COLOR_TEXT)
            fb.show()
            time.sleep_ms(30)
        # Graph the equation
        if mode == 'param':
            graph_parametric(''.join(input_buffer), ''.join(input_buffer2))
        else:
            graph_equation(''.join(input_buffer))
        # Wait for any key to return to input
        while not keyboard.readinto(temp):
            pass

if __name__ == "__main__":
    main()
