import os
import pygame
from config import *

class SoundManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Load sound files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.tracks_path = os.path.join(current_dir, "Audios")
        print(f"Loading audio files from: {self.tracks_path}")
        
        # Create dictionary to store sounds and channels
        self.sounds = {}
        self.channels = {}
        self.volumes = {}
        
        # Load 8 sounds and create their channels
        for i in range(1, 9):
            sound_name = f"s{i}"
            sound_path = os.path.join(self.tracks_path, f"{sound_name}.mp3")
            
            try:
                self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                self.channels[sound_name] = pygame.mixer.Channel(i-1)
                self.volumes[sound_name] = 0.0
                print(f"✓ Loaded {sound_name}")
            except FileNotFoundError:
                print(f"✗ Could not find {sound_path}")
    
    def start_all(self):
        """Start playing all loaded sounds (muted)"""
        for name in self.sounds:
            self.channels[name].play(self.sounds[name], loops=-1)
            self.channels[name].set_volume(0)
    
    def stop_all(self):
        """Stop all sounds"""
        for name in self.channels:
            self.channels[name].stop()
    
    def play(self, sound_name: str, volume: float):
        """Play a sound at specified volume (0-100)"""
        if sound_name in self.channels:
            # Apply LERP for smooth transition
            self.volumes[sound_name] += (
                (volume/100.0) - self.volumes[sound_name]
            ) * LERP_SPEED
            self.channels[sound_name].set_volume(self.volumes[sound_name] * MASTER_VOLUME)
    
    def set_master_volume(self, volume: float):
        """Set master volume (0-100)"""
        global MASTER_VOLUME
        MASTER_VOLUME = volume/100.0 