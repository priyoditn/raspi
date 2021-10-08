#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
 
in1 = 11
in2 = 12
in3 = 13
in4 = 15
#sudo apt-get update --fix-missing && sudo apt-get install python3-rpi.gpio
# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.004 #	ms

degrees = 90

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
GPIO.setup( in1, GPIO.OUT )
GPIO.setup( in2, GPIO.OUT )
GPIO.setup( in3, GPIO.OUT )
GPIO.setup( in4, GPIO.OUT )
 

GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )
 
 
motor_pins = [in1,in2,in3,in4]
motor_step_counter = 0 ;
 
 
def cleanup():
	GPIO.output( in1, GPIO.LOW )
	GPIO.output( in2, GPIO.LOW )
	GPIO.output( in3, GPIO.LOW )
	GPIO.output( in4, GPIO.LOW )
	GPIO.cleanup()
 

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
			print( "direction must be True / False" )
			cleanup()
			exit( 1 )
		time.sleep( step_sleep )
 
except KeyboardInterrupt:
	cleanup()
	exit( 1 )
 
cleanup()
exit( 0 )
