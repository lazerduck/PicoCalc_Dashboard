# gpio_control.py - Graphical GPIO configuration tool for PicoCalc

import time
import machine
from ui import *
from battery import get_status as get_battery_status


# Pins available on the left-hand side header (see device diagram)
# We include power rails for context (not selectable), and GPIOs as configurable.
LEFT_HEADER_PINS = [
    {"label": "3V3 OUT", "type": "PWR"},
    {"label": "GP2", "type": "GPIO", "gp": 2},
    {"label": "GP3", "type": "GPIO", "gp": 3},
    {"label": "GP4", "type": "GPIO", "gp": 4},
    {"label": "GP5", "type": "GPIO", "gp": 5},
    {"label": "GP21", "type": "GPIO", "gp": 21},
    {"label": "GP28", "type": "GPIO", "gp": 28},
    {"label": "GND", "type": "PWR"},
]


class PinController:
    """Manage mode and state for a single GPIO pin."""

    def __init__(self, label, gp):
        self.label = label
        self.gp = gp
        self.mode = "IN"  # IN | OUT | PWM
        self._pin = None
        self._pwm = None
        self.out_value = 0  # 0/1 for OUT
        self.pwm_duty_pct = 50  # 0..100 for PWM
        self._apply_mode(initial=True)

    # --- hardware control helpers ---
    def _deinit_all(self):
        try:
            if self._pwm:
                self._pwm.deinit()
        except Exception:
            pass
        self._pwm = None
        self._pin = None

    def _apply_mode(self, initial=False):
        """Create underlying machine objects to reflect current mode."""
        # Clean up any previous peripherals
        self._deinit_all()
        try:
            if self.mode == "IN":
                self._pin = machine.Pin(self.gp, machine.Pin.IN)
            elif self.mode == "OUT":
                self._pin = machine.Pin(self.gp, machine.Pin.OUT, value=self.out_value)
            elif self.mode == "PWM":
                pin = machine.Pin(self.gp)
                self._pwm = machine.PWM(pin)
                try:
                    self._pwm.freq(1000)
                except Exception:
                    pass
                self._apply_pwm_duty()
        except Exception:
            # If anything fails (rare), fall back to input to avoid locking the pin
            try:
                self._pin = machine.Pin(self.gp, machine.Pin.IN)
                self.mode = "IN"
            except Exception:
                pass

        # Set a safe default output if we just switched modes
        if not initial and self.mode == "OUT" and self._pin:
            try:
                self._pin.value(self.out_value)
            except Exception:
                pass

    def _apply_pwm_duty(self):
        if not self._pwm:
            return
        # Convert 0..100% to 16-bit duty
        duty_u16 = int(max(0, min(100, self.pwm_duty_pct)) * 65535 / 100)
        try:
            self._pwm.duty_u16(duty_u16)
        except Exception:
            # Some firmwares only support duty_ns; try a fallback
            try:
                # 1 kHz -> 1_000_000 ns period
                period_ns = 1_000_000
                duty_ns = int(period_ns * self.pwm_duty_pct / 100)
                self._pwm.duty_ns(duty_ns)
            except Exception:
                pass

    # --- public controls ---
    def set_mode(self, mode):
        if mode not in ("IN", "OUT", "PWM"):
            return
        if mode == self.mode:
            return
        self.mode = mode
        self._apply_mode()

    def toggle_output(self):
        if self.mode != "OUT" or not self._pin:
            return
        self.out_value = 0 if self.out_value else 1
        try:
            self._pin.value(self.out_value)
        except Exception:
            pass

    def adjust_pwm(self, delta_pct):
        if self.mode != "PWM":
            return
        self.pwm_duty_pct = max(0, min(100, self.pwm_duty_pct + delta_pct))
        self._apply_pwm_duty()

    def read_input(self):
        if self.mode == "IN" and self._pin:
            try:
                return 1 if self._pin.value() else 0
            except Exception:
                return None
        return None

    def cleanup(self):
        self._deinit_all()


