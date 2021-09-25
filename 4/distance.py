import RPi.GPIO as GPIO
import time

sleep_time_high = 0.5
sleep_time_low = 0.2

led_pin = 12
ir_pin = 16
ultrasonic_trig_pin = 38
ultrasonic_echo_pin = 37

ir_key = 'IR'
ultrasonic_key = 'Ultrasonic'
half_of_speed_of_sound_const = 34300 / 2
far_away_threshold = 200
sensor_stabilise_time = 0.5

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
				led_blink()
			else:
				GPIO.output(led_pin, True)
				time.sleep(sleep_time_high)

	except:
		GPIO.cleanup()




def get_distance():
	#	Initialise distance and pin
	distance = -1
	GPIO.output(ultrasonic_trig_pin, False)
	time.sleep(sensor_stabilise_time)
	
	GPIO.output(ultrasonic_trig_pin, True)
	time.sleep(0.00001)
	GPIO.output(ultrasonic_trig_pin, False)
	
	while GPIO.input(ultrasonic_echo_pin) == 0:
		t_init = time.time()
	
	while GPIO.input(ultrasonic_echo_pin) == 1:
		t_final = time.time()
		distance = 0
	
	if distance == 0:
		time_taken = t_final - t_init
		distance = round(time_taken * 171500, 2)
	
	return distance



def compute_led_intensity(inputs):
	result = True
	
	if ir_key in inputs:
		inputs[ir_key] = not inputs[ir_key]

	# we require boolean for now
	if ultrasonic_key in inputs:
		inputs[ultrasonic_key] = inputs[ultrasonic_key] <= far_away_threshold

	result = call_model(inputs)

	return result

def call_model(inputs):
	if ultrasonic_key not in inputs:
		inputs[ultrasonic_key] = False

	if ir_key not in inputs:
			inputs[ir_key] = False

	rule_output = (inputs[ultrasonic_key] or inputs[ir_key])

	return rule_output



def led_blink():
	GPIO.output(led_pin, True)
	time.sleep(sleep_time_high)
	GPIO.output(led_pin, False)
	time.sleep(sleep_time_low)



main()
