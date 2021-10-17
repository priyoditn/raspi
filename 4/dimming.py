import dht11
import RPi.GPIO as GPIO
import time

from datetime import date, datetime
from pathlib import Path
import math
import pickle
import numpy as np




sleep_time_high = 0.5
model_filename = r'/home/pi/code/raspi/4/models/zing_brightness_v0.pkl'

#	motor pins
motor_in1 = 11
motor_in2 = 13
motor_in3 = 15
motor_in4 = 35

#	motor pins
motor_in1 = 11
motor_in2 = 13
motor_in3 = 15
motor_in4 = 35

led_pin = 12
ir_pin = 16
ultrasonic_trig_pin = 38
ultrasonic_echo_pin = 37
internal_ldr_pin = 32
external_ldr_pin = 29
dht11_pin = 40

ir_key = 'IR'
ultrasonic_key = 'Ultrasonic'
internal_ldr_key = 'internal LDR'
external_ldr_key = 'external LDR'
temperature_key = 'DHT 11 temperature'
humidity_key = 'DHT 11 humidity'

half_of_speed_of_sound = 343000 / 2 # mm/sec
ultrasonic_trigger_interval = 0.00001 # sec
far_away_threshold = 200 # mm
sensor_stabilise_time = 0.5
#min_ai_luminosity = 80
#max_ai_luminosity = 90
pwm_frequency = 1000	#   hertz.
dimming_interval = 5
brightening_interval = 2
luminosity_steps = 100
ldr_max = 700
ldr_min = 90

#	--------------------
#	motor params
step_sleep = 0.004 #	ms

# For motor 28BYJ-48 and driver ULN2003
step_sequence = [
					[1,0,0,1],
					[1,0,0,0],
					[1,1,0,0],
					[0,1,0,0],
					[0,1,1,0],
					[0,0,1,0],
					[0,0,1,1],
					[0,0,0,1]
				]

#	--------------------

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(ir_pin, GPIO.IN)
GPIO.setup(ultrasonic_echo_pin, GPIO.IN)
GPIO.setup(ultrasonic_trig_pin, GPIO.OUT)
# LDR pin setup occurs inside the ldr() method


GPIO.setup(motor_in1, GPIO.OUT)
GPIO.setup(motor_in2, GPIO.OUT)
GPIO.setup(motor_in3, GPIO.OUT)
GPIO.setup(motor_in4, GPIO.OUT)

GPIO.output(motor_in1, GPIO.LOW)
GPIO.output(motor_in2, GPIO.LOW)
GPIO.output(motor_in3, GPIO.LOW)
GPIO.output(motor_in4, GPIO.LOW)
motor_pins = [motor_in1, motor_in2, motor_in3, motor_in4]

brightness_model = pickle.load(open(model_filename, 'rb'))

log_file_loc = "/home/pi/log/"

sensor_status_path = '/home/pi/code/raspi/4/persist_sensor_status.txt'




def main():
	pwm = GPIO.PWM(led_pin, pwm_frequency)
	pwm.start(0)
	brightness = 100
	logfile = None
	dht11_sensor = dht11.DHT11(pin = dht11_pin)
	prev_temperature = 26.8
	prev_humidity = 78.0
	
	reset_motor()
	
	try:
		logfile = initialise_log()
		print("Timestamp\tIR Status\tUltrasonic Status\tInternal Incident Radiation\tExternal Incident Radiation\tTemperature\tHumidity\tHeadcount\tBrightness Level")
		
		while True:
			ir_output = GPIO.input(ir_pin)

			ultrasonic_data = get_distance()
			
			internal_ldr_data = ldr(internal_ldr_pin)
			external_ldr_data = ldr(external_ldr_pin)
			
			temperature, humidity = measure_temperature_humidity(dht11_sensor)
			
			if temperature == 0:
				temperature = prev_temperature
			
			if humidity == 0:
				humidity = prev_humidity
			
			prev_temperature = temperature
			prev_humidity = humidity
			
			sensor_data = {ir_key : ir_output
						, ultrasonic_key : ultrasonic_data
						, internal_ldr_key : internal_ldr_data
						, external_ldr_key : external_ldr_data
						, temperature_key: temperature
						, humidity_key: humidity}
			
			output = decide(sensor_data)
			
			headcount = 0
			
			if output == 100:
				headcount = 1
			
			print(f"{datetime.now().strftime('%H:%M:%S')}\t{ir_output}\t{ultrasonic_data}\t{internal_ldr_data}\t{external_ldr_data}\t{temperature}\t{humidity}\t{headcount}\t{output}")
			
			logfile.write(f"{datetime.now().strftime('%H:%M:%S')}\t{ir_output}\t{ultrasonic_data}\t{internal_ldr_data}\t{external_ldr_data}\t{temperature}\t{humidity}\t{headcount}\t{output}\n")
			
			prev_brightness = brightness
			brightness = output
			
			dim_led(pwm, brightness, prev_brightness)
			
	except KeyboardInterrupt:
		pass
	finally:
		GPIO.cleanup()
		logfile.close()




def reset_motor():
	print("~~~~ resetting windows blinds to 0° ...")
	
	motor_angular_displacement = 0
	
	with open(sensor_status_path, 'r') as fileHandler:
		motor_angular_displacement = int(fileHandler.read())
	
	if motor_angular_displacement > 0:
		with open(sensor_status_path, 'w') as fileHandler:
			fileHandler.write('0')
		run_motor(motor_angular_displacement, False)


def decide(sensor_data):
	rotate_motor(sensor_data[external_ldr_key])
	output = compute_intensity_and_postprocess(sensor_data)
	return output



def compute_intensity_and_postprocess(sensor_data):
	output = predict_brightness(sensor_data)
	
	return output



def rotate_motor(external_luminosity):
	motor_angular_displacement = int((90 * external_luminosity) / 100)
	
	with open(sensor_status_path, 'r') as fileHandler:
		prev_motor_angular_displacement = int(fileHandler.read())
	
	diff = abs(motor_angular_displacement - prev_motor_angular_displacement)
	
	if diff >= 10:
		run_motor(diff, motor_angular_displacement > prev_motor_angular_displacement)
		
		with open(sensor_status_path, 'w') as fileHandler:
			fileHandler.write(str(motor_angular_displacement))




def measure_temperature_humidity(dht11_sensor):
	result = dht11_sensor.read()
	humidity, temperature = result.humidity, result.temperature
	
	return temperature, humidity



def ldr(ldr_pin):
	GPIO.setup(ldr_pin, GPIO.OUT)
	GPIO.output(ldr_pin, GPIO.LOW)
	time.sleep(0.1)
	
	GPIO.setup(ldr_pin, GPIO.IN)
	
	t0 = time.time_ns()
	
	while (GPIO.input(ldr_pin) == GPIO.LOW):
		pass
	
	t1 = time.time_ns()
	
	diff = math.log(t1 - t0)
	diff = diff * diff
	
	scaled_value = ((diff - ldr_max) * 100) / (ldr_min - ldr_max)
	
	if scaled_value > 100:
		scaled_value = 100
	elif scaled_value < 25:
		scaled_value = 25
	
	scaled_value = (scaled_value - 25) * 100 / (75)
	scaled_value = round(scaled_value, 2)
	
	return scaled_value



def motor_cleanup():
	GPIO.output( motor_in1, GPIO.LOW )
	GPIO.output( motor_in2, GPIO.LOW )
	GPIO.output( motor_in3, GPIO.LOW )
	GPIO.output( motor_in4, GPIO.LOW )



def run_motor(angle, direction):
	motor_step_counter = 0
	
	#	4096 steps is 360° <=> 5.625*(1/64) per step,
	step_count = int(angle * 4096 / 360)
	
	try:
		for i in range(step_count):
			for pin in range(0, len(motor_pins)):
				GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
			
			if direction == True: # anticlockwise
				motor_step_counter = (motor_step_counter - 1) % 8
			elif direction == False: # clockwise
				motor_step_counter = (motor_step_counter + 1) % 8
			else:
				print("direction must be True / False only. Other value was provided.")
				
				break
			
			time.sleep(step_sleep)
	 
	except KeyboardInterrupt:
		pass
	finally:
		motor_cleanup()



def motor_cleanup():
	GPIO.output( motor_in1, GPIO.LOW )
	GPIO.output( motor_in2, GPIO.LOW )
	GPIO.output( motor_in3, GPIO.LOW )
	GPIO.output( motor_in4, GPIO.LOW )



def run_motor(angle, direction):
	motor_step_counter = 0
	
	#	4096 steps is 360° <=> 5.625*(1/64) per step,
	step_count = int(angle * 4096 / 360)
	
	try:
		for i in range(step_count):
			for pin in range(0, len(motor_pins)):
				GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
			if direction == True: # anticlockwise
				motor_step_counter = (motor_step_counter - 1) % 8
			elif direction == False: # clockwise
				motor_step_counter = (motor_step_counter + 1) % 8
			else:
				print("direction must be True / False only. Other value was provided.")
				motor_cleanup()
			
			time.sleep(step_sleep)
	 
	except KeyboardInterrupt:
		pass
	finally:
		motor_cleanup()



def initialise_log():
	today = date.today()
	d = today.strftime("%Y-%m-%d")
	logfileName = log_file_loc + d + ".log"
	f = Path(logfileName)
	fileExists = f.exists()
	
	logfile = open(logfileName, "a")
	
	if not fileExists:
		logfile.write("Timestamp\tIR Status\tUltrasonic Status\tInternal Incident Radiation\tExternal Incident Radiation\tTemperature\tHumidity\tHeadcount\tBrightness Level\n")
		
	return logfile


def normalise_brightness(level):
	if level > 100:
		level = 100
	elif level == 0:
		level = 10
	elif level < 0:
		level = 0
		
	return level


def dim_led(pwm, brightness, prev_brightness):
	if brightness == prev_brightness:
		time.sleep(sleep_time_high)
		return
	
	brightness = int(round(normalise_brightness(brightness), 0))
	prev_brightness = int(round(normalise_brightness(prev_brightness), 0))
	
	transition_interval = brightening_interval
	
	if brightness < prev_brightness:
		transition_interval = dimming_interval
		
	delta = brightness - prev_brightness
	stay_interval = transition_interval * 1.0 / luminosity_steps
	step = int(delta * 1.0 / luminosity_steps)
	
	if delta != 0:
		if step == 0:
			if delta < 0:
				step = -1
			else:
				step = 1
			stay_interval = step * 1.0 / delta
		
		brightness += step
		
		if brightness > 100:
			brightness = 101
		
		for i in range(prev_brightness, brightness, step):
			pwm.ChangeDutyCycle(i)
			time.sleep(stay_interval)
		
		brightness += step
		
		if brightness > 100:
			brightness = 101
		
		for i in range(prev_brightness, brightness, step):
			pwm.ChangeDutyCycle(i)
			time.sleep(stay_interval)



def get_distance():
	#   Initialise distance and pin
	distance = -1
	GPIO.output(ultrasonic_trig_pin, False)
	time.sleep(sensor_stabilise_time)
	
	GPIO.output(ultrasonic_trig_pin, True)
	time.sleep(ultrasonic_trigger_interval)
	GPIO.output(ultrasonic_trig_pin, False)
	
	while GPIO.input(ultrasonic_echo_pin) == 0:
		t_init = time.time()
	
	while GPIO.input(ultrasonic_echo_pin) == 1:
		t_final = time.time()
		distance = 0
	
	if distance == 0:
		time_taken = t_final - t_init
		distance = round(time_taken * half_of_speed_of_sound, 2)
	
	return distance



def compute_led_intensity(inputs):
	if ir_key in inputs:
		inputs[ir_key] = not inputs[ir_key]

	# When the ultrasonic_key sensor doesn't work, we set the default value to be 25000 mm
	# This is set to 25000 mm assuming no object is detected by the sensor
	if ultrasonic_key not in inputs:
		inputs[ultrasonic_key] = 25000

	brightness_level = call_model(inputs)

	return brightness_level



def predict_brightness(inputs):
	output = 10
	
	preprocessed_sensor_data = preprocess_sensor_data_for_brightness(inputs)
	
	brightness_level = brightness_model.predict(preprocessed_sensor_data)
	
	if brightness_level[0] <= 1:
		output = 10
	else:
		output = brightness_level[0] * 20
	
	output = int(round(output))

	if output > 100:
		output = 100
	elif output < 0:
		output = 0
	
	return output


def preprocess_sensor_data_for_brightness(inputs):
	if ir_key not in inputs:
		inputs[ir_key] = 1 
	
	if internal_ldr_key not in inputs:
		inputs[internal_ldr_key] = 50
	
	if ultrasonic_key not in inputs:
		inputs[ultrasonic_key] = 500
	
	external_luminosity = inputs[internal_ldr_key]

	if external_luminosity <= 10:
		external_luminosity_level = 0 # something like pitch black night
	elif external_luminosity <= 20:
		external_luminosity_level = 1 # 4 - 6 AM
	elif external_luminosity <= 40:
		external_luminosity_level = 2 # 6 - 8 AM
	elif external_luminosity <= 60:
		external_luminosity_level = 3 # 8 - 10 AM
	elif external_luminosity <= 80:
		external_luminosity_level = 4 # 10 - 12 A/PM
	else:
		external_luminosity_level = 5 # 12 - 2 PM
	
	distance = inputs[ultrasonic_key] # in millimeters

	if distance <= 200:
		distance_level = 0
	elif distance <= 300:
		distance_level = 1
	elif distance <= 400:
		distance_level = 2
	elif distance <= 500:
		distance_level = 3
	elif distance <= 600:
		distance_level = 4
	else:
		distance_level = 5
	
	sensor_data = [external_luminosity_level, distance_level, inputs[ir_key]]
	sensor_data_arr = np.array(sensor_data)
	sensor_data_arr = sensor_data_arr.reshape(1, -1)
	
	return sensor_data_arr


main()
