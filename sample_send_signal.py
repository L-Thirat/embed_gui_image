import ASUS.GPIO as GPIO
import time

LED = 164
BTN_input = 167

GPIO.setwarnings(False)
GPIO.setmode(GPIO.ASUS)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BTN_input, GPIO.IN)


def control(pin, signal):
    if signal:
        GPIO.output(pin, GPIO.HIGH)
        print("ON")
    else:
        GPIO.output(pin, GPIO.LOW)
        print("OFF")
    time.sleep(1)


try:
    while True:
        if GPIO.input(BTN_input):
            control(pin=LED, signal=False)  # is pressed
        else:
            control(pin=LED, signal=True)  # is not pressed
except KeyboardInterrupt:
    GPIO.cleanup()
