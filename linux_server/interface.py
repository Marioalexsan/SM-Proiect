import config
from pybluez import bluetooth

connected_devices = []
socket = bluetooth.BluetoothSocket()

while True:
    devices = bluetooth.discover_devices()

    for device in bluetooth_devices:
        if device in devices:
            bluetooth.connect()
