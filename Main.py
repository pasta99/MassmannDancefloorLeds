import threading
import time
from Controller import Controller
from MQTTListener import MQTTListener
from BeatMaker import BeatMaker

import psutil

def is_connected():
    # Get the network interfaces
    interfaces = psutil.net_if_addrs()
    # Check if any interface is up
    for interface, addresses in interfaces.items():
        stats = psutil.net_if_stats()[interface]
        if stats.isup:
            return True
    return False

if __name__ == "__main__":
    while not is_connected():
        print("Waiting for network...")
        time.sleep(5)

    c = Controller()
    listener = MQTTListener(c)
    l_t = threading.Thread(target=listener.start).start()
    m_l = threading.Thread(target=c.main_loop).start()
    beat_thread = threading.Thread(target=BeatMaker).start()
