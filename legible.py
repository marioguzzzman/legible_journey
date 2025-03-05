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

def main():
    sound_manager = SoundManager()
    volume_control = VolumeEncoder()
    
    # Start all sounds muted
    sound_manager.start_all()
    
    print("\nStarting sound demo...")
    print("Press Ctrl+C to exit")
    
    start_time = time.time()
    total_active_time = 0
    last_active_time = 0
    
    try:
        while True:
            current_speed = main_wheel.speed
            is_moving = main_wheel.is_moving or pedal.is_moving
            current_time = time.time()
            
            # Update active time only when moving
            if is_moving:
                if last_active_time == 0:  # Just started moving
                    last_active_time = current_time
                total_active_time += current_time - last_active_time
                
                # Example volume controls based on speed:
                
                # s1 increases with speed
                s1_vol = min(100, current_speed * 10)  # 10% volume per km/h
                sound_manager.play("s1", s1_vol)
                
                # s2 peaks at medium speed
                s2_vol = min(100, max(0, 100 - abs(25 - current_speed) * 4))
                sound_manager.play("s2", s2_vol)
                
                # s3 fades out as speed increases
                s3_vol = min(100, max(0, 100 - abs(25 - current_speed) * 5))
                sound_manager.play("s3", s2_vol)
                
                # s4 only plays at high speeds
                if current_speed > 30:
                    s4_vol = min(100, (current_speed - 30) * 5)
                    sound_manager.play("s4", s4_vol)
                else:
                    sound_manager.play("s4", 0)
            else:
                last_active_time = 0  # Reset last active time when stopped
                sound_manager.stop_all()
                sound_manager.start_all()  # Restart muted
            
            # Store current time for next loop
            last_active_time = current_time
            
            # Apply master volume
            sound_manager.set_master_volume(volume_control.volume)
            
            if MONITOR_VOLUMES or (DEBUG_MODE and DEBUG_SOUND):
                print(f"\nSpeed: {current_speed:.1f} km/h")
                print(f"Active Time: {total_active_time:.1f}s ({total_active_time/60:.1f}min)")
                if DEBUG_MODE and DEBUG_SOUND:
                    sound_manager.print_sound_status()
                else:
                    print("Volumes:")
                    for name, vol in sound_manager.volumes.items():
                        print(f"- {name}: {vol*100:.0f}%")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        print(f"Total Active Time: {total_active_time:.1f}s ({total_active_time/60:.1f}min)")
        sound_manager.stop_all()
        pygame.quit()

if __name__ == "__main__":
    main() 