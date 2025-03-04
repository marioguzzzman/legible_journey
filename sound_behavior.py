import os
import pygame
import numpy as np
from config import *

class SoundManager:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Channel initialization (matching legible.py)
        self.channels = {
            "abstract": pygame.mixer.Channel(0),
            "deconstr": pygame.mixer.Channel(1),
            "narrative": pygame.mixer.Channel(2)
        }
        
        # Load sounds
        print("Loading sounds (it can take several seconds)...")
        self.sounds = {
            "abstract": pygame.mixer.Sound(os.path.join("/home/djarak/LEGIBLE/tracks/", "ligne_abstraction.mp3")),
            "deconstr": pygame.mixer.Sound(os.path.join("/home/djarak/LEGIBLE/tracks/", "ligne_deconstruite.mp3")),
            "narrative": pygame.mixer.Sound(os.path.join("/home/djarak/LEGIBLE/tracks/", "ligne_narrative.mp3"))
        }
        
        # Initialize volume tracking
        self.current_volumes = {name: 0.0 for name in self.channels}
        
        # Start all tracks
        for name, channel in self.channels.items():
            channel.play(self.sounds[name], loops=-1, fade_ms=FADE_MS)
    
    def update(self, speed: float):
        """Update volumes based on speed"""
        # Calculate target volumes using curves from config
        target_volumes = {
            name: self._interpolate_volume(speed, VOLUME_CURVES[name])
            for name in self.channels
        }
        
        # Update volumes with LERP
        for name, channel in self.channels.items():
            self.current_volumes[name] += (
                target_volumes[name] - self.current_volumes[name]
            ) * LERP_SPEED
            
            # Apply master volume
            channel.set_volume(self.current_volumes[name] * MASTER_VOLUME)
    
    def _interpolate_volume(self, speed: float, curve: list) -> float:
        """Calculate volume based on speed using the curve"""
        speeds, volumes = zip(*curve)
        return np.interp(speed * 100 / MAX_SPEED, speeds, volumes)
    
    def set_master_volume(self, volume: float):
        """Set master volume for all channels"""
        for name, channel in self.channels.items():
            channel.set_volume(self.current_volumes[name] * volume)
    
    def stop_all(self):
        """Stop all sounds"""
        for channel in self.channels.values():
            channel.stop() 