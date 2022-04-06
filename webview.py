from random import random
import time
from threading import Thread, Lock
from queue import Queue
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# from RPi.GPIO import GPIO
# from w1thermsensor import W1ThermSensor, Unit

def content_type(path: str):
    extmap = {
        '.css': 'text/css',
        '.js': 'text/js',
        '.html': 'text/html',
        '.ico': 'image/vnd.microsoft.icon'
    }

    for k, v in extmap.items():
        if path.endswith(k):
            return v
    return None


class RPiHandler:
    def __init__(self):
        self.led = 15

    def __enter__(self):
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(self.led, GPIO.OUT)
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        # GPIO.cleanup()
        return

    def get_temperatures(self):
        # sensors = W1ThermSensor.get_available_sensors()
        # temperatures = [x.get_temperature(Unit.DEGREES_C) for x in sensors]
        temperatures = [random() for x in range(0, 2)]
        return temperatures

    def set_led(self, value):
        # GPIO.output(self.led, value)
        return


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        file_map = {
            '/style.css': 'website/style.css',
            '/script.js': 'website/script.js',
            '/favicon.ico': 'website/favicon.ico',
            '/': 'website/index.html'
        }

        if self.path in file_map:
            path = file_map[self.path]
            try:
                with open(path, 'rb') as file:
                    data = file.read()
                    self.send_response(200)
                    self.send_header('Content-Type', content_type(path))
                    self.send_header('Content-Length', str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
            except:
                self.send_error(500)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/get-temp':
            self.POST_get_temp()
        else:
            self.send_error(404)

    def POST_get_temp(self):
        data = 'Temperature readings:'
        data += '<ul>'

        with self.server.data_lock:
            for x in self.server.temp_history[-20:-1]:
                data += f'<li> {x["time"]}, {x["temps"]} </li>'

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data.encode('utf-8'))


class RpiServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int]) -> None:
        super().__init__(server_address, WebHandler)
        self.http_thread: Thread = None
        self.rpi_thread: Thread = None
        self.active = False
        self.activity_lock = Lock()
        self.data_lock = Lock()
        self.temp_history: list[dict] = []
        self.max_temp_count = 5

    def start(self):
        with self.activity_lock:
            if self.active:
                return

            self.active = True

            self.http_thread = Thread(target=self.__thread_http)
            self.rpi_thread = Thread(target=self.__thread_rpi)

            self.http_thread.start()
            self.rpi_thread.start()

    def stop(self):
        with self.activity_lock:
            if not self.active:
                return

            self.active = False
            self.shutdown()
            
            self.http_thread.join()
            self.rpi_thread.join()

    
    def __thread_http(self):
        self.serve_forever()

    def __thread_rpi(self):
        rpi = RPiHandler()
        with rpi:
            while self.active:
                time.sleep(1.0)
                with self.data_lock:
                    self.temp_history.append({'time': time.time(), 'temps': rpi.get_temperatures()})
                    if len(self.temp_history) > self.max_temp_count:
                        self.temp_history = self.temp_history[-self.max_temp_count:]


def main():
    try:
        print('Starting...')

        server = RpiServer(('', 8080))
        server.start()

        print('Started!')

        while True:
            time.sleep(1000)
    
    except KeyboardInterrupt:
        print('Closing...')
        server.stop()
        print('Bye!')


if __name__ == '__main__':
    main()