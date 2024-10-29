import time

class ManualBeatMaker:
    def __init__(self, callback, bpm) -> None:
        self.callback = callback 
        self.set_bpm(bpm)
        self.running = True
    
    def set_bpm(self, bpm):
        if bpm == 0:
            bpm = 0.1
        self.waiting_time = 60 / bpm

    def start(self):
        self.running = True
    
    def stop(self):
        self.running = False

    def main_loop(self):
        while True: 
            while (self.running):
                self.callback(self.waiting_time)
                print("Sent beat")
                time.sleep(self.waiting_time)
            time.sleep(1/20)