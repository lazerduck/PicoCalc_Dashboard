import mp3, time, vtterminal
from machine import UART

uart = UART(0, 115200)

def _drain_uart():
    while uart.any():
        uart.read(1)

def play_music(path):
    mp3.init(pin_l=26, pin_r=27)
    mp3.load(path)
    mp3.play()

    _drain_uart()

    try:
        while mp3.state() == "playing":
            if hasattr(mp3, "poll"):
                mp3.poll()

            if uart.any():                    # non-blocking
                ch = uart.read(1)             # bytes
                if ch:
                    vtterminal.printChar(ch[0])
                    mp3.stop()
                    break

            time.sleep(0.005)
    finally:
        mp3.stop()