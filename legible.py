# The Legible project's main program

from colorama import Fore, Back, Style

print(Style.DIM, end="")
import pygame
print(Style.RESET_ALL)

import wheel_meter
from config import *
import time
import numpy as np
from hardware_controls import VolumeEncoder

pygame.mixer.init()

folder_path = "/home/djarak/LEGIBLE/tracks/"
ext = ".mp3"

# Channel initialization
channels = {
    "abstract": pygame.mixer.Channel(0),
    "deconstr": pygame.mixer.Channel(1),
    "narrative": pygame.mixer.Channel(2)
}

print("Loading sounds (it can take several seconds)...")

# Sound initialization
sounds = {
    "abstract": pygame.mixer.Sound(folder_path + "ligne_abstraction" + ext),
    "deconstr": pygame.mixer.Sound(folder_path + "ligne_deconstruite" + ext),
    "narrative": pygame.mixer.Sound(folder_path + "ligne_narrative" + ext)
}

print(Fore.GREEN + "Now playing. Time to get on the bike!" + Style.RESET_ALL)

# Volume initialization
current_volumes = {channel: 0.0 for channel in channels}

# Starts all the channels
for name, channel in channels.items():
    channel.play(sounds[name], loops=-1, fade_ms=FADE_MS)

def interpolate_volume(speed, curve):
    speeds, volumes = zip(*curve)
    return np.interp(speed * 100 / MAX_SPEED, speeds, volumes)

def get_all_volumes(speed):
    return [f"{interpolate_volume(wheel_meter.speed, VOLUME_CURVES[c]):.2f}" for c in channels]

def pygame_loop():
    running = True
    volume_control = VolumeEncoder()
    last_volumes = {channel: 0.0 for channel in channels}
    
    while running:
        target_volumes = {channel: interpolate_volume(wheel_meter.speed, VOLUME_CURVES[channel]) for channel in channels}

        for name, channel in channels.items():
            current_volumes[name] += (target_volumes[name] - current_volumes[name]) * LERP_SPEED
            # Apply master volume from encoder
            final_volume = current_volumes[name] * volume_control.volume
            channel.set_volume(final_volume)
            
            # Store last volume without LED feedback
            last_volumes[name] = final_volume

        if (MONITOR_VOLUMES):
            print(f"Speed: {wheel_meter.speed} | Master Volume: {volume_control.volume:.2f}")
            print(f"Volumes: {get_all_volumes(wheel_meter.speed)}")

        time.sleep(0.1)

pygame_loop()
