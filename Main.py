import threading
import time
from Controller import Controller
from MQTTListener import MQTTListener

if __name__ == "__main__":
    c = Controller()
    time.sleep(20)
    listener = MQTTListener(c)
    l_t = threading.Thread(target=listener.start).start()
    m_l = threading.Thread(target=c.main_loop).start()
