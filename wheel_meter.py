# Imports
from gpiozero import Button
from signal import pause
from time import time, sleep
from threading import Thread
from math import pi
import numpy as np

# Constants
PIN = 17 # The GPIO pin used for the sensor's digital output
BOUNCE_TIME = 0.01 # The time span during which the sensor ingores inputs after a trigger (necessary)
DEFAULT_DIAMETER = 622 # The default diameter of the wheel (in millimeters)
AVG_SMOOTHNESS = 5 # The amount of stored previous speed (used to compute a rolling average)
PERIOD = 2 # The duration between each measuring (in seconds)

print(f"Using pin {PIN}.") 
wheel_diameter_mm = input("Wheel diameter (millimeters): ")

try:
    wheel_diameter_mm = int(wheel_diameter_mm)
except ValueError:
    print("Setting diameter to default value (622 mm).")
    wheel_diameter_mm = DEFAULT_DIAMETER

circum_m = wheel_diameter_mm * pi / 1000
previous_values = np.zeros(AVG_SMOOTHNESS)
count = 0
previous_time = time()

def detected():
    global count
    count += 1

def round_meter():
    global count, previous_time, previous_values

    while True:
        sleep(PERIOD)

        elapsed = time() - previous_time
        rounds = count / elapsed
        speed = circum_m * rounds * 3.6
        
        # Rolling average
        previous_values = np.roll(previous_values, -1)
        previous_values[-1] = speed
        avg = np.average(previous_values)

        print(f"Rounds (/s): {rounds:.2f} | Speed (km/h): {speed:.2f} | Smoothened speed (km/h): {avg:.2f}")
        
        count = 0
        previous_time = time()

# Speed measuring thread
thread = Thread(target=round_meter, daemon=True)
thread.start()

# Sensor setup
sensor = Button(PIN, bounce_time=BOUNCE_TIME)
sensor.when_pressed = detected

print("Measuring...")
pause()
