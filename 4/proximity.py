import RPi.GPIO as GPIO
import time

sleep_time = 0.5

led_pin = 12
ir_pin = 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(ir_pin, GPIO.IN)

def led_blink(sleep_time):
	GPIO.output(led_pin, True)
	time.sleep(sleep_time)
	GPIO.output(led_pin, False)
	time.sleep(sleep_time)

try:
	while True:
		if GPIO.input(ir_pin):
			led_blink(sleep_time)
		else:
			GPIO.output(led_pin, True)
			time.sleep(sleep_time)

except KeyboardInterrupt:
	GPIO.cleanup()
