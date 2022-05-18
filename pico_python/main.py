# Imports #

from machine import Pin, UART
import time
import dht
import _thread
import sys


# Pin Configuration #

bt_tx_pin = 4
bt_rx_pin = 5
dht11_pin = 6
led_status_pin = 16

# Functionality #

bt = UART(1, 9600, tx=Pin(bt_tx_pin), rx=Pin(bt_rx_pin))
d = dht.DHT11(Pin(dht11_pin))
led_status = Pin(led_status_pin, Pin.OUT)

# Initialization #

led_status.value(1)

# Main Thread #

def main():
    while True:
        d.measure()
        t = d.temperature()
        h = d.humidity()
        print('Temperature is ', t)
        print('Humidity is ', h)

        # Write status
        bt.write(('Temperature = {}, Humidity = {}\n'.format(str(t), str(h))).encode('utf-8'))

        time.sleep(5)

# Side Thread #

def side(stop_condition):
    while running_state:
        time.sleep(1)
        
        # Toggle Status LED
        led_status.value(1 - led_status.value())


# Start #

running_state = True

try:
    _thread.start_new_thread(side, (running_state, ))
    main()

# Cleanup #

except KeyboardInterrupt:
    print('Quitting due to KeyboardInterrupt!')

except:
    print('Quitting due to exception!')

running_state = False

