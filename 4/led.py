import RPi.GPIO as GPIO
import time

sleep_time = 0.5

led_pin = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)

def led_blink(sleep_time):
	GPIO.output(led_pin, True)
	time.sleep(sleep_time)
	GPIO.output(led_pin, False)
	time.sleep(sleep_time)

try:
	while True:
		led_blink(sleep_time)

except KeyboardInterrupt:
	GPIO.cleanup()
