import ASUS.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.ASUS)
LED = 164
GPIO.setup(LED,GPIO.OUT)

BTN_input = 167
# [167, 160, 162]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.ASUS)
GPIO.setup(164, GPIO.OUT)
GPIO.setup(167, GPIO.IN)

def control(pin, signal):
    if signal:
        GPIO.output(pin, GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.LOW)
    time.sleep(1)

try:
    while True:
        if GPIO.input(BTN_input):
            control(pin=LED, signal=True)
        else:
            control(pin=LED, signal=False)
except KeyboardInterrupt:
    GPIO.cleanup()