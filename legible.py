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
    zone_2_reached = False
    
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
                
                # Volume controls based on speed:
                # s1: Linear increase with speed
                s1_vol = min(100, current_speed * 10)  # 10% volume per km/h
                if zone_2_reached:
                    s1_vol = max(0, s1_vol - 10)  # Decrease by 10% until reaching 0
                sound_manager.play("s1", s1_vol)
                
                # s2: Peak at medium speed (25 km/h)
                s2_vol = min(100, max(0, 100 - abs(25 - current_speed) * 10))
                if zone_2_reached:
                    s2_vol = max(0, s2_vol - 10)  # Decrease by 10% until reaching 0
                sound_manager.play("s2", s2_vol)
                
                # s3: Also peaks at medium speed but different curve
                s3_vol = min(100, max(0, 100 - abs(25 - current_speed) * 5))
                if zone_2_reached:
                    s3_vol = max(0, s3_vol - 10)  # Decrease by 10% until reaching 0
                sound_manager.play("s3", s3_vol)  # Fixed: was using s2_vol
                
                # s4: Only at high speeds
                if total_active_time >= 60:  # 1 minute
                    if not zone_2_reached:
                        print("Reached Zone 2!")
                        zone_2_reached = True
                    s4_vol = min(100, (current_speed - 30) * 10)  # Increase by 10% continuously
                    sound_manager.play("s4", s4_vol)
                else:
                    sound_manager.play("s4", 0)
            else:
                last_active_time = 0
                sound_manager.stop_all()
                sound_manager.start_all()  # Restart muted
            
            # Store current time for next loop
            last_active_time = current_time
            
            # Set master volume from encoder (0-100)
            sound_manager.set_master_volume(volume_control.volume * 100)  # Fixed: scale to 0-100
            
            if MONITOR_VOLUMES or (DEBUG_MODE and DEBUG_SOUND):
                print(f"\nSpeed: {current_speed:.1f} km/h")
                print(f"Active Time: {total_active_time:.1f}s ({total_active_time/60:.1f}min)")
                print(f"Master Volume: {volume_control.volume*100:.0f}%")
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