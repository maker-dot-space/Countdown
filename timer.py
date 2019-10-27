from threading import Timer
import time

class RenewableTimer():

    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.timer = Timer(timeout, callback)

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.start_time = time.time()
        self.timer.start()

    def pause(self):
        self.cancel_time = time.time()
        self.timer.cancel()
        return self.get_actual_time()

    def resume(self):
        self.timeout = self.get_actual_time()
        self.timer = Timer(self.timeout, self.callback)
        self.start_time = time.time()
        self.timer.start()

    def get_actual_time (self):
        return self.timeout - (self.cancel_time - self.start_time)

def printtime():
    print (RenewableTimer.get_actual_time)

t = RenewableTimer(5, printtime())

