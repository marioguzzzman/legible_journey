# The Legible project's sound demo

from colorama import Fore, Back, Style

print(Style.DIM, end="")
import pygame
print(Style.RESET_ALL)

import time
from wheel_meter import main_wheel
from sound_behavior import SoundManager
from hardware_controls import VolumeEncoder
from config import *

def main():
    sound_manager = SoundManager()
    volume_control = VolumeEncoder()
    
    # Start all sounds muted
    sound_manager.start_all()
    
    print("\nStarting sound demo...")
    print("Press Ctrl+C to exit")
    
    start_time = None
    last_active_time = time.time()
    current_frame = 0
    stop_counter = None
    first_frame_elapsed = 0
    
    try:
        while True:
            current_speed = main_wheel.speed
            is_moving = main_wheel.is_moving
            current_time = time.time()

            # Initialize start time when bike starts moving
            if is_moving and start_time is None:
                start_time = current_time
                print("Bike started moving - beginning Time Frame 1")

            if start_time is not None:
                elapsed_time = current_time - start_time

                # Handle stopping logic
                if not is_moving:
                    if current_frame > 0:  # After Time Frame 1
                        if stop_counter is None:  # Start 30s countdown
                            stop_counter = current_time
                        elif current_time - stop_counter >= 30:  # Reset after 30s stopped
                            print("\nBike stopped for 30s - resetting everything")
                            sound_manager.stop_all()
                            start_time = None
                            current_frame = 0
                            stop_counter = None
                            first_frame_elapsed = 0
                            continue
                else:
                    stop_counter = None  # Reset stop counter if moving again

                # Time Frame 1 (0-30s): s1, s2, s3 with increasing volumes
                if first_frame_elapsed <= 30:
                    current_frame = 0
                    if is_moving:
                        first_frame_elapsed += 0.1  # Only count time when moving
                    volume = min(100, current_speed * 10)  # 10% per km/h
                    # Stagger the sounds within the 30s
                    if first_frame_elapsed <= 10:
                        sound_manager.play("s1", volume)
                    elif first_frame_elapsed <= 20:
                        sound_manager.play("s2", volume)
                    else:
                        sound_manager.play("s3", volume)

                # Time Frame 2 (30s-2m30s): s4 with base volume + speed boost
                elif elapsed_time <= 150:
                    if current_frame != 1:
                        current_frame = 1
                        print("\nEntering Time Frame 2")
                        sound_manager.stop_all()
                    
                    base_vol = 60
                    speed_boost = min(20, current_speed * 20)  # 2% per km/h up to 20%
                    volume = min(90, base_vol + speed_boost)
                    sound_manager.play("s4", volume)

                # Time Frame 3 (2m30s-4m30s): s5 with variable volume
                elif elapsed_time <= 270:
                    if current_frame != 2:
                        current_frame = 2
                        print("\nEntering Time Frame 3")
                        sound_manager.stop_all()
                    
                    volume = max(40, min(100, 60 + current_speed * 20))  # Base 60%, vary with speed
                    sound_manager.play("s5", volume)

                else:  # After 4m30s, reset everything
                    print("\nSequence complete - resetting")
                    sound_manager.stop_all()
                    start_time = None
                    current_frame = 0
                    first_frame_elapsed = 0

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        sound_manager.stop_all()
        pygame.quit()

if __name__ == "__main__":
    main()