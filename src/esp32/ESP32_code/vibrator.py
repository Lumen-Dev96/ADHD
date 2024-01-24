import time
import _thread


class VIBRATOR:
    is_working = False

    def __init__(self, pin):
        self.pin = pin
        pin.off()

    def _this_thread(self, mode):
        for i in range(0, len(mode)):
            if i % 2 == 0:
                self.pin.on()
            else:
                self.pin.off()
            time.sleep(mode[i])
        self.pin.off()
        self.is_working = False

    def start(self, mode):
        if not self.is_working:
            self.is_working = True
            try:
                _thread.start_new_thread(self._this_thread, (mode,))
            except:
                print('无法开启线程')
