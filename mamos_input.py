# todo config camera bar gui/cv2
import time

TEST_MAMOS = True  # TEST MAMOS mode -> use Mamos's button instead GUI

import ASUS.GPIO as GPIO

LED_OK = 161
LED_NG = 184
BTN_input = 167

GPIO.setwarnings(False)
GPIO.setmode(GPIO.ASUS)
GPIO.setup(LED_OK, GPIO.OUT)
GPIO.setup(LED_NG, GPIO.OUT)
GPIO.setup(BTN_input, GPIO.IN)


def control(pin):
    """Control GPIO output"""
    # if signal:
    GPIO.output(pin, GPIO.HIGH)
    print("LED ON")
    time.sleep(0.1)
    GPIO.output(pin, GPIO.LOW)
    # time.sleep(0.1)


while True:
    print(GPIO.input(BTN_input))

