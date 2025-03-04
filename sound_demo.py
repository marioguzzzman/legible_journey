import time
from wheel_meter import main_wheel, pedal
from sound_behavior import SoundManager, PedalState
from hardware_controls import VolumeEncoder
import pygame
from config import *

def main():
    # Initialize sound and volume control
    sound_manager = SoundManager()
    volume_control = VolumeEncoder()
    
    print("Starting sound demo...")
    print("\nAudio files loaded:")
    for name, track in sound_manager.tracks.items():
        print(f"- {name}: {track.file_path}")
    
    print(f"\nVolume curves from config:")
    for track, curve in VOLUME_CURVES.items():
        print(f"- {track}: {curve}")
    print("\nPress Ctrl+C to exit")
    
    try:
        while True:
            # Get current state
            current_speed = main_wheel.speed
            pedal_direction = pedal.direction
            
            # Convert to PedalState
            pedal_state = PedalState.FORWARD if pedal_direction == 1 else (
                PedalState.BACKWARD if pedal_direction == -1 else PedalState.STOPPED
            ) 
            if pedal.is_moving:
                pedal_state = PedalState.FORWARD
            
            # Update sound states based on movement
            if main_wheel.is_moving or pedal.is_moving:
                sound_manager.update(current_speed, pedal_state)
            else:
                sound_manager.stop_all()
            
            # Apply master volume from encoder
            sound_manager.set_master_volume(volume_control.volume)
            
            # Debug output
            print(f"\rSpeed: {current_speed:.1f}/{MAX_SPEED} km/h | "
                  f"Pedaling: {pedal.is_moving} | "
                  f"Direction: {pedal_state.name} | "
                  f"Master Vol: {volume_control.volume:.2f}", end="")
            
            # Audio playback monitoring
            if MONITOR_VOLUMES:
                print("\nActive Channels:", end="")
                for name, track in sound_manager.tracks.items():
                    channel = sound_manager.channels[track.channel]
                    if channel.get_busy():
                        print(f"\n- {name}:")
                        print(f"  File: {track.file_path}")
                        print(f"  Channel: {track.channel.name}")
                        print(f"  Volume: {channel.get_volume():.2f}")
                        print(f"  Target Volume: {sound_manager.current_volumes[name]:.2f}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping demo...")
        sound_manager.stop_all()
        pygame.quit()

if __name__ == "__main__":
    main() 