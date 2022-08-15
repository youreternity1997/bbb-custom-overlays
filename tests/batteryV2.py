import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import time

class BatteryV2:
    def isCharge(self):
        return GPIO.input(self.charge)

    def __init__(self, charge, adc, _callback):
        # Instance Variables
        self.charge = charge
        self.adc = adc
        self.callback = _callback

    def setUp(self):
        # GPIO
        # https://adafruit-beaglebone-io-python.readthedocs.io/en/latest/GPIO.html
        GPIO.setup(self.charge, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(self.charge, GPIO.FALLING)
        GPIO.add_event_callback(self.charge, callback=self.callback)
        
        # ADC
        # https://adafruit-beaglebone-io-python.readthedocs.io/en/latest/ADC.html
        ADC.setup()

    def voltage(self):
        return ADC.read(self.adc) * 1.8

def charge_callback(channel):
    print("callback called for " + channel)

b = BatteryV2("P9_30", "P9_40", charge_callback)
b.setUp()

while True:
    if b.isCharge() == 0:
       break
    time.sleep(1)
    print("voltage " + str(b.voltage()) )

print("exit")
