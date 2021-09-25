import RPi.GPIO as GPIO
import time

ultrasonic_trig_pin = 38
ultrasonic_echo_pin = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ultrasonic_trig_pin, GPIO.OUT)
GPIO.setup(ultrasonic_echo_pin, GPIO.IN)


def get_distance():
	#	Initialise distance and pin
	distance = -1
	GPIO.output(ultrasonic_trig_pin, False)
	time.sleep(2)
	
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



def main():
	try:
		while True:
			ultrasonic_data = get_distance()

			print(f"Distance is {ultrasonic_data} mm")

	except KeyboardInterrupt:
		GPIO.cleanup()



main()