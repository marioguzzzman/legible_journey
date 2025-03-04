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
        # Verify sound loaded correctly
        if name in sound_manager.sounds:
            print(f"  ✓ Sound loaded successfully")
        else:
            print(f"  ✗ Failed to load sound")
    
    print(f"\nVolume curves from config:")
    for track, curve in VOLUME_CURVES.items():
        print(f"- {track}: {curve}")
    print("\nPress Ctrl+C to exit")
    
    # Start playing all tracks immediately with zero volume
    for name, track in sound_manager.tracks.items():
        if name in sound_manager.sounds:
            channel = sound_manager.channels[track.channel]
            sound = sound_manager.sounds[name]
            channel.play(sound, loops=-1, fade_ms=FADE_MS)
            channel.set_volume(0.0)
            print(f"Started playing {name} on channel {track.channel.name}")
    
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
                print(f"\nMoving - Speed: {current_speed:.1f} km/h")
            else:
                sound_manager.stop_all()
                print("\nStopped")
            
            # Apply master volume from encoder
            sound_manager.set_master_volume(volume_control.volume)
            
            # Audio playback monitoring
            if MONITOR_VOLUMES:
                print("\nActive Channels:")
                for name, track in sound_manager.tracks.items():
                    channel = sound_manager.channels[track.channel]
                    if channel.get_busy():
                        print(f"- {name}:")
                        print(f"  Channel: {track.channel.name}")
                        print(f"  Playing: {'Yes' if channel.get_busy() else 'No'}")
                        print(f"  Volume: {channel.get_volume():.2f}")
                        print(f"  Target Volume: {sound_manager.current_volumes[name]:.2f}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping demo...")
        sound_manager.stop_all()
        pygame.quit()

if __name__ == "__main__":
    main() 