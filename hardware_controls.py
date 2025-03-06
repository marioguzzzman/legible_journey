from gpiozero import Button, DigitalOutputDevice
from time import sleep
import threading
from config import *
import json
import os
import atexit
from threading import Thread
from RPi import GPIO

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
            
            # Set initial state - only green LED on to save power
            self.red.off()
            self.green.on()
            self.blue.off()
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

    def debug_output(self):
        while True:
            if DEBUG_MODE and DEBUG_LED:
                print("\n=== RGB LED Debug ===")
                print(f"Red State: {self.red.value}")
                print(f"Green State: {self.green.value}")
                print(f"Blue State: {self.blue.value}")
            sleep(DEBUG_REFRESH_RATE)

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
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(ENCODER_CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(ENCODER_DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(ENCODER_SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self._position = int(self._load_volume() * 100)
            self.clk_last_state = GPIO.input(ENCODER_CLK)
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_rotation, daemon=True)
            self.monitor_thread.start()
            atexit.register(self.cleanup)  # Register cleanup function
            
            if DEBUG_MODE:
                self.debug_thread = threading.Thread(target=self.debug_output, daemon=True)
                self.debug_thread.start()
            
            self._initialized = True
            
        except Exception as e:
            print(f"Error initializing encoder: {e}")
            self.cleanup()
            raise
    
    def _monitor_rotation(self):
        """Monitor encoder rotation in a separate thread"""
        while self.running:
            clk_state = GPIO.input(ENCODER_CLK)
            dt_state = GPIO.input(ENCODER_DT)
            
            # Check rotation
            if clk_state != self.clk_last_state:
                if dt_state != clk_state:
                    self.position = self.position + 1
                else:
                    self.position = self.position - 1
                print(f"Position: {self.position}% | Volume: {self.volume:.2f}")
            
            self.clk_last_state = clk_state
            
            # Check encoder button press with longer debounce
            if GPIO.input(ENCODER_SW):
                self._save_volume()
                sleep(0.3)  # Longer debounce
            
            sleep(0.005)  # Slightly longer delay
    
    @property
    def position(self):
        """Get current position (0-100)"""
        return self._position
    
    @position.setter
    def position(self, value):
        """Set position with bounds checking"""
        self._position = max(0, min(100, value))
    
    @property
    def volume(self):
        """Convert position (0-100) to volume (0.0-1.0)"""
        return self.position / 100.0

    def get_volume(self):
        """Get the current volume as a percentage (0-100)"""
        return self.position  # Return the position directly as percentage

    def cleanup(self):
        """Clean up GPIO resources"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1.0)
        GPIO.cleanup([ENCODER_CLK, ENCODER_DT, ENCODER_SW])
    
    def debug_output(self):
        """Debug output thread"""
        while self.running:
            if DEBUG_MODE and DEBUG_VOLUME:
                print("\n=== Volume Encoder Debug ===")
                print(f"Position: {self.position}%")
                print(f"Volume: {self.volume:.2f}")
                print(f"CLK State: {GPIO.input(ENCODER_CLK)}")
                print(f"DT State: {GPIO.input(ENCODER_DT)}")
                print(f"Switch State: {GPIO.input(ENCODER_SW)}")
            sleep(DEBUG_REFRESH_RATE)
    
    def _save_volume(self):
        """Save volume to both JSON and config file"""
        try:
            # Save to JSON for persistence
            with open('volume_setting.json', 'w') as f:
                json.dump({
                    'master_volume': self.volume,
                    'position': self.position
                }, f)
            
            # Update config.py
            self._update_config_file()
            
            print(f"✓ Volume saved: {self.position}% ({self.volume:.2f})")
                
        except Exception as e:
            print(f"Error saving volume: {e}")
    
    def _load_volume(self):
        """Load volume from JSON file or use default"""
        try:
            with open('volume_setting.json', 'r') as f:
                data = json.load(f)
                if 'position' in data:
                    self._position = data['position']
                    return self.volume
                return data.get('master_volume', DEFAULT_MASTER_VOLUME)
        except:
            return DEFAULT_MASTER_VOLUME
    
    def _update_config_file(self):
        """Update the config.py file with new master volume"""
        try:
            # Get absolute path to config.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'config.py')
            
            print(f"Attempting to update config file at: {config_path}")  # Debug line
            
            if not os.path.exists(config_path):
                print(f"Error: Config file not found at {config_path}")
                return
            
            # Read all lines from config file
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            # Find and update both DEFAULT_MASTER_VOLUME and MASTER_VOLUME
            default_found = False
            current_found = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('DEFAULT_MASTER_VOLUME'):
                    lines[i] = f"DEFAULT_MASTER_VOLUME = {self.volume:.2f}  # Default master volume level\n"
                    default_found = True
                    print(f"Updated DEFAULT_MASTER_VOLUME to {self.volume:.2f}")  # Debug line
                elif line.strip().startswith('MASTER_VOLUME'):
                    lines[i] = f"MASTER_VOLUME = {self.volume:.2f}  # Current master volume level\n"
                    current_found = True
                    print(f"Updated MASTER_VOLUME to {self.volume:.2f}")  # Debug line
            
            # Add values if not found
            if not default_found:
                lines.append(f"\nDEFAULT_MASTER_VOLUME = {self.volume:.2f}  # Default master volume level\n")
                print("Added DEFAULT_MASTER_VOLUME line")  # Debug line
            if not current_found:
                lines.append(f"MASTER_VOLUME = {self.volume:.2f}  # Current master volume level\n")
                print("Added MASTER_VOLUME line")  # Debug line
            
            # Write back to config file
            with open(config_path, 'w') as f:
                f.writelines(lines)
            
            print(f"Successfully updated config file with volume: {self.volume:.2f}")
                
        except Exception as e:
            print(f"Error updating config file: {e}")
            import traceback
            traceback.print_exc()  # Print full error traceback
    
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