from gpiozero import Button
from time import sleep
import threading
from config import *
import json
import os

# class RGBLed:  # Currently disabled
#     def __init__(self):
#         self.red = PWMLED(LED_R)
#         self.green = PWMLED(LED_G)
#         self.blue = PWMLED(LED_B)
#         self.current_brightness = 0
#         self._blink_thread = None
#     
#     ... rest of RGBLed class ...

class VolumeEncoder:
    def __init__(self):
        self.clk = Button(ENCODER_CLK)
        self.dt = Button(ENCODER_DT)
        self.sw = Button(ENCODER_SW)
        self.save_button = Button(VOLUME_SAVE_PIN)
        
        self._volume = self._load_volume()
        self.clk_last_state = self.clk.value
        
        self.clk.when_pressed = self._check_rotation
        self.save_button.when_pressed = self._save_volume
    
    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, value):
        self._volume = max(0.0, min(1.0, value))
    
    def _check_rotation(self):
        clk_state = self.clk.value
        dt_state = self.dt.value
        
        if clk_state != self.clk_last_state:
            if dt_state != clk_state:
                self.volume = self.volume + 0.05
            else:
                self.volume = self.volume - 0.05
            print(f"Volume adjusted to: {self.volume:.2f}")
        
        self.clk_last_state = clk_state
    
    def _save_volume(self):
        """Save volume to both JSON and config file"""
        try:
            # Save to JSON for persistence
            with open('volume_setting.json', 'w') as f:
                json.dump({'master_volume': self.volume}, f)
            
            # Update config.py
            self._update_config_file()
            
            print(f"Volume setting saved: {self.volume:.2f}")
                
        except Exception as e:
            print(f"Error saving volume: {e}")
    
    def _load_volume(self):
        """Load volume from JSON file or use default"""
        try:
            with open('volume_setting.json', 'r') as f:
                data = json.load(f)
                return data.get('master_volume', DEFAULT_MASTER_VOLUME)
        except:
            return DEFAULT_MASTER_VOLUME
    
    def _update_config_file(self):
        """Update the config.py file with new master volume"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.py')
        
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            # Find and update/add the MASTER_VOLUME line
            volume_line_found = False
            for i, line in enumerate(lines):
                if line.startswith('MASTER_VOLUME'):
                    lines[i] = f"MASTER_VOLUME = {self.volume:.2f}  # Master volume level (0.0 to 1.0)\n"
                    volume_line_found = True
                    break
            
            # Add MASTER_VOLUME if not found
            if not volume_line_found:
                lines.append(f"\nMASTER_VOLUME = {self.volume:.2f}  # Master volume level (0.0 to 1.0)\n")
            
            with open(config_path, 'w') as f:
                f.writelines(lines)
                
        except Exception as e:
            print(f"Error updating config file: {e}")
    
    def _blink_confirmation(self):
        """Blink green LED briefly to confirm save"""
        if self.led:
            def confirm_blink():
                current_state = self.led.green.value
                self.led.green.value = 1
                sleep(0.2)
                self.led.green.value = current_state
            
            thread = threading.Thread(target=confirm_blink, daemon=True)
            thread.start() 