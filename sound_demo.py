import time
from wheel_meter import main_wheel, pedal
from sound_behavior import SoundManager
from hardware_controls import VolumeEncoder
from config import *

def main():
    # Initialize sound and volume control
    sound_manager = SoundManager()
    volume_control = VolumeEncoder()
    
    print("\nStarting sound demo...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            # Update volumes based on speed
            if main_wheel.is_moving or pedal.is_moving:
                sound_manager.update(main_wheel.speed)
            else:
                sound_manager.stop_all()
            
            # Apply master volume from encoder
            sound_manager.set_master_volume(volume_control.volume)
            
            # Monitor output
            if MONITOR_VOLUMES:
                print("\nSpeed:", f"{main_wheel.speed:.1f}/{MAX_SPEED} km/h")
                print("Master Volume:", f"{volume_control.volume:.2f}")
                print("Channel Volumes:")
                for name, volume in sound_manager.current_volumes.items():
                    print(f"- {name}: {volume:.2f}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping demo...")
        sound_manager.stop_all()

if __name__ == "__main__":
    main() 