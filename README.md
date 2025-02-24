# legible_journey
Legible_journey art project

## legible.py

The project's main program. According to the speed of a bike's wheel, the program will adjust independently the volumes of 3 custom audio tracks. Its behaviour can be configured inside ``config.py``.

## wheel_meter.py

> Please note that this is only the program that tests the feasibility of the measurements we want to make during the experience.

This program reads the output signal of a Hall sensor to measure the rotation speed of a wheel on with a magnet attached. It is meant to run on a Raspberry Pi (uses the ``gpiozero`` library).

It is a dependency of ``legible.py``.

### How it works

1. When the program is executed, it asks for a wheel diameter. This is useful to determine the "distance" covered by the wheel.
2. Every 2 seconds (this is the default period, you can change the ``PERIOD`` variable to modify it), the program will update the speed measured from the time difference and the amount of times the magnet went by the Hall sensor.
3. The program will print the results accordingly after each measure.

## config.py

The configuration file for both ``legible.py`` and ``wheel_meter.py``.

It is a dependency of ``legible.py``.

> TODO: Explain the VOLUME_CURVES parameter with visuals

## Mounting

In order to use this program, you will need the appropriate electronic mounting. The example diagram below uses a Raspberry Pi.

![Mounting](https://github.com/user-attachments/assets/60cf8277-9cbf-4c12-9479-361631009aeb)
