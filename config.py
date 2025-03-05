### WHEEL_METER.PY

# Wheel Sensors
PIN = 17          # GPIO27 (pin 11) - Main wheel sensor
PEDAL_PIN1 = 27   # GPIO27 (pin 13) - First pedal sensor
PEDAL_PIN2 = 22   # GPIO22 (pin 15) - Second pedal sensor

# Volume Encoder Pins
ENCODER_CLK = 23  # GPIO23 (pin 16) - Encoder clock
ENCODER_DT = 24   # GPIO24 (pin 18) - Encoder data
ENCODER_SW = 25   # GPIO25 (pin 22) - Encoder switch
VOLUME_SAVE_PIN = 16  # GPIO16 (pin 36) - Save button

# RGB LED Pins (Common cathode LED)
LED_R = 5         # GPIO5  (pin 29) - Red channel
LED_G = 6         # GPIO6  (pin 31) - Green channel
LED_B = 13        # GPIO13 (pin 33) - Blue channel
LED_BLINK_DURATION = 0.2  # Seconds for each blink
LED_BLINK_COUNT = 3  # Number of blinks for audio changes

PEDAL_SENSOR_DISTANCE = 0.05 # Distance between pedal sensors in meters
MOVEMENT_TIMEOUT = 2 # Time in seconds after which wheel is considered stopped
MIN_SPEED = 0.5 # Minimum speed in km/h to consider wheel moving

BOUNCE_TIME = 0.005 # The time span during which the sensor ingores inputs after a trigger (necessary)
DEFAULT_DIAMETER = 622 # The default diameter of the wheel (in millimeters)
PERIOD = 2 # The duration between each measuring (in seconds)
USE_AVG_SPEED = False # Whether to use the average speed instead of the direct speed
AVG_SMOOTHNESS = 5 # The amount of stored previous speed (used to compute a rolling average)

# Milestone settings
MILESTONE_TIME = 1 * 60  # Time in seconds (5 minutes) to count as one milestone
MILESTONE_NOTIFICATION = 3  # Number of milestones needed to trigger a mark
MILESTONE_DEBUG = True  # Show milestone progress in debug mode

# Debug settings
DEBUG_MODE = True  # Master debug switch
DEBUG_REFRESH_RATE = 0.5  # How often to update debug information (seconds)

# Component debug flags (only work when DEBUG_MODE is True)
DEBUG_MAIN_WHEEL = True
DEBUG_PEDAL_WHEEL = False
DEBUG_VOLUME = True
DEBUG_LED = False
DEBUG_SOUND = True  # Add this line to monitor sound status

### LEGIBLE.PY

# VOLUME_CURVES contains the volume configuration for each track. For each pair of values, the first one represents the speed (percentage), while the second one represents the volume (from 0 to 1).
# For example, if the maximum speed is set to 50 km/h, and we have (30, 0.5), it means that when 30 % of 50 km/h (= 15 km/h) is reached, the volume of the associated track will reach 50 %.
# Feel free to add, remove and modify the values and value pairs for each track, but you MUST keep them in ascending order (according to the speed percentage).
# You also need to specify at least the 0 % and 100 % pairs.

VOLUME_CURVES = {
    "abstract": [(0, 0.0), (1, 1.0)], # The track is fully muted at 0 km/h and out loud at maximum speed. (Remove this comment if changed)
    "deconstr": [(0, 0.0), (30, 0.3), (50, 1.0), (100, 0.7)], # The track begins to be heard at 30 % of the maximum speed, is out loud at 50 % and gets quieter at maximum speed. (Remove this comment if changed)
    "narrative": [(0, 1.0), (70, 0.0), (100, 0.0)] # This track is out loud at 0 km/h then gets muted at 70 % of the maximum speed. (Remove this comment if changed)
}

FADE_MS = 1000 # The fade-in effect (in milliseconds) when a track (re)starts
MAX_SPEED = 50 # The maximum speed (in km/h) used to make interpolations between tracks
LERP_SPEED = 0.05  # Speed of volume changes (0.0-1.0)
MONITOR_VOLUMES = False # Not recommended, because it takes ressources that are needed for continuous audio. Only use for testing purposes.

# Volume settings
DEFAULT_MASTER_VOLUME = 0.5  # Default master volume level (0.0-1.0)
MASTER_VOLUME = 0.5  # Current master volume level (0.0-1.0)