def _draw_pin_row(y, pin, selected):
    """Draw a single pin row with left label, line, and mode boxes."""
    # Left label
    label_color = COLOR_CYAN if isinstance(pin, str) else (COLOR_YELLOW if selected else COLOR_WHITE)
    if isinstance(pin, str):
        draw_text(pin, 8, y, COLOR_CYAN)
    else:
        # Selection caret
        if selected:
            draw_text(">", 0, y, COLOR_YELLOW)
        draw_text(pin.label, 8, y, label_color)

    # Connecting line from left margin to option boxes
    draw_line_horizontal(y + 7, 72, 128, COLOR_WHITE)

    # For GPIO rows, draw mode boxes
    if not isinstance(pin, str):
        box_y = y + 2
        boxes = [("IN", 130), ("OUT", 174), ("PWM", 224)]
        for name, x in boxes:
            is_mode = (pin.mode == name)
            # Outline
            draw_rect(x, box_y, 36, 16, COLOR_WHITE, fill=False)
            # Fill if selected mode
            if is_mode:
                color = COLOR_GREEN if name == "IN" else (COLOR_YELLOW if name == "OUT" else COLOR_CYAN)
                fb.fill_rect(x + 1, box_y + 1, 34, 14, color)
            # Text (centered-ish)
            text_color = COLOR_BLACK if is_mode else COLOR_WHITE
            draw_text(name, x + 6, box_y + 4, text_color)

        # Status box at far right
        status_x = 268
        draw_rect(status_x, box_y, 44, 16, COLOR_WHITE, fill=False)
        if pin.mode == "IN":
            v = pin.read_input()
            txt = "HIGH" if v else "LOW"
            col = COLOR_GREEN if v else COLOR_RED
            draw_text(txt, status_x + 6, box_y + 4, col)
        elif pin.mode == "OUT":
            txt = "ON" if pin.out_value else "OFF"
            col = COLOR_YELLOW if pin.out_value else COLOR_WHITE
            draw_text(txt, status_x + 10, box_y + 4, col)
        else:  # PWM
            pct = int(pin.pwm_duty_pct)
            txt = f"{pct:>3}%"
            draw_text(txt, status_x + 6, box_y + 4, COLOR_CYAN)


