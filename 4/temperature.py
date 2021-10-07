import RPi.GPIO as GPIO
from dht11 import DHT11
 
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

thermometer = DHT11(pin = 40)
while True:
	try:
		result = thermometer.read()

		if result.is_valid():
			print("Temperature: %-3.1f C" % result.temperature)
			print("Humidity: %-3.1f %%" % result.humidity)
		else:
			print("Error: %d" % result.error_code)
		
	except:
		pass
	finally:
		GPIO.cleanup()
