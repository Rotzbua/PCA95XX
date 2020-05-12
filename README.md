# Interface Library for PCA953X

## Description

This library provides support for using PCA953X/5X chips.

## Requirements
### Library Dependencies
#### Linux / Raspberry
This library requires python-smbus, and as a result, currently requires root permissions.
#### Windows
For development under Windows, a mockup library like `fake_rpi` is required.

### Python version

Code is compatible with python >=3.6. Tested with python 3.7 (31.08.2019).

## Structure

Two interfaces are provided:

1. A class that supports all the functionality of the chip directly,
including changing polarity of pins. This class is named PCA95XX.

2. An interface that is compatible with RPi.GPIO. This class is named PCA95XX_GPIO


The RPi.GPIO compatible interface allows you to simply plug the I2C class
into existing libraries that expect RPi.GPIO.  It does not support edge events
or reading from output pins.


## Example

An example is AdaFruit's CharLCD library (which supports HD44780 compatible LCD's).

The following code will work with an LCD hooked up to a PCA9555:

```python
from PCA95XX_GPIO import PCA95XX_GPIO
from Adafruit_CharLCD import Adafruit_CharLCD

# Assumes a PCA9555 with 16 GPIO's at address 0x20
chip = PCA95XX_GPIO(0, 0x20, 16) 
# Assumes we are hooked up to pins 8, 9, 10, 11, 12, and 13 on the I2C chip
lcd = Adafruit_CharLCD(8,9, [10, 11, 12, 13], chip)
```

From this point, the lcd object will function as it does normally.

## Limitations

Support for the PCA957X series could be added, but the registers used are slightly different.

There is also a 24 GPIO version of these chips (TCA6424), which is not supported right now.