def show_gpio_control():
    """Interactive GPIO configuration UI."""
    # Build rows: include fixed strings for power rails to align visuals
    rows = []
    for info in LEFT_HEADER_PINS:
        if info["type"] == "PWR":
            rows.append(info["label"])  # string placeholder row
        else:
            rows.append(PinController(info["label"], info["gp"]))

    sel_idx = 0

    while True:
        clear()
        try:
            battery_status = get_battery_status()
        except Exception:
            battery_status = None
        draw_title_bar("GPIO Control", battery_status)

        # Column headers
        draw_text("Pin", 8, 32, COLOR_WHITE)
        draw_text("Mode", 130, 32, COLOR_WHITE)
        draw_text("State", 276, 32, COLOR_WHITE)
        draw_line_horizontal(40, 0, 320, COLOR_WHITE)

        # Rows
        y = 48
        row_h = 24

        # Draw a vertical "header" spine to emulate the physical connector
        # from the left edge into the row lines
        fb.fill_rect(68, 44, 2, 8 + len(rows) * row_h, COLOR_WHITE)

        for i, r in enumerate(rows):
            _draw_pin_row(y + i * row_h, r, selected=(i == sel_idx and not isinstance(r, str)))

        # Help text
        draw_text("UP/DOWN: Select pin  LEFT/RIGHT: Mode", 8, 290, COLOR_YELLOW)
        draw_text("ENTER: Toggle/Apply  +/-: PWM duty  Q: Back", 8, 306, COLOR_YELLOW)

        # Input handling
        key = wait_key_raw()

        if key == 'A':
            # Up
            sel_idx = (sel_idx - 1) % len(rows)
            # Skip non-configurable rows
            while isinstance(rows[sel_idx], str):
                sel_idx = (sel_idx - 1) % len(rows)
        elif key == 'B':
            # Down
            sel_idx = (sel_idx + 1) % len(rows)
            while isinstance(rows[sel_idx], str):
                sel_idx = (sel_idx + 1) % len(rows)
        elif key == 'C':  # Right: next mode
            pin = rows[sel_idx]
            if not isinstance(pin, str):
                pin.set_mode({"IN": "OUT", "OUT": "PWM", "PWM": "IN"}[pin.mode])
        elif key == 'D':  # Left: prev mode
            pin = rows[sel_idx]
            if not isinstance(pin, str):
                pin.set_mode({"IN": "PWM", "PWM": "OUT", "OUT": "IN"}[pin.mode])
        elif key in ('\r', '\n'):  # Enter
            pin = rows[sel_idx]
            if not isinstance(pin, str):
                if pin.mode == "OUT":
                    pin.toggle_output()
                elif pin.mode == "PWM":
                    # Enter Servo Control mode
                    servo_angle = 90  # Start at midpoint
                    min_us = 500
                    max_us = 2500
                    freq = 50
                    running = True
                    # Helper: set PWM for given angle
                    def set_servo_pwm(angle):
                        angle = max(0, min(180, angle))
                        pulse_us = int(min_us + (max_us - min_us) * angle / 180)
                        duty_pct = pulse_us * freq / 10000  # (pulse_us / 20_000us) * 100
                        pin.pwm_duty_pct = duty_pct
                        if pin._pwm:
                            try:
                                pin._pwm.freq(freq)
                            except Exception:
                                pass
                            try:
                                pin._pwm.duty_u16(int(duty_pct * 65535 / 100))
                            except Exception:
                                try:
                                    period_ns = 20_000_000
                                    duty_ns = int(period_ns * duty_pct / 100)
                                    pin._pwm.duty_ns(duty_ns)
                                except Exception:
                                    pass
                        return pulse_us, duty_pct

                    # Set initial position
                    pulse_us, duty_pct = set_servo_pwm(servo_angle)
                    while running:
                        clear()
                        try:
                            battery_status = get_battery_status()
                        except Exception:
                            battery_status = None
                        draw_title_bar(f"Servo Control: {pin.label}", battery_status)
                        center_text(f"Angle: {servo_angle}°", 80, COLOR_CYAN)
                        center_text(f"Pulse: {pulse_us}us", 120, COLOR_YELLOW)
                        center_text(f"Duty: {duty_pct:.2f}% @ 50Hz", 160, COLOR_WHITE)
                        draw_text("UP/DOWN: Move servo", 8, 290, COLOR_YELLOW)
                        draw_text("ENTER: Exit", 8, 306, COLOR_YELLOW)
                        key2 = wait_key_raw()
                        if key2 == 'A':
                            servo_angle = min(180, servo_angle + 5)
                        elif key2 == 'B':
                            servo_angle = max(0, servo_angle - 5)
                        elif key2 in ('\r', '\n'):
                            running = False
                        pulse_us, duty_pct = set_servo_pwm(servo_angle)
                        time.sleep(0.01)
        elif key in ('+', '='):
            pin = rows[sel_idx]
            if not isinstance(pin, str) and pin.mode == "PWM":
                pin.adjust_pwm(+5)
        elif key in ('-', '_'):
            pin = rows[sel_idx]
            if not isinstance(pin, str) and pin.mode == "PWM":
                pin.adjust_pwm(-5)
        elif key in ('q', 'Q'):
            # Cleanup PWM resources
            for r in rows:
                if not isinstance(r, str):
                    r.cleanup()
            return

        # Small delay to keep UI responsive without starving system
        time.sleep(0.01)


if __name__ == "__main__":
    show_gpio_control()
