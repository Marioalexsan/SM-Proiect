from dis import disco
from flask import Flask
import socket
import time
app = Flask(__name__)

module_addr = '98:D3:31:F9:E5:70'
port = 1
s = None

@app.route("/info/<thing>")
def hello_world(thing):
    global s

    if thing != 'temperature' and thing != 'humidity':
        return 'Bad request'

    tries = 3
    success = False
    data = b''
    print('Connecting...')
    while tries > 0:
        try:
            if s is None:
                s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                s.settimeout(8.0)
                s.connect((module_addr, port))

            s.send(b'get ' + thing.encode('utf-8'))

            while True:
                data += s.recv(1024)

                nl = data.find(b'\n')
                if nl != -1:
                    data = data[:nl]
                    break

            success = True
            break
        except Exception as e:
            s = None
            tries -= 1
            if tries > 0:
                print(repr(e))
                print('Failed, retrying...')
                time.sleep(0.1)

    if not success:
        print('Failed, giving up.')
        return 'Can\'t connect'

    print('Success!')
    return data