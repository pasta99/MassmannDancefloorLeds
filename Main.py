import threading

from Controller import Controller
from MQTTListener import MQTTListener

if __name__ == "__main__":
    c = Controller()
    listener = MQTTListener(c)
    threading.Thread(target=listener.start).start()
    threading.Thread(target=c.main_loop).start()