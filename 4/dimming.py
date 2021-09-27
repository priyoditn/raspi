import RPi.GPIO as GPIO
import time
from datetime import date, datetime
from pathlib import Path

sleep_time_high = 0.5

led_pin = 12
ir_pin = 16
ultrasonic_trig_pin = 38
ultrasonic_echo_pin = 37

ir_key = 'IR'
ultrasonic_key = 'Ultrasonic'
half_of_speed_of_sound = 343000 / 2 # mm/sec
ultrasonic_trigger_interval = 0.00001 # sec
far_away_threshold = 200 # mm
sensor_stabilise_time = 0.5
pwm_frequency = 50	#	hertz. this is theoretical max
dimming_interval = 5
brightening_interval = 2
luminosity_steps = 100

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(ir_pin, GPIO.IN)
GPIO.setup(ultrasonic_echo_pin, GPIO.IN)
GPIO.setup(ultrasonic_trig_pin, GPIO.OUT)

log_file_loc = "/home/pi/log/"





def main():
	pwm = GPIO.PWM(led_pin, pwm_frequency)
	pwm.start(0)
	brightness = 100
	logfile = None
	
	try:
		logfile = initialise_log()
		print("Timestamp\tIR Status\tUltrasonic Status\tTemperature\tHumidity\tHeadcount\tBrightness Level")
	
		while True:
			ir_output = GPIO.input(ir_pin)
			ir_status = 'Object detected'

			if ir_output:
				ir_status = 'Surroundings clear'

			ultrasonic_data = get_distance()

			sensor_data = {ir_key:ir_output
						, ultrasonic_key: ultrasonic_data}
			
			output = compute_led_intensity(sensor_data)
			
			headcount = 0
			
			if output == 100:
				headcount = 1

			print(f"{datetime.now().strftime('%H:%M:%S')}\t{ir_output}\t{ultrasonic_data}\t21.6\t70.5\t{headcount}\t{output}")
			
			logfile.write(f"{datetime.now().strftime('%H:%M:%S')}\t{ir_output}\t{ultrasonic_data}\t21.6\t70.5\t{headcount}\t{output}\n")
			
			prev_brightness = brightness
			brightness = output

			dim_led(pwm, brightness, prev_brightness)

	except KeyboardInterrupt:
		pass
	finally:
		GPIO.cleanup()
		logfile.close()



def initialise_log():
	today = date.today()
	d = today.strftime("%Y-%m-%d")
	logfileName = log_file_loc + d + ".log"
	f = Path(logfileName)
	fileExists = f.exists()
	
	logfile = open(logfileName, "a")
	
	if not fileExists:
		logfile.write("Timestamp\tIR Status\tUltrasonic Status\tTemperature\tHumidity\tHeadcount\tBrightness Level\n")
		
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
	
	brightness = normalise_brightness(brightness)
	prev_brightness = normalise_brightness(prev_brightness)
	
	transition_interval = brightening_interval
	
	if brightness < prev_brightness:
		transition_interval = dimming_interval
		
	delta = brightness - prev_brightness
	stay_interval = transition_interval * 1.0 / luminosity_steps
	step = int(delta * 1.0 / luminosity_steps)
	
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
		
	

def get_distance():
	#	Initialise distance and pin
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

	# we require boolean for now
	if ultrasonic_key in inputs:
		inputs[ultrasonic_key] = inputs[ultrasonic_key] <= far_away_threshold

	brightness_level = call_model(inputs)

	return brightness_level


# TODO: @arunjeyapal: please add your model wrapper here. Please take a look at log_samples folder for preprocessing of data
def call_model(inputs):
	brightness_level = 10
	
	if ultrasonic_key not in inputs:
		inputs[ultrasonic_key] = False

	if ir_key not in inputs:
			inputs[ir_key] = False

	detected = (inputs[ultrasonic_key] or inputs[ir_key])
	
	if detected:
		brightness_level = 100

	return brightness_level





main()
