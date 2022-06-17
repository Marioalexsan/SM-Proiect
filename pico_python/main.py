from machine import Pin, UART, PWM
import time
import dht
import _thread
import sys
import math


class Config:
    BLUETOOTH_TX_PIN = 4
    BLUETOOTH_RX_PIN = 5
    DHT11_DATA_PIN = 15
    LED_DISPLAY_PINS = [ 16, 17, 18, 19, 20 ]
    LED_MODE_PIN = 21
    LED_DISPLAY_COUNT = len(LED_DISPLAY_PINS)
    DHT11_MIN_TEMP = 0
    DHT11_MAX_TEMP = 50
    DHT11_MIN_HUMIDITY = 0
    DHT11_MAX_HUMIDITY = 100
    PWM_FREQUENCY = 500
    UPDATE_INTERVAL_SECONDS = 5


class State:
    running_state = True
    led_display_mode = 0
    temperature = None
    humidity = None


class Objects:
    bluetooth = UART(1, 9600, tx=Pin(Config.BLUETOOTH_TX_PIN), rx=Pin(Config.BLUETOOTH_RX_PIN))
    dht11 = dht.DHT11(Pin(Config.DHT11_DATA_PIN))

    leds_display_pins = [Pin(x, Pin.OUT) for x in Config.LED_DISPLAY_PINS]
    leds_display_pwms = [PWM(x) for x in leds_display_pins]
    led_mode = Pin(Config.LED_MODE_PIN, Pin.OUT)

for x in Objects.leds_display_pwms:
    x.freq(Config.PWM_FREQUENCY)
    x.duty_u16(65535)

def clamp(x, min, max):
    if x < min:
        return min
    if x > max:
        return max
    return x


def update_leds(*, value, min, max, mode):
    fill_ratio = (value - min) / (max - min) * Config.LED_DISPLAY_COUNT
    target_led_index = clamp(math.floor(fill_ratio), 0, Config.LED_DISPLAY_COUNT)
    duty = clamp(math.floor((fill_ratio - target_led_index) * 65535), 0, 65535)

    for i in range(0, target_led_index):
        Objects.leds_display_pwms[i].duty_u16(0)

    for i in range(target_led_index, Config.LED_DISPLAY_COUNT):
        Objects.leds_display_pwms[i].duty_u16(65535)

    if target_led_index != Config.LED_DISPLAY_COUNT:
        # Need to invert since 0 = LED on
        Objects.leds_display_pwms[target_led_index].duty_u16(65535 - duty)

    Objects.led_mode.value(1 if mode == 1 else 0)

# Main Thread - Runs measurement code #

def main():
    while True:
        Objects.dht11.measure()
        [State.temperature, State.humidity] = [Objects.dht11.temperature(), Objects.dht11.humidity()]

        if State.led_display_mode == 1:
            update_leds(value=State.temperature, min=Config.DHT11_MIN_TEMP, max=Config.DHT11_MAX_TEMP, mode=State.led_display_mode)
            State.led_display_mode = 0
        else:
            update_leds(value=State.humidity, min=Config.DHT11_MIN_HUMIDITY, max=Config.DHT11_MAX_HUMIDITY, mode=State.led_display_mode)
            State.led_display_mode = 1

        time.sleep(Config.UPDATE_INTERVAL_SECONDS)

# Side Thread - manages bluetooth connection #

def side():
    try:
        while State.running_state:
            line = Objects.bluetooth.readline()

            if line is None:
                time.sleep(1)
                continue

            args = line.decode('utf-8').rstrip('\r\n').split(' ')

            if len(args) == 0:
                Objects.bluetooth.write(b'No command received!\n')

            if args[0] == 'get' and len(args) >= 2:

                if args[1] == 'temperature':
                    Objects.bluetooth.write(str(State.temperature).encode('utf-8'))

                elif args[1] == 'humidity':
                    Objects.bluetooth.write(str(State.humidity).encode('utf-8'))
                
                else:
                    Objects.bluetooth.write(b'Unknown paramter!')
    
            else:
                Objects.bluetooth.write(b'Unknown command!')

            Objects.bluetooth.write(b'\n')

    except Exception as e:
        print('Quitting due to exception in side thread!')
        print(repr(e))
        State.running_state = False

# Start #

try:
    _thread.start_new_thread(side, ())
    main()

except KeyboardInterrupt as e:
    print('Quitting due to KeyboardInterrupt!')
    print(repr(e))

except Exception as e:
    print('Quitting due to exception!')
    print(repr(e))

# Cleanup #

try:
    for x in Objects.leds_display_pwms:
        x.duty_u16(65535)

    time.sleep(0.05)

    for x in Objects.leds_display_pwms:
        x.deinit()

    Objects.led_mode.value(1)

except Exception as e:
    print('Cleanup exception!')
    print(repr(e))

State.running_state = False