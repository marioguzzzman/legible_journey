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
    
    start_time = time.time()
    last_active_time = 0
    sound_index = 0
    
    try:
        while True:
            current_speed = main_wheel.speed
            is_moving = main_wheel.is_moving
            current_time = time.time()
            
            # Update sound every 30 seconds
            if current_time - start_time >= 30:
                start_time = current_time
                sound_index = (sound_index + 1) % 8  # Cycle through 8 sounds
                sound_name = f"s{sound_index + 1}"
                
                # Volume control based on speed
                s_vol = min(100, current_speed * 10)  # 10% volume per km/h
                sound_manager.play(sound_name, s_vol)
                
                print(f"\nSwitching to sound: {sound_name}")
                print(f"Speed: {current_speed:.1f} km/h")
                print(f"Volume: {s_vol:.0f}%")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        sound_manager.stop_all()
        pygame.quit()

if __name__ == "__main__":
    main() 