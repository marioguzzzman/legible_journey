# The Legible project's sound demo

from colorama import Fore, Back, Style

print(Style.DIM, end="")
import pygame
print(Style.RESET_ALL)

import time
from wheel_meter import main_wheel, pedal
from sound_behavior import SoundManager, Zone
from hardware_controls import VolumeEncoder
from config import *

def main():
    sound_manager = SoundManager()
    volume_control = VolumeEncoder()
    
    print("\nStarting sound demo...")
    print("Press Ctrl+C to exit")
    
    start_time = time.time()
    active_time = 0
    current_zone = Zone.INTRO
    
    try:
        while True:
            current_speed = main_wheel.speed
            is_moving = main_wheel.is_moving or pedal.is_moving
            
            if is_moving:
                active_time = time.time() - start_time
                
                # Zone transitions
                if current_zone == Zone.INTRO:
                    if active_time >= 30 or current_speed >= 10:
                        current_zone = Zone.MAIN
                        print(f"Transitioning to MAIN zone (Time: {active_time:.1f}s, Speed: {current_speed:.1f}km/h)")
                elif current_zone == Zone.MAIN and active_time >= 300:
                    current_zone = Zone.MILESTONE
                    print("Transitioning to MILESTONE zone")
                
                # Zone behaviors
                if current_zone == Zone.INTRO:
                    # Only abstract track in intro
                    intro_vol = 0 + (current_speed * 20)  # Base 50% + 5% per km/h
                    sound_manager.play_s1(intro_vol)
                    sound_manager.play_s2(0)
                    sound_manager.play_s3(0)
                
                elif current_zone == Zone.MAIN:
                    # Speed-based mix
                 """    abstract_vol = min(100, current_speed * 10)
                    sound_manager.play_abstract(abstract_vol)
                    
                    deconstr_vol = min(100, max(0, current_speed * 5))
                    sound_manager.play_deconstr(deconstr_vol)
                    
                    narrative_vol = max(0, 100 - (current_speed * 10))
                    sound_manager.play_narrative(narrative_vol) """
                
                elif current_zone == Zone.MILESTONE:
                   """  sound_manager.play_abstract(30)
                    sound_manager.play_deconstr(100)
                    sound_manager.play_narrative(20)
            else: """
                sound_manager.mute_all()
            
            # Apply master volume
            sound_manager.set_master_volume(volume_control.volume)
            
            if MONITOR_VOLUMES:
                print(f"\nZone: {current_zone.name}")
                print(f"Time: {active_time:.1f}s")
                print(f"Speed: {current_speed:.1f} km/h")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping demo...")
        sound_manager.mute_all()
        pygame.quit()

if __name__ == "__main__":
    main() 