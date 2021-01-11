import ASUS.GPIO as GPIO
import time


class Mamos:
    def __init__(self, LED_OK, LED_NG, BTN_input):
        """ Mamos setup"""
        self.LED_OK = LED_OK
        self.LED_NG = LED_NG
        self.BTN_input = BTN_input
        self.prev_input = False

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.ASUS)
            GPIO.setup(LED_OK, GPIO.OUT)
            GPIO.setup(LED_NG, GPIO.OUT)
            GPIO.setup(BTN_input, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except:
            pass

    @staticmethod
    def control(pin):
        """Control GPIO output"""
        GPIO.output(pin, GPIO.HIGH)
        print("LED ON", pin)
        time.sleep(0.1)
        GPIO.output(pin, GPIO.LOW)

    @staticmethod
    def clean():
        """Clean GPIO"""
        GPIO.cleanup()

    def output(self):
        """Input button event"""
        try:
            if not GPIO.input(self.BTN_input) and not self.prev_input:
                print("click")
                self.prev_input = True
                return True
            # elif not GPIO.input(self.BTN_input) and self.prev_input:
            else:
                self.prev_input = False
        except KeyboardInterrupt:
            GPIO.cleanup()  # Get a frame from the video source

        return False
