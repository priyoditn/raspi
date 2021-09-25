import RPi.GPIO as GPIO
import time

sleep_time = 0.5

led_pin = 12
ir_pin = 16

ir_key = 'IR'

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(ir_pin, GPIO.IN)


def main():
	try:
		while True:
			ir_output = GPIO.input(ir_pin)
			ir_status = 'Object detected'

			if ir_output:
				ir_status = 'Surroundings clear'

			print(f"IR Sensor: {ir_status}")

			sensor_data = {ir_key:ir_output}
			
			output = compute_led_intensity(sensor_data)			

			if ir_output:
				led_blink(sleep_time)
			else:
				GPIO.output(led_pin, True)
				time.sleep(sleep_time)

	except KeyboardInterrupt:
		GPIO.cleanup()


def compute_led_intensity(inputs):
	ir_output = not inputs[ir_key]

	return ir_output



def led_blink(sleep_time):
	GPIO.output(led_pin, True)
	time.sleep(sleep_time)
	GPIO.output(led_pin, False)
	time.sleep(sleep_time)



main()
