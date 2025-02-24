# Imports
from gpiozero import Button
from signal import pause
from time import time, sleep
from threading import Thread
from math import pi
from colorama import Fore, Back, Style
import numpy as np

# Constants
from config import *

# Variables
wheel_diameter_mm = 0 # The wheel diameter (millimeters)
circum_m = 0 # The wheel circumference (meters)
previous_values = np.zeros(AVG_SMOOTHNESS) # The previous values measured
count = 0 # The number of sensor triggers (resets after each period)
previous_time = 0 # The previous time (obviously)

# Useful values
speed = 0
avg_speed = 0

def detected():
    global count
    count += 1

def round_meter():
    global count, previous_time, previous_values, speed, avg_speed

    while True:
        sleep(PERIOD)

        elapsed = time() - previous_time
        rounds = count / elapsed
        speed = circum_m * rounds * 3.6
        
        # Rolling average
        if (USE_AVG_SPEED):
            previous_values = np.roll(previous_values, -1)
            previous_values[-1] = speed
            avg_speed = np.average(previous_values)

        if (__name__) == "__main__":
            print(f"Rounds (/s): {rounds:.2f} | Speed (km/h): {speed:.2f} | Smoothened speed (km/h): {avg_speed:.2f}")
        
        count = 0
        previous_time = time()

print(f"Using pin {PIN}", end="")

if __name__ == "__main__":
    wheel_diameter_mm = input("\nWheel diameter (millimeters): ")
    try:
        wheel_diameter_mm = int(wheel_diameter_mm)
    except ValueError:
        print(f"Setting diameter to default value ({DEFAULT_DIAMETER} mm)")
        wheel_diameter_mm = DEFAULT_DIAMETER
else:
    print(f" | Wheel diameter: {DEFAULT_DIAMETER} mm.")
    print(Fore.BLUE + "Note: You can change the pin number or the wheel diameter in config.py." + Style.RESET_ALL)
    wheel_diameter_mm = DEFAULT_DIAMETER


circum_m = wheel_diameter_mm * pi / 1000
previous_time = time()

# Speed measuring thread
thread = Thread(target=round_meter, daemon=True)
thread.start()

# Sensor setup
sensor = Button(PIN, bounce_time=BOUNCE_TIME)
sensor.when_pressed = detected

if __name__ == "__main__":
    print("Measuring...")
    pause()
