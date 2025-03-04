import os
from enum import Enum
import pygame
from dataclasses import dataclass
from typing import List, Dict, Optional
import time
import numpy as np
from config import *  # Import all config parameters

class PedalState(Enum):
    STOPPED = 0
    FORWARD = 1
    BACKWARD = -1

class AudioChannel(Enum):
    ABSTRACT = 0    # Abstract/Ambient sounds (was AMBIENT)
    DECONSTR = 1    # Deconstructed sounds (was MOVEMENT)
    NARRATIVE = 2   # Narrative tracks
    EFFECTS = 3     # Special effects (for milestones, etc)

@dataclass
class AudioTrack:
    name: str
    file_path: str
    channel: AudioChannel
    loop: bool = False
    volume: float = 1.0
    volume_curve: List = None  # Volume curve from config
    fade_ms: int = FADE_MS    # Fade-in time from config

class SoundManager:
    def __init__(self):
        # Use the path from legible.py
        self.base_path = "/home/djarak/LEGIBLE/tracks/"
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Create channels matching legible.py
        pygame.mixer.set_num_channels(len(AudioChannel))
        self.channels = {
            channel: pygame.mixer.Channel(channel.value)
            for channel in AudioChannel
        }
        
        # Audio tracks configuration matching legible.py structure
        self.tracks: Dict[str, AudioTrack] = {
            'abstract': AudioTrack(
                name='abstract',
                file_path=os.path.join(self.base_path, "ligne_abstraction.mp3"),
                channel=AudioChannel.ABSTRACT,
                loop=True,
                volume_curve=VOLUME_CURVES['abstract']
            ),
            
            'deconstr': AudioTrack(
                name='deconstr',
                file_path=os.path.join(self.base_path, "ligne_deconstruite.mp3"),
                channel=AudioChannel.DECONSTR,
                loop=True,
                volume_curve=VOLUME_CURVES['deconstr']
            ),
            
            'narrative': AudioTrack(
                name='narrative',
                file_path=os.path.join(self.base_path, "ligne_narrative.mp3"),
                channel=AudioChannel.NARRATIVE,
                loop=True,
                volume_curve=VOLUME_CURVES['narrative']
            )
        }
        
        # Load all sounds
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._load_sounds()
        
        # Initialize volume tracking
        self.current_volumes = {name: 0.0 for name in self.tracks}
    
    def _load_sounds(self):
        """Load all sound files"""
        print("Loading sounds (it can take several seconds)...")
        for track_name, track in self.tracks.items():
            try:
                if os.path.exists(track.file_path):
                    sound = pygame.mixer.Sound(track.file_path)
                    self.sounds[track_name] = sound
                    track.duration = sound.get_length()
                else:
                    print(f"Warning: Sound file not found: {track.file_path}")
            except Exception as e:
                print(f"Error loading sound {track_name}: {e}")
    
    def interpolate_volume(self, speed: float, curve: List) -> float:
        """Calculate volume based on speed using the same method as legible.py"""
        speeds, volumes = zip(*curve)
        return np.interp(speed * 100 / MAX_SPEED, speeds, volumes)
    
    def update(self, speed: float, pedal_state: PedalState):
        """Update sound playback based on current state"""
        # Calculate target volumes based on speed
        target_volumes = {
            name: self.interpolate_volume(speed, track.volume_curve)
            for name, track in self.tracks.items()
        }
        
        # Update volumes with LERP
        for name, track in self.tracks.items():
            channel = self.channels[track.channel]
            sound = self.sounds.get(name)
            
            if not sound:
                continue
            
            # Start playing if not already playing
            if not channel.get_busy():
                channel.play(sound, loops=-1 if track.loop else 0, fade_ms=track.fade_ms)
            
            # Update volume using LERP
            self.current_volumes[name] += (
                target_volumes[name] - self.current_volumes[name]
            ) * LERP_SPEED
            
            # Apply master volume
            final_volume = self.current_volumes[name] * MASTER_VOLUME
            channel.set_volume(final_volume)
    
    def stop_all(self):
        """Stop all sounds"""
        for channel in self.channels.values():
            channel.stop()
    
    def set_master_volume(self, volume: float):
        """Set master volume for all channels"""
        for channel in self.channels.values():
            current_vol = channel.get_volume()
            if current_vol > 0:  # Only adjust volume for active channels
                channel.set_volume(current_vol * volume) 