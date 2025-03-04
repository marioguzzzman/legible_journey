from gpiozero import PWMLED, Button
from time import sleep
import threading
from config import *
import json

class RGBLed:
    def __init__(self):
        self.red = PWMLED(LED_R)
        self.green = PWMLED(LED_G)
        self.blue = PWMLED(LED_B)
        self.current_brightness = 0
        self._blink_thread = None
    
    def set_brightness(self, level, max_level=LED_BRIGHTNESS_STEPS):
        """Set LED brightness based on milestone level"""
        self.current_brightness = min(1.0, level / max_level)
        self.red.value = 0
        self.green.value = self.current_brightness
        self.blue.value = 0
    
    def blink_audio_change(self):
        """Blink blue LED for audio changes"""
        if self._blink_thread and self._blink_thread.is_alive():
            return
        
        def blink():
            current_r = self.red.value
            current_g = self.green.value
            current_b = self.blue.value
            
            for _ in range(LED_BLINK_COUNT):
                self.red.value = 0
                self.green.value = 0
                self.blue.value = 1
                sleep(LED_BLINK_DURATION)
                self.blue.value = 0
                sleep(LED_BLINK_DURATION)
            
            self.red.value = current_r
            self.green.value = current_g
            self.blue.value = current_b
        
        self._blink_thread = threading.Thread(target=blink, daemon=True)
        self._blink_thread.start()

class VolumeEncoder:
    def __init__(self):
        self.clk = Button(ENCODER_CLK)
        self.dt = Button(ENCODER_DT)
        self.sw = Button(ENCODER_SW)
        self.save_button = Button(VOLUME_SAVE_PIN)
        
        self.volume = self._load_volume()
        self.clk_last_state = self.clk.value
        
        self.clk.when_pressed = self._check_rotation
        self.save_button.when_pressed = self._save_volume
    
    def _check_rotation(self):
        clk_state = self.clk.value
        dt_state = self.dt.value
        
        if clk_state != self.clk_last_state:
            if dt_state != clk_state:
                self.volume = min(1.0, self.volume + 0.05)
            else:
                self.volume = max(0.0, self.volume - 0.05)
        
        self.clk_last_state = clk_state
    
    def _save_volume(self):
        try:
            with open('volume_setting.json', 'w') as f:
                json.dump({'master_volume': self.volume}, f)
            print(f"Volume setting saved: {self.volume:.2f}")
        except Exception as e:
            print(f"Error saving volume: {e}")
    
    def _load_volume(self):
        try:
            with open('volume_setting.json', 'r') as f:
                data = json.load(f)
                return data.get('master_volume', 0.5)
        except:
            return 0.5  # Default volume 