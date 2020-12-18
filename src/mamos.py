import ASUS.GPIO as GPIO
import time


class Mamos:
    def __init__(self, LED_OK, LED_NG, BTN_input):
        self.LED_OK = LED_OK
        self.LED_NG = LED_NG
        self.BTN_input = BTN_input
        self.prev_input = False

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.ASUS)
            GPIO.setup(LED_OK, GPIO.OUT)
            # todo test 1 pin
            # GPIO.setup(LED_NG, GPIO.OUT)
            GPIO.setup(BTN_input, GPIO.IN)
        except:
            pass

    @staticmethod
    def control(pin):
        """Control GPIO output"""
        GPIO.output(pin, GPIO.HIGH)
        print("LED ON")
        time.sleep(0.1)
        GPIO.output(pin, GPIO.LOW)

    @staticmethod
    def clean():
        GPIO.cleanup()

    def output(self):
        try:
            if not GPIO.input(self.BTN_input) and not self.prev_input:
                print("click")
                self.prev_input = True
                return True
            elif GPIO.input(self.BTN_input) and self.prev_input:
                self.prev_input = False
        except KeyboardInterrupt:
            GPIO.cleanup()  # Get a frame from the video source

        return False
