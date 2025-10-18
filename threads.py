import _thread, time, sys

running = True
def bg():
    while running:
        # do a tiny bit of work
        time.sleep(0.01)

_thread.start_new_thread(bg, ())
time.sleep(0.2)
running = False
print("Background ran OK")