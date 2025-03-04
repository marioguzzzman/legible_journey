# Imports
from gpiozero import Button
from signal import pause
from time import time, sleep
from threading import Thread
from math import pi
from colorama import Fore, Back, Style
import numpy as np
from datetime import datetime
from hardware_controls import VolumeEncoder

# Constants
from config import *

class PedalWheel:
    def __init__(self, pin1, pin2, bounce_time=BOUNCE_TIME):
        self.sensor1 = Button(pin1, bounce_time=bounce_time)
        self.sensor2 = Button(pin2, bounce_time=bounce_time)
        self.last_sensor1_time = 0
        self.last_sensor2_time = 0
        self.direction = 0  # 1 for forward, -1 for backward
        self.is_moving = False
        self.speed = 0
        self.start_time = 0
        self.stop_time = 0
        
        self.sensor1.when_pressed = self.sensor1_detected
        self.sensor2.when_pressed = self.sensor2_detected
        
        # Start monitoring thread
        self.monitor_thread = Thread(target=self.check_movement, daemon=True)
        self.monitor_thread.start()
        
        if DEBUG_MODE:
            self.debug_thread = Thread(target=self.debug_output, daemon=True)
            self.debug_thread.start()
    
    def sensor1_detected(self):
        current_time = time()
        if self.last_sensor2_time > self.last_sensor1_time:
            self.direction = 1  # Forward
        self.last_sensor1_time = current_time
        self.is_moving = True
        if not self.start_time:
            self.start_time = current_time
    
    def sensor2_detected(self):
        current_time = time()
        if self.last_sensor1_time > self.last_sensor2_time:
            self.direction = -1  # Backward
        self.last_sensor2_time = current_time
        self.is_moving = True
        if not self.start_time:
            self.start_time = current_time
    
    def check_movement(self):
        while True:
            current_time = time()
            if (current_time - max(self.last_sensor1_time, self.last_sensor2_time) > MOVEMENT_TIMEOUT 
                and self.is_moving):
                self.is_moving = False
                self.stop_time = current_time
                self.speed = 0
            sleep(0.1)

    def debug_output(self):
        """Debug output for pedal wheel"""
        while True:
            if DEBUG_MODE:
                current_time = time()
                print("\n=== Pedal Wheel Debug ===")
                print(f"Moving: {self.is_moving}")
                print(f"Direction: {'Forward' if self.direction == 1 else 'Backward' if self.direction == -1 else 'None'}")
                print(f"Time since Sensor 1: {current_time - self.last_sensor1_time:.2f}s")
                print(f"Time since Sensor 2: {current_time - self.last_sensor2_time:.2f}s")
                if self.is_moving:
                    print(f"Active time: {current_time - self.start_time:.1f}s")
                if self.stop_time:
                    print(f"Last stop: {current_time - self.stop_time:.1f}s ago")
            sleep(DEBUG_REFRESH_RATE)

class MainWheel:
    def __init__(self, pin, wheel_diameter_mm=DEFAULT_DIAMETER):
        self.sensor = Button(pin, bounce_time=BOUNCE_TIME)
        self.wheel_diameter_mm = wheel_diameter_mm
        self.circum_m = wheel_diameter_mm * pi / 1000
        self.count = 0
        self.previous_time = time()
        self.previous_values = np.zeros(AVG_SMOOTHNESS)
        self.speed = 0
        self.avg_speed = 0
        self.is_moving = False
        self.start_time = 0
        self.stop_time = 0
        
        self.sensor.when_pressed = self.detected
        
        # Start monitoring thread
        self.monitor_thread = Thread(target=self.round_meter, daemon=True)
        self.monitor_thread.start()
        
        if DEBUG_MODE:
            self.debug_thread = Thread(target=self.debug_output, daemon=True)
            self.debug_thread.start()
    
    def detected(self):
        self.count += 1
        if not self.is_moving:
            self.is_moving = True
            self.start_time = time()
    
    def round_meter(self):
        while True:
            sleep(PERIOD)
            
            current_time = time()
            elapsed = current_time - self.previous_time
            rounds = self.count / elapsed
            self.speed = self.circum_m * rounds * 3.6
            
            # Check if wheel has stopped
            if self.speed < MIN_SPEED and self.is_moving:
                self.is_moving = False
                self.stop_time = current_time
            
            # Rolling average
            if USE_AVG_SPEED:
                self.previous_values = np.roll(self.previous_values, -1)
                self.previous_values[-1] = self.speed
                self.avg_speed = np.average(self.previous_values)
            
            self.count = 0
            self.previous_time = current_time

    def debug_output(self):
        while True:
            if DEBUG_MODE:
                current_time = time()
                print("\n=== Main Wheel Debug ===")
                print(f"Rotations this period: {self.count}")
                print(f"Speed: {self.speed:.2f} km/h")
                print(f"Avg Speed: {self.avg_speed:.2f} km/h")
                print(f"Moving: {self.is_moving}")
                if self.is_moving:
                    print(f"Active time: {current_time - self.start_time:.1f}s")
            sleep(DEBUG_REFRESH_RATE)

class MilestoneTracker:
    def __init__(self):
        self.active_time = 0
        self.milestone_count = 0
        self.last_milestone_mark = 0
        self.marks_triggered = 0
        self.last_check_time = time()
    
    def update(self, main_wheel_moving, pedal_moving):
        current_time = time()
        
        if main_wheel_moving and pedal_moving:
            self.active_time += current_time - self.last_check_time
            
            milestones = int(self.active_time / MILESTONE_TIME)
            if milestones > self.milestone_count:
                self.milestone_count = milestones
                print(f"\n🏆 MILESTONE MARK {self.marks_triggered + 1} ACHIEVED! 🏆")
                print(f"Total active time: {self.active_time/60:.1f} minutes")
                self.marks_triggered += 1
                self.last_milestone_mark = current_time
        
        self.last_check_time = current_time
    
    def debug_output(self):
        if DEBUG_MODE:
            print("\n=== Milestone Tracker Debug ===")
            print(f"Active time: {self.active_time/60:.1f} minutes")
            print(f"Milestones: {self.milestone_count}")
            print(f"Marks triggered: {self.marks_triggered}")
            if self.marks_triggered > 0:
                print(f"Time since last mark: {(time() - self.last_milestone_mark)/60:.1f} minutes")

# Initialize hardware
main_wheel = MainWheel(PIN)
pedal = PedalWheel(PEDAL_PIN1, PEDAL_PIN2)  # Using both pedal sensors
volume_control = VolumeEncoder()
milestone_tracker = MilestoneTracker()

# For compatibility with existing code
speed = 0
avg_speed = 0

def update_speed():
    global speed, avg_speed
    while True:
        speed = main_wheel.speed
        avg_speed = main_wheel.avg_speed
        milestone_tracker.update(main_wheel.is_moving, pedal.is_moving)
        sleep(0.1)

# Start speed update thread
speed_thread = Thread(target=update_speed, daemon=True)
speed_thread.start()

if __name__ == "__main__":
    print(f"Using main wheel pin {PIN} and pedal pins {PEDAL_PIN1} and {PEDAL_PIN2}")
    print(f"Debug mode: {'ON' if DEBUG_MODE else 'OFF'}")
    print(f"Milestone tracking: Every {MILESTONE_TIME/60:.1f} minutes, mark every {MILESTONE_NOTIFICATION} milestones")
    print("Measuring...")
    
    if DEBUG_MODE:
        try:
            while True:
                # Show all debug information
                main_wheel.debug_output()
                pedal.debug_output()
                milestone_tracker.debug_output()
                volume_control.debug_output()
                sleep(DEBUG_REFRESH_RATE)
        except KeyboardInterrupt:
            print("\nExiting debug mode...")
    else:
        while True:
            print(f"Main Wheel - Speed: {main_wheel.speed:.2f} km/h | Moving: {main_wheel.is_moving}")
            print(f"Pedal - Speed: {pedal.speed:.2f} km/h | Moving: {pedal.is_moving} | Direction: {pedal.direction}")
            if pedal.is_moving and main_wheel.is_moving:
                print(f"Both wheels active for: {time() - max(pedal.start_time, main_wheel.start_time):.1f} seconds")
                print(f"Milestones: {milestone_tracker.milestone_count} (Marks: {milestone_tracker.marks_triggered})")
            sleep(1)
