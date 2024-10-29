import threading
import time
from Controller import Controller
from MQTTListener import MQTTListener
from BeatMaker import BeatMaker

if __name__ == "__main__":
    c = Controller()
    # time.sleep(1)
    listener = MQTTListener(c)
    l_t = threading.Thread(target=listener.start).start()
    m_l = threading.Thread(target=c.main_loop).start()
    beat_thread = threading.Thread(target=BeatMaker).start()
