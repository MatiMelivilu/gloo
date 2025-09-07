# gpio_config.py
from gpiozero import Device, LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory

Device.pin_factory = PiGPIOFactory()

class GPIOConfig:
    def __init__(self):
        self.ch1 = Button(12, pull_up=True, bounce_time=0.1)
        self.ch2 = Button(16, pull_up=True, bounce_time=0.1)
        self.ch3 = Button(9, pull_up=True, bounce_time=0.1)
        self.ch4 = Button(7, pull_up=True, bounce_time=0.1)
        self.inhibit = LED(21)

        self.inhibit.on()  # Inhibir el monedero por defecto
