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
    
    # Start all sounds muted
    sound_manager.start_all()
    
    print("\nStarting sound demo...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            current_speed = main_wheel.speed
            is_moving = main_wheel.is_moving or pedal.is_moving
            
            if is_moving:
                # Example volume controls based on speed:
                
                # s1 increases with speed
                s1_vol = min(100, current_speed * 10)  # 10% volume per km/h
                sound_manager.play("s1", s1_vol)
                
                # s2 peaks at medium speed
                s2_vol = min(100, max(0, 100 - abs(25 - current_speed) * 4))
                sound_manager.play("s2", s2_vol)
                
                # s3 fades out as speed increases
                s3_vol = max(0, 100 - current_speed * 5)  # Starts at 100%, drops 5% per km/h
                sound_manager.play("s3", s3_vol)
                
                # s4 only plays at high speeds
                if current_speed > 30:
                    s4_vol = min(100, (current_speed - 30) * 5)
                    sound_manager.play("s4", s4_vol)
                else:
                    sound_manager.play("s4", 0)
            else:
                # Stop all sounds when not moving
                sound_manager.stop_all()
                sound_manager.start_all()  # Restart muted
            
            # Apply master volume
            sound_manager.set_master_volume(volume_control.volume)
            
            if MONITOR_VOLUMES:
                print(f"\nSpeed: {current_speed:.1f} km/h")
                print("Volumes:")
                for name, vol in sound_manager.volumes.items():
                    print(f"- {name}: {vol*100:.0f}%")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        sound_manager.stop_all()
        pygame.quit()

if __name__ == "__main__":
    main() 