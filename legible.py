# The Legible project's sound demo

from colorama import Fore, Back, Style

print(Style.DIM, end="")
import pygame
print(Style.RESET_ALL)

import time
from wheel_meter import main_wheel, pedal
from sound_behavior import SoundManager
from hardware_controls import VolumeEncoder
from config import *
import atexit
from RPi import GPIO

def main():
    sound_manager = SoundManager()
    volume_control = VolumeEncoder()
    
    # Start all sounds muted
    sound_manager.start_all()
    
    print("\nStarting sound demo...")
    print("Press Ctrl+C to exit")
    
    start_time = None
    last_active_time = time.time()
    
    first_frame_elapsed = 0
    
    short_trip = 2
    long_trip = 1
    what_trip = long_trip

    current_frame = 0
    stop_counter = None

    # Speed thresholds for long trip (km/h)
    SLOW_MAX = 3
    MEDIUM_MAX = 7
    # Anything above MEDIUM_MAX is considered fast

    # Volume targets for each sound
    target_volumes = {
        "bliss": 0.0,
        "story": 0.0, 
        "deconstruction": 0.0
    }

    # Current volumes for each sound
    current_volumes = {
        "bliss": 0.0,
        "story": 0.0,
        "deconstruction": 0.0
    }

    # Fade rate (volume change per iteration)
    FADE_RATE = 0.05

    # Initialize master volume
    master_volume = DEFAULT_MASTER_VOLUME

    try:
        while True:
            current_speed = main_wheel.speed
            is_moving = main_wheel.is_moving
            current_time = time.time()

            # Update master volume from encoder
            master_volume = volume_control.get_volume()

            if DEBUG_MODE:
                print("\n=== Time Frame Status ===")
                if start_time is not None:
                    elapsed = current_time - start_time
                    print(f"Total Time: {elapsed:.1f}s")
                    print(f"Frame 1 Time: {first_frame_elapsed:.1f}s")
                    print(f"Current Frame: {current_frame + 1}")
                    if stop_counter:
                        print(f"Stop Time: {current_time - stop_counter:.1f}s")
                print(f"Moving: {is_moving}")
                print(f"Speed: {current_speed:.1f} km/h")
                print(f"Master Volume: {master_volume:.2f}")

            if what_trip == short_trip:
                # [Original short_trip code remains exactly the same]
                # Initialize start time when bike starts moving
                if is_moving and start_time is None:
                    start_time = current_time
                    print("\n Bike started moving - beginning Time Frame 1")

                if start_time is not None:
                    elapsed_time = current_time - start_time

                    # Handle stopping logic
                    if not is_moving:
                        if current_frame > 0:  # After Time Frame 1
                            if stop_counter is None:  # Start 30s countdown
                                stop_counter = current_time
                                print("\n Bike stopped - 30s countdown started")
                            elif current_time - stop_counter >= 30:  # Reset after 30s stopped
                                print("\n Bike stopped for 30s - resetting everything")
                                sound_manager.stop_all()
                                start_time = None
                                current_frame = 0
                                stop_counter = None
                                first_frame_elapsed = 0
                                continue
                        sound_manager.stop_all()
                    else:
                        stop_counter = None  # Reset stop counter if moving again

                    # Time Frame 1 (0-30s): s1, s2, s3 with increasing volumes
                    if first_frame_elapsed <= 30:
                        if current_frame != 0:
                            current_frame = 0
                            print("\n Time Frame 1: Introducing sounds gradually")
                        if is_moving:
                            first_frame_elapsed += 0.1  # Only count time when moving
                        volume = min(100, current_speed * 10) * master_volume  # Apply master volume
                        
                        # Stagger the sounds within the 30s
                        if first_frame_elapsed <= 10:
                            sound_manager.play("s1", volume)
                            if DEBUG_MODE:
                                print(f"Playing s1 at {volume:.0f}%")
                        elif first_frame_elapsed <= 20:
                            sound_manager.play("s1", volume)
                            sound_manager.play("s2", volume)
                            if DEBUG_MODE:
                                print(f"Playing s1, s2 at {volume:.0f}%")
                        else:
                            sound_manager.play("s1", volume)
                            sound_manager.play("s2", volume)
                            sound_manager.play("s3", volume)
                            if DEBUG_MODE:
                                print(f"Playing s1, s2, s3 at {volume:.0f}%")

                    # Time Frame 2 (30s-2m30s): s4 with base volume + speed boost
                    elif elapsed_time <= 150:
                        if current_frame != 1:
                            current_frame = 1
                            print("\n Time Frame 2: Speed-boosted s4")
                            sound_manager.stop_all()
                            sound_manager.start_all()
                        
                        if not is_moving:
                            if stop_counter is None:  # Just stopped
                                stop_counter = current_time
                                print("\n Wheel stopped - muting sound (60s timeout)")
                                sound_manager.play("s4", 0)  # Mute but don't stop
                            elif current_time - stop_counter >= 60:  # 60s timeout
                                print("\n Wheel stopped for 60s - resetting sequence")
                                sound_manager.stop_all()
                                start_time = None
                                current_frame = 0
                                stop_counter = None
                                first_frame_elapsed = 0
                                continue
                        else:  # Wheel is moving
                            stop_counter = None  # Reset stop counter
                            base_vol = 60
                            speed_boost = min(40, current_speed * 2)
                            volume = min(100, base_vol + speed_boost) * master_volume  # Apply master volume
                            sound_manager.play("s4", volume)
                            if DEBUG_MODE:
                                print(f"Playing s4 at {volume:.0f}% (base: {base_vol}%, boost: {speed_boost:.0f}%)")

                    # Time Frame 3 (2m30s-4m30s): s5 with variable volume
                    elif elapsed_time <= 270:
                        if current_frame != 2:
                            current_frame = 2
                            print("\n Time Frame 3: Variable s5")
                            sound_manager.stop_all()
                            sound_manager.start_all()
                        
                        volume = max(40, min(100, 60 + current_speed * 2)) * master_volume  # Apply master volume
                        sound_manager.play("s5", volume)
                        if DEBUG_MODE:
                            print(f"Playing s5 at {volume:.0f}%")

                    else:  # After 4m30s, reset everything
                        print("\n Sequence complete - resetting")
                        sound_manager.stop_all()
                        start_time = None
                        current_frame = 0
                        first_frame_elapsed = 0

            elif what_trip == long_trip:
                # Start all sounds if not already started
                if is_moving and start_time is None:
                    start_time = current_time
                    sound_manager.play("s5", 0)  # bliss
                    sound_manager.play("s6", 0)  # story
                    sound_manager.play("s7", 0)  # deconstruction
                    print("\n Long trip started - all sounds initialized")

                if start_time is not None:
                    # Handle stopping logic
                    if not is_moving:
                        if stop_counter is None:
                            stop_counter = current_time
                            print("\n Wheel stopped - starting 60s countdown")
                        elif current_time - stop_counter >= 60:
                            print("\n Wheel stopped for 60s - resetting everything")
                            sound_manager.stop_all()
                            start_time = None
                            stop_counter = None
                            # Reset all volumes
                            for key in current_volumes:
                                current_volumes[key] = 0.0
                                target_volumes[key] = 0.0
                            continue
                        # Set all target volumes to 0 when stopped
                        for key in target_volumes:
                            target_volumes[key] = 0.0
                    else:
                        stop_counter = None
                        # Set target volumes based on speed range
                        if current_speed <= SLOW_MAX:
                            target_volumes["bliss"] = 1.0
                            target_volumes["story"] = 0.0
                            target_volumes["deconstruction"] = 0.0
                        elif current_speed <= MEDIUM_MAX:
                            target_volumes["bliss"] = 0.0
                            target_volumes["story"] = 1.0
                            target_volumes["deconstruction"] = 0.0
                        else:
                            target_volumes["bliss"] = 0.0
                            target_volumes["story"] = 0.0
                            target_volumes["deconstruction"] = 1.0

                    # Gradually adjust volumes
                    for sound, target in target_volumes.items():
                        if current_volumes[sound] < target:
                            current_volumes[sound] = min(target, current_volumes[sound] + FADE_RATE)
                        elif current_volumes[sound] > target:
                            current_volumes[sound] = max(target, current_volumes[sound] - FADE_RATE)
                        
                        # Apply volumes with master volume
                        if sound == "bliss":
                            sound_manager.play("s5", current_volumes[sound] * 100 * master_volume)
                        elif sound == "story":
                            sound_manager.play("s6", current_volumes[sound] * 100 * master_volume)
                        elif sound == "deconstruction":
                            sound_manager.play("s7", current_volumes[sound] * 100 * master_volume)

                    if DEBUG_MODE:
                        print("\nCurrent Volumes:")
                        print(f"Bliss: {current_volumes['bliss']:.2f}")
                        print(f"Story: {current_volumes['story']:.2f}")
                        print(f"Deconstruction: {current_volumes['deconstruction']:.2f}")

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        sound_manager.stop_all()
        pygame.quit()
    finally:
        GPIO.cleanup()  # Ensure GPIO pins are released

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted. Cleaning up...")
    finally:
        GPIO.cleanup()  # Ensure GPIO pins are released