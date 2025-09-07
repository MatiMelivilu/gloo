import time
from gpiozero.pins.native import NativeFactory
from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero import Device, LED, Button
from signal import pause
		
def ch1Detect():
	print('1000 ch1')
def ch2Detect():
	print('2000 ch2')

def ch3Detect():
	print('5000 ch3')
	
def ch4Detect():
	print('10000 ch4')				
factory = RPiGPIOFactory()
ch1 = Button(2) #antes io13
ch2 = Button(16, pull_up=True, bounce_time=0.1) #antes io6
ch3 = Button(9, pull_up=True, bounce_time=0.1) #antes io 10
ch4 = Button(7, pull_up=True, bounce_time=0.1) #antes io8

ch1.when_pressed = ch1Detect
ch2.when_pressed = ch2Detect
ch3.when_pressed = ch3Detect
ch4.when_pressed = ch4Detect

inib = LED(21)
inib.on()

pause()

