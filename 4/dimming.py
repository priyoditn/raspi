import dht11
import RPi.GPIO as GPIO
import time
import pred
from datetime import date, datetime
from pathlib import Path
import math
    


sleep_time_high = 0.5

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
pwm_frequency = 1000    #   hertz.
dimming_interval = 5
brightening_interval = 2
luminosity_steps = 100
ldr_max = 700
ldr_min = 90

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(ir_pin, GPIO.IN)
GPIO.setup(ultrasonic_echo_pin, GPIO.IN)
GPIO.setup(ultrasonic_trig_pin, GPIO.OUT)
# LDR pin setup occurs inside the ldr() method

# loading model for prediction
pred.load_model("models/lrmodel_v3_trainset_v4.pkl")

log_file_loc = "/home/pi/log/"





def main():
    pwm = GPIO.PWM(led_pin, pwm_frequency)
    pwm.start(0)
    brightness = 100
    logfile = None
    dht11_sensor = dht11.DHT11(pin = dht11_pin)
    prev_temperature = 26.8
    prev_humidity = 78.0
        
    
    try:
        logfile = initialise_log()
        print("Timestamp\tIR Status\tUltrasonic Status\tInternal Incident Radiation\tExternal Incident Radiation\tTemperature\tHumidity\tHeadcount\tBrightness Level")
        
        while True:
            ir_output = GPIO.input(ir_pin)
            ir_status = 'Object detected'

            if ir_output:
                ir_status = 'Surroundings clear'

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
            
            output = compute_led_intensity(sensor_data)
            
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


# install adafruit lib before running it
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


def call_model(inputs):
    brightness_level = 10

    if ir_key not in inputs:
        inputs[ir_key] = 1 # set to no object detection by default when the IR sensor stops working
                           # which means that the light intensity would remain low when human pass through
                           # triggering a suspicion that something has failed
    
    # detected = (inputs[ultrasonic_key] or inputs[ir_key])
    if internal_ldr_key not in inputs:
        inputs[internal_ldr_key] = 50 # assume the brightness level at 50 when the ldr sensor stops working



    current_time = datetime.now().strftime("%H:%M")

    brightness_level = pred.infer(inputs[internal_ldr_key], inputs[ir_key], 
                                  inputs[ultrasonic_key], current_time)
    #   if detected:
    #       brightness_level = 100

    return brightness_level





main()
