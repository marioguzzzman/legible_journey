import pygame
import time
import os

# Initialize Pygame mixer
pygame.mixer.init()

# Set the path to the sound file
current_dir = os.path.dirname(os.path.abspath(__file__))
sound_path = os.path.join(current_dir, "Audios", "s1.mp3")  # Update with the correct path to your sound file

# Load the sound file
try:
    sound = pygame.mixer.Sound(sound_path)
except pygame.error as e:
    print(f"Error loading sound: {e}")
    exit(1)

# Play the sound at full volume
sound.set_volume(1.0)  # Set volume to 100%
sound.play()

# Keep the program running for a few seconds to hear the sound
print("Playing sound 's1' at full volume. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    print("\nStopping sound playback.")
    sound.stop()
finally:
    pygame.mixer.quit()  # Clean up the mixer 