import os
import pygame
import numpy as np
from config import *
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional

class Zone(Enum):
    INTRO = 1
    MAIN = 2
    MILESTONE = 3

@dataclass
class ZoneConfig:
    duration: float  # How long this zone lasts (in seconds), None for infinite
    abstract_behavior: str  # Volume behavior description
    deconstr_behavior: str  # Volume behavior description
    narrative_behavior: str  # Volume behavior description
    
    def __str__(self):
        return f"""
Zone Duration: {self.duration if self.duration else 'infinite'} seconds
- Abstract: {self.abstract_behavior}
- Deconstr: {self.deconstr_behavior}
- Narrative: {self.narrative_behavior}
"""

class SoundManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Load the three tracks
        self.tracks_path = "/home/djarak//legible_journey/Audios/"

        self.s1 = pygame.mixer.Sound(os.path.join(self.tracks_path, "s1.mp3"))
        self.s2 = pygame.mixer.Sound(os.path.join(self.tracks_path, "s2.mp3"))
        self.s3 = pygame.mixer.Sound(os.path.join(self.tracks_path, "s3.mp3"))
         
        # Create channels
        self.s1_channel = pygame.mixer.Channel(0)
        self.s2_channel = pygame.mixer.Channel(1)
        self.s3_channel = pygame.mixer.Channel(2)
        
        # Start playing all tracks (muted)
        self.s1_channel.play(self.s1, loops=-1)
        self.s2_channel.play(self.s2, loops=-1)
        self.s3_channel.play(self.s3, loops=-1)
        
        self.current_volumes = {"velo_lent": 0.0, "velo_moyen": 0.0, "velo_rapide": 0.0}
        self.mute_all()
        
        # Zone configurations
        self.zones: Dict[Zone, ZoneConfig] = {
            Zone.INTRO: ZoneConfig(
                duration=30,
                s1="Starts at 0% volume, increases with speed",
                s2="Muted",
                s3="Muted"
            ),
            Zone.MAIN: ZoneConfig(
                # duration=270,  # 4.5 minutes (until milestone)
                # abstract_behavior="Volume follows speed curve",
                # deconstr_behavior="Fades in at medium speeds",
                # narrative_behavior="Loud at start, fades with speed"
            ),
            Zone.MILESTONE: ZoneConfig(
                # duration=None,  # Continues until stop
                # abstract_behavior="Reduced volume",
                # deconstr_behavior="Main focus - full volume",
                # narrative_behavior="Subtle background"
            )
        }
        
        self.current_zone = Zone.INTRO
        self.zone_start_time = 0
        self.total_active_time = 0
    
    def play_s1(self, target_volume: float):
        """Play abstract track at specified volume (0-100) with smooth transition"""
        self.current_volumes["s1"] += (
            (target_volume/100.0) - self.current_volumes["s1"]
        ) * LERP_SPEED
        self.abstract_channel.set_volume(self.current_volumes["abstract"] * MASTER_VOLUME)
    
    def play_s2(self, target_volume: float):
        """Play deconstructed track at specified volume (0-100) with smooth transition"""
        self.current_volumes["s2"] += (
            (target_volume/100.0) - self.current_volumes["s2"]
        ) * LERP_SPEED
        self.deconstr_channel.set_volume(self.current_volumes["deconstr"] * MASTER_VOLUME)
    
    def play_s3(self, target_volume: float):
        """Play narrative track at specified volume (0-100) with smooth transition"""
        self.current_volumes["s3"] += (
            (target_volume/100.0) - self.current_volumes["s3"]
        ) * LERP_SPEED
        self.narrative_channel.set_volume(self.current_volumes["narrative"] * MASTER_VOLUME)
    
    def mute_all(self):
        """Smoothly mute all tracks"""
        for name in self.current_volumes:
            self.current_volumes[name] = 0.0
        self.s1_channel.set_volume(0)
        self.s2_channel.set_volume(0)
        self.s3_channel.set_volume(0)
    
    def set_master_volume(self, volume: float):
        """Set master volume (0-100)"""
        MASTER_VOLUME = volume/100.0
    
    def update(self, speed: float):
        """Update volumes based on speed"""
        # Calculate target volumes using curves from config
        target_volumes = {
            "s1": self._interpolate_volume(speed, VOLUME_CURVES["abstract"]),
            "s2": self._interpolate_volume(speed, VOLUME_CURVES["deconstr"]),
            "s3": self._interpolate_volume(speed, VOLUME_CURVES["narrative"])
        }
        
        # Update volumes with LERP
        self.s1_channel.set_volume(target_volumes["s1"] * MASTER_VOLUME)
        self.s2_channel.set_volume(target_volumes["s2"] * MASTER_VOLUME)
        self.s3_channel.set_volume(target_volumes["s3"] * MASTER_VOLUME)
    
    def _interpolate_volume(self, speed: float, curve: list) -> float:
        """Calculate volume based on speed using the curve"""
        speeds, volumes = zip(*curve)
        return np.interp(speed * 100 / MAX_SPEED, speeds, volumes)
    
    def stop_all(self):
        """Stop all sounds"""
        self.s1_channel.stop()
        self.s2_channel.stop()
        self.s3_channel.stop()
    
    def update_zone(self, is_moving: bool, speed: float, active_time: float):
        """Update zone and volumes based on movement, speed, and time"""
        if not is_moving:
            self.mute_all()
            return
            
        self.total_active_time = active_time
        
        # Zone transitions based on time AND speed
        if self.current_zone == Zone.INTRO:
            if active_time >= 30 or speed >= 10:
                self.current_zone = Zone.MAIN
                print(f"Transitioning to MAIN zone (Time: {active_time:.1f}s, Speed: {speed:.1f}km/h)")
        elif self.current_zone == Zone.MAIN and active_time >= 300:
            self.current_zone = Zone.MILESTONE
            print("Transitioning to MILESTONE zone")
        
        # Apply zone-specific sound behaviors
        if self.current_zone == Zone.INTRO:
            # Only abstract track, volume increases with speed
            abstract_vol = 50 + (speed * 5)  # Start at 50%, add 5% per km/h
            self.play_s1(abstract_vol)
            self.play_s2(0)  # Muted
            self.play_s3(0)  # Muted
            
        elif self.current_zone == Zone.MAIN:
            # All tracks active with speed-based mixing
            abstract_vol = min(100, speed * 10)  # 10% per km/h
            self.play_abstract(abstract_vol)
            
            deconstr_vol = min(100, max(0, speed * 5))  # 5% per km/h
            self.play_deconstr(deconstr_vol)
            
            # Narrative fades out with speed
            narrative_vol = max(0, 100 - (speed * 10))  # Starts 100%, reduces 10% per km/h
            self.play_narrative(narrative_vol)
            
        elif self.current_zone == Zone.MILESTONE:
            # Deconstructed track becomes prominent
            self.play_abstract(30)  # Fixed low volume
            self.play_deconstr(100)  # Full volume
            self.play_narrative(20)  # Subtle background
    
    def print_zone_info(self):
        """Print current zone status and volumes"""
        print(f"\nCurrent Zone: {self.current_zone.name}")
        print(f"Active Time: {self.total_active_time:.1f} seconds")
        print(f"Current Speed: {speed:.1f} km/h")
        print("\nTrack Volumes:")
        print(f"- Abstract: {self.current_volumes['abstract']:.2f}")
        print(f"- Deconstr: {self.current_volumes['deconstr']:.2f}")
        print(f"- Narrative: {self.current_volumes['narrative']:.2f}") 