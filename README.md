# legible_journey
Legible_journey art project

## legible.py

The project's main program. According to the speed of a bike's wheel, the program will adjust independently the volumes of 3 custom audio tracks. Its behaviour can be configured inside `config.py`. The program now includes master volume control via a rotary encoder and visual feedback through an RGB LED.

## wheel_meter.py

This program reads sensor signals to measure:
1. The rotation speed of the main wheel using a Hall sensor
2. The movement of the pedal using another Hall sensor
3. Tracks milestones based on active riding time

It is a dependency of `legible.py`.

### How it works

1. The main wheel sensor measures rotation speed for audio track mixing
2. The pedal sensor detects when the bike is being actively pedaled
3. When both wheels are moving, the system:
   - Tracks active riding time
   - Counts milestones (every 1 minute by default)
   - Triggers milestone marks every 3 milestones
4. Visual feedback is provided through an RGB LED:
   - Green brightness increases with milestones
   - Blue blinks when audio track volumes change significantly

## hardware_controls.py

Manages additional hardware components:

### RGB LED
- Shows milestone progress through green brightness levels
- Blinks blue when audio changes occur
- Uses GPIO pins 5 (red), 6 (green), and 13 (blue)

### Volume Encoder
- Controls master volume using a rotary encoder
- Includes save functionality to persist volume settings
- Uses GPIO pins:
  - 23 (CLK)
  - 24 (DT)
  - 25 (SW)
  - 16 (Save button)

## config.py

The configuration file for all components. Key sections include:

### Sensor Configuration
- Main wheel sensor (GPIO17)
- Pedal sensor (GPIO27)
- Timing and threshold settings

### Hardware Settings
- RGB LED pin assignments and behavior
- Encoder pin assignments
- Volume control parameters

### Milestone Settings
- Time between milestones
- Number of milestones per mark
- Debug options

### Audio Settings
- Volume curves for each track
- Mixing and transition parameters

## Hardware Setup

### Required Components
1. Raspberry Pi 4B
2. 2× Hall effect sensors (for wheel and pedal)
3. 2× Magnets (for wheel and pedal)
4. 1× RGB LED (common cathode)
5. 1× Rotary encoder with push button
6. 1× Push button (for saving volume)
7. 3× 220Ω resistors (for LED)

### Pin Connections

#### Sensors
- Main Wheel Sensor → GPIO17 (pin 11)
- Pedal Sensor → GPIO27 (pin 13)

#### RGB LED
- Red → GPIO5 (pin 29) through 220Ω resistor
- Green → GPIO6 (pin 31) through 220Ω resistor
- Blue → GPIO13 (pin 33) through 220Ω resistor
- Common Ground → Any GND pin

#### Rotary Encoder
- CLK → GPIO23 (pin 16)
- DT → GPIO24 (pin 18)
- SW → GPIO25 (pin 22)
- VCC → 3.3V
- GND → Any GND pin

#### Volume Save Button
- Signal → GPIO16 (pin 36)
- GND → Any GND pin

### Wiring Diagram

![Mounting](https://github.com/user-attachments/assets/60cf8277-9cbf-4c12-9479-361631009aeb)

> Note: The wiring diagram needs to be updated to include the new components (RGB LED, rotary encoder, and save button)

## Usage

1. Connect all hardware components according to the pin assignments
2. Configure settings in `config.py` if needed
3. Run `legible.py`
4. Use the rotary encoder to adjust master volume
5. Press the save button to store volume settings
6. Monitor milestone progress through the RGB LED
7. Debug mode can be enabled in config.py for detailed sensor information
