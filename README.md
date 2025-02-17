# legible_journey
Legible_journey art project

## wheel_meter.py

> Please note that this is only the program that tests the feasibility of the measurements we want to make during the experience.

This program reads the output signal of a Hall sensor to measure the rotation speed of a wheel on with a magnet attached. It is meant to run on a Raspberry Pi (uses the ``gpiozero`` library).

### How it works

1. When the program is executed, it asks for a wheel diameter. This is useful to determine the "distance" covered by the wheel.
2. Every 2 seconds (this is the default period, you can change the ``PERIOD`` variable to modify it), the program will update the speed measured from the time difference and the amount of times the magnet went by the Hall sensor.
3. The program will print the results accordingly after each measure.
