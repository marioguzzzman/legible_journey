from gpiozero import Button, DigitalOutputDevice
from time import sleep
import threading
from config import *
import json
import os
import atexit
from threading import Thread

class RGBLed:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RGBLed, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            # Using DigitalOutputDevice instead of PWMLED for simple on/off control
            self.red = DigitalOutputDevice(LED_R)
            self.green = DigitalOutputDevice(LED_G)
            self.blue = DigitalOutputDevice(LED_B)
            
            # Set initial state - all LEDs on
            self.red.on()
            self.green.on()
            self.blue.on()
            self._blink_thread = None
            
            # Register cleanup function
            atexit.register(self.cleanup)
            
            self._initialized = True
            
        except Exception as e:
            print(f"Error initializing LED: {e}")
            self.cleanup()
            raise
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if hasattr(self, 'red'):
            self.red.close()
        if hasattr(self, 'green'):
            self.green.close()
        if hasattr(self, 'blue'):
            self.blue.close()
    
    def blink_audio_change(self):
        """Blink blue LED for audio changes"""
        if self._blink_thread and self._blink_thread.is_alive():
            return
        
        def blink():
            # Store current states
            current_r = self.red.value
            current_g = self.green.value
            current_b = self.blue.value
            
            for _ in range(LED_BLINK_COUNT):
                # Turn off red and green, only blue blinks
                self.red.off()
                self.green.off()
                self.blue.on()
                sleep(LED_BLINK_DURATION)
                self.blue.off()
                sleep(LED_BLINK_DURATION)
            
            # Restore original states
            self.red.value = current_r
            self.green.value = current_g
            self.blue.value = current_b
        
        self._blink_thread = threading.Thread(target=blink, daemon=True)
        self._blink_thread.start()

class VolumeEncoder:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VolumeEncoder, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            # Try to initialize the buttons
            self.clk = Button(ENCODER_CLK)
            self.dt = Button(ENCODER_DT)
            self.sw = Button(ENCODER_SW)
            self.save_button = Button(VOLUME_SAVE_PIN)
            
            self._volume = self._load_volume()
            self.clk_last_state = self.clk.value
            
            self.clk.when_pressed = self._check_rotation
            self.save_button.when_pressed = self._save_volume
            
            # Register cleanup function
            atexit.register(self.cleanup)
            
            if DEBUG_MODE:
                self.debug_thread = Thread(target=self.debug_output, daemon=True)
                self.debug_thread.start()
            
            self._initialized = True
            
        except Exception as e:
            print(f"Error initializing encoder: {e}")
            self.cleanup()
            raise
    
    def debug_output(self):
        """Debug output for volume encoder"""
        while True:
            if DEBUG_MODE:
                print("\n=== Volume Encoder Debug ===")
                print(f"Current Volume: {self.volume:.2f}")
                print(f"CLK State: {self.clk.value}")
                print(f"DT State: {self.dt.value}")
                print(f"Switch State: {self.sw.value}")
                print(f"Save Button State: {self.save_button.value}")
            sleep(DEBUG_REFRESH_RATE)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if hasattr(self, 'clk'):
            self.clk.close()
        if hasattr(self, 'dt'):
            self.dt.close()
        if hasattr(self, 'sw'):
            self.sw.close()
        if hasattr(self, 'save_button'):
            self.save_button.close()
    
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