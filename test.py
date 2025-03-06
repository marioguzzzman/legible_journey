import pygame
import time

# Initialize Pygame mixer
pygame.mixer.init()

# Load the sound file
try:
    sound = pygame.mixer.Sound("path/to/your/Audios/s1.mp3")  # Update with the correct path
except pygame.error as e:
    print(f"Error loading sound: {e}")
    exit(1)

# Play the sound
sound.play()

# Keep the program running for a few seconds to hear the sound
print("Playing sound 's1' at full volume.")
time.sleep(5)  # Play for 5 seconds

# Stop the sound
sound.stop()
pygame.mixer.quit()  # Clean up the mixer 