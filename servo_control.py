# servo_control.py - Multi-servo dashboard for PicoCalc
import time
import machine
from ui import *
from battery import get_status as get_battery_status

SERVO_PINS = [
    {"label": "GP2", "gp": 2},
    {"label": "GP3", "gp": 3},
    {"label": "GP4", "gp": 4},
    {"label": "GP5", "gp": 5},
    {"label": "GP21", "gp": 21},
    {"label": "GP28", "gp": 28},
]

class Servo:
    def __init__(self, label, gp):
        self.label = label
        self.gp = gp
        self.angle = 90  # Start at midpoint
        self._pwm = None
        self._init_pwm()
    def _init_pwm(self):
        try:
            pin = machine.Pin(self.gp)
            self._pwm = machine.PWM(pin)
            self._pwm.freq(50)
            self.set_angle(self.angle)
        except Exception:
            self._pwm = None
    def set_angle(self, angle):
        self.angle = max(0, min(180, angle))
        min_us = 500
        max_us = 2500
        pulse_us = int(min_us + (max_us - min_us) * self.angle / 180)
        duty_pct = pulse_us * 50 / 10000  # (pulse_us / 20_000us) * 100
        if self._pwm:
            try:
                self._pwm.duty_u16(int(duty_pct * 65535 / 100))
            except Exception:
                try:
                    period_ns = 20_000_000
                    duty_ns = int(period_ns * duty_pct / 100)
                    self._pwm.duty_ns(duty_ns)
                except Exception:
                    pass
        return pulse_us, duty_pct
    def cleanup(self):
        try:
            if self._pwm:
                self._pwm.deinit()
        except Exception:
            pass
        self._pwm = None

def show_servo_control():
    servos = [Servo(info["label"], info["gp"]) for info in SERVO_PINS]
    sel_idx = 0
    running = True
    while running:
        clear()
        try:
            battery_status = get_battery_status()
        except Exception:
            battery_status = None
        draw_title_bar("Servo Control", battery_status)
        draw_text("Pin", 8, 32, COLOR_WHITE)
        draw_text("Angle", 80, 32, COLOR_WHITE)
        draw_text("Pulse", 160, 32, COLOR_WHITE)
        draw_text("Duty", 240, 32, COLOR_WHITE)
        draw_line_horizontal(40, 0, 320, COLOR_WHITE)
        y = 48
        row_h = 32
        for i, s in enumerate(servos):
            selected = (i == sel_idx)
            color = COLOR_YELLOW if selected else COLOR_WHITE
            draw_text(s.label, 8, y + i * row_h, color)
            ang = s.angle
            pulse_us, duty_pct = s.set_angle(ang)
            draw_text(f"{ang:3d}°", 80, y + i * row_h, color)
            draw_text(f"{pulse_us}us", 160, y + i * row_h, COLOR_CYAN)
            draw_text(f"{duty_pct:.2f}%", 240, y + i * row_h, COLOR_GREEN)
        draw_text("UP/DOWN: Select  LEFT/RIGHT: Angle", 8, 290, COLOR_YELLOW)
        draw_text("Q: Exit", 8, 306, COLOR_YELLOW)
        key = wait_key_raw()
        if key == 'A':
            sel_idx = (sel_idx - 1) % len(servos)
        elif key == 'B':
            sel_idx = (sel_idx + 1) % len(servos)
        elif key == 'C':
            s = servos[sel_idx]
            s.set_angle(s.angle + 5)
        elif key == 'D':
            s = servos[sel_idx]
            s.set_angle(s.angle - 5)
        elif key in ('q', 'Q'):
            running = False
        time.sleep(0.01)
    for s in servos:
        s.cleanup()

if __name__ == "__main__":
    show_servo_control()
