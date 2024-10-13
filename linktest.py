import socket
import struct
import time

MULTICAST_GROUP = '239.192.1.2'
PORT = 50000
INTERFACE = 'eth0'  # Change this to your network interface (e.g., 'wlan0' for Wi-Fi)

def discover_devices(timeout=5):
    devices = set()

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', PORT))

    # Set up the multicast group
    group = socket.inet_aton(MULTICAST_GROUP)
    local_interface = socket.inet_aton('0.0.0.0')
    mreq = struct.pack('4s4s', group, local_interface)
    
    try:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        # Use the correct interface
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(INTERFACE))
    except OSError as e:
        print(f"Failed to set up multicast group: {e}")
        sock.close()
        return []

    sock.settimeout(timeout)
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            try:
                data, address = sock.recvfrom(1024)
                if address not in devices:
                    devices.add(address)
                    print(f"Discovered device: {address} with data: {data}")
            except socket.timeout:
                break
    finally:
        sock.close()

    return list(devices)

if __name__ == "__main__":
    devices = discover_devices()
    if devices:
        for device in devices:
            print(f"Found device at {device}")
    else:
        print("No devices found.")
