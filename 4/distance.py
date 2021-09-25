import RPi.GPIO as GPIO
import time

sleep_time = 0.5

led_pin = 12
ir_pin = 16
ultrasonic_trig_pin = 38
ultrasonic_echo_pin = 40

ir_key = 'IR'
ultrasonic_key = 'Ultrasonic'
half_of_speed_of_sound_const = 34300 / 2
far_away_threshold = 10000

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(ir_pin, GPIO.IN)
GPIO.setup(ultrasonic_echo_pin, GPIO.IN)
GPIO.setup(ultrasonic_trig_pin, GPIO.OUT)


def main():
	try:
		while True:
			ir_output = GPIO.input(ir_pin)
			ir_status = 'Object detected'

			if ir_output:
				ir_status = 'Surroundings clear'

			ultrasonic_data = get_distance()

			sensor_data = {ir_key:ir_output
						, ultrasonic_key: ultrasonic_data}
			
			output = compute_led_intensity(sensor_data)

			print(f"IR Sensor: {ir_status}\tUltrasonic Sensor: {ultrasonic_data}\tOutput: {output}")

			if output:
				led_blink(sleep_time)
			else:
				GPIO.output(led_pin, True)
				time.sleep(sleep_time)

	except KeyboardInterrupt:
		GPIO.cleanup()



def get_distance():
	GPIO.output(ultrasonic_trig_pin, True)
	time.sleep(0.00001)
	GPIO.output(ultrasonic_trig_pin, False)
	
	object_found = False
	time_taken = time.time()
	
	if GPIO.input(ultrasonic_echo_pin):
		time_taken = time.time() - time_taken
		object_found = True
	
	if object_found:
		distance = time_taken * half_of_speed_of_sound_const
	else:
		distance = far_away_threshold
	
	return distance



def compute_led_intensity(inputs):
	result = True
	
	if ir_key in inputs:
		inputs[ir_key] = not inputs[ir_key]

	# we require boolean for now
	if ultrasonic_key in inputs:
		inputs[ultrasonic_key] = inputs[ultrasonic_key] < far_away_threshold

	result = call_model(inputs)

	return result

def call_model(inputs):
	if ultrasonic_key not in inputs:
		inputs[ultrasonic_key] = False

	if ir_key in inputs:
			inputs[ir_key] = False

	rule_output = inputs[ultrasonic_key] or inputs[ir_key]

	return rule_output



def led_blink(sleep_time):
	GPIO.output(led_pin, True)
	time.sleep(sleep_time)
	GPIO.output(led_pin, False)
	time.sleep(sleep_time)



main()
