#sudo apt-get update --fix-missing && sudo apt-get install python3-rpi.gpio
# warning: lowering step_sleep may run into the mechanical limitation of how quick your motor can move

import RPi.GPIO as GPIO
import time
 
motor_in1 = 11
motor_in2 = 12
motor_in3 = 13
motor_in4 = 35

step_sleep = 0.004 #	ms

degrees = 45

#	4096 steps is 360° <=> 5.625*(1/64) per step,
step_count = int(degrees * 4096 / 360)

anticlockwise = True

# For motor 28BYJ-48 and driver ULN2003
step_sequence = [
					[1,0,0,1],
					[1,0,0,0],
					[1,1,0,0],
					[0,1,0,0],
					[0,1,1,0],
					[0,0,1,0],
					[0,0,1,1],
					[0,0,0,1]]
 
# setting up
GPIO.setmode( GPIO.BOARD )
GPIO.setup( motor_in1, GPIO.OUT )
GPIO.setup( motor_in2, GPIO.OUT )
GPIO.setup( motor_in3, GPIO.OUT )
GPIO.setup( motor_in4, GPIO.OUT )

GPIO.output( motor_in1, GPIO.LOW )
GPIO.output( motor_in2, GPIO.LOW )
GPIO.output( motor_in3, GPIO.LOW )
GPIO.output( motor_in4, GPIO.LOW )

motor_pins = [motor_in1, motor_in2, motor_in3, motor_in4]


def motor_cleanup():
	GPIO.output( motor_in1, GPIO.LOW )
	GPIO.output( motor_in2, GPIO.LOW )
	GPIO.output( motor_in3, GPIO.LOW )
	GPIO.output( motor_in4, GPIO.LOW )
	GPIO.cleanup()
 
def run_motor():
	motor_step_counter = 0 ;
	try:
		i = 0
		for i in range(step_count):
			for pin in range(0, len(motor_pins)):
				GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
			if anticlockwise == True:
				motor_step_counter = (motor_step_counter - 1) % 8
			elif anticlockwise ==False:
				motor_step_counter = (motor_step_counter + 1) % 8
			else:
				print( "direction must be True / False only. Other value was provided." )
				motor_cleanup()
			time.sleep( step_sleep )
	 
	except KeyboardInterrupt:
		pass
	finally:
		motor_cleanup()
 
run_motor()
