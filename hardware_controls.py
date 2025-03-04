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
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(ENCODER_CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(ENCODER_DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(ENCODER_SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Initialize position counter (0-100)
            self._position = int(self._load_volume() * 100)
            self.clk_last_state = GPIO.input(ENCODER_CLK)
            
            # Start monitoring thread
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_rotation, daemon=True)
            self.monitor_thread.start()
            
            # Register cleanup
            atexit.register(self.cleanup)
            
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
            
            # Check encoder button press (instead of separate save button)
            if GPIO.input(ENCODER_SW):
                self._save_volume()
                sleep(0.2)  # Debounce
            
            sleep(0.001)  # Small delay to prevent CPU overload
    
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