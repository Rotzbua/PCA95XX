# Copyright 2012 Daniel Berlin
# Copyright 2019-2020 Ludwig Grill
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import platform
from typing import List

if platform.system() == 'Windows':
    # Replace libraries by fake ones
    import sys
    import fake_rpi

    sys.modules['RPi'] = fake_rpi.RPi  # Fake RPi (GPIO)
    sys.modules['smbus'] = fake_rpi.smbus  # Fake smbus (I2C)

import smbus

# For the PCA 953X and 955X series, the chips with 8 GPIO's have these port numbers.
# The chips with 16 GPIO's have the first port for each type at double these numbers.
# IE The first config port is 6.
INPUT_PORT: int = 0
OUTPUT_PORT: int = 1
POLARITY_PORT: int = 2
CONFIG_PORT: int = 3


class PCA95XX(object):

    def __init__(self, busnum: int, address: int, num_gpios: int) -> None:
        assert 0 <= busnum <= 16, "Bus Number must be between 0 <= X <= 16."
        assert 0 <= address <= 0xFF, "Adress must be 0 <= X <= 0xFF."
        assert 0 <= num_gpios <= 16, "Number of GPIOs must be 0 <= X <= 16."

        self.bus = smbus.SMBus(busnum)
        self.address = address
        self.num_gpios = num_gpios
        if num_gpios <= 8:
            self.direction = self.bus.read_byte_date(address, CONFIG_PORT)
            self.outputvalue = self.bus.read_byte_data(address, OUTPUT_PORT)
        elif 8 < num_gpios <= 16:
            self.direction = self.bus.read_word_data(address, CONFIG_PORT << 1)
            self.outputvalue = self.bus.read_word_data(address, OUTPUT_PORT << 1)

    def _changebit(self, bitmap: int, bit: int, value: int) -> int:
        assert value == 1 or value == 0, "Value is %s must be 1 or 0." % value
        if value == 0:
            return bitmap & ~(1 << bit)
        elif value == 1:
            return bitmap | (1 << bit)

    def _readandchangepin(self, port: int, pin: int, value: int, portstate=None) -> int:
        """
        Change the value of bit PIN on port PORT to VALUE.  If the  current pin state for the port is passed in as
        PORTSTATE, we will avoid doing a read to get it.  The port pin state must be complete if passed in (IE it
        should not just be the value of the single pin we are trying to change).
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid." % (pin, self.num_gpios)

        if not portstate:
            if self.num_gpios <= 8:
                portstate = self.bus.read_byte_data(self.address, port)
            elif 8 < self.num_gpios <= 16:
                portstate = self.bus.read_word_data(self.address, port << 1)
        newstate = self._changebit(portstate, pin, value)
        if self.num_gpios <= 8:
            self.bus.write_byte_data(self.address, port, newstate)
        else:
            self.bus.write_word_data(self.address, port << 1, newstate)
        return newstate

    def polarity(self, pin: int, value: int) -> int:
        """
        Polarity inversion.
        """
        return self._readandchangepin(POLARITY_PORT, pin, value)

    def config(self, pin: int, mode: int) -> int:
        """
        Pin direction.
        """
        self.direction = self._readandchangepin(CONFIG_PORT, pin, mode, self.direction)
        return self.direction

    def config_all(self, mode: int) -> None:
        """
        Pin direction.
        """
        for pin in range(self.num_gpios):
            self.config(pin, mode)

    def output(self, pin: int, value: int) -> int:
        assert self.direction & (1 << pin) == 0, "Pin %s not set to output." % pin

        self.outputvalue = self._readandchangepin(OUTPUT_PORT, pin, value, self.outputvalue)
        return self.outputvalue

    def input(self, pin: int) -> int:
        assert self.direction & (1 << pin) != 0, "Pin %s not set to input." % pin

        if self.num_gpios <= 8:
            value = self.bus.read_byte_data(self.address, INPUT_PORT)
        elif 8 < self.num_gpios <= 16:
            value = self.bus.read_word_data(self.address, INPUT_PORT << 1)
        return value & (1 << pin)

    def input_state_pin(self, pin: int) -> int:
        """
        :param pin: Pin whose state should be returned.
        :return: 0 or 1 for pin state.
        """
        assert self.direction & (1 << pin) != 0, "Pin %s not set to input." % pin

        if self.num_gpios <= 8:
            value = self.bus.read_byte_data(self.address, INPUT_PORT)
        elif 8 < self.num_gpios <= 16:
            value = self.bus.read_word_data(self.address, INPUT_PORT << 1)
        return (value >> pin) & 0x01

    def input_state_list_all(self) -> List[int]:
        """
        Lists all states of the pins.
        (outdated) Note: No check for input state, you have to ensure that every pin is in input mode.
        :return: Integer list with state 0 or 1 of the according pin. E.g. [1, 0, 0, 1, 1, 1, 1, 1]
        """
        for pin in range(self.num_gpios):
            assert self.direction & (1 << pin) != 0, "Pin %s not set to input" % pin
        if self.num_gpios <= 8:
            value = self.bus.read_byte_data(self.address, INPUT_PORT)
        if 8 < self.num_gpios <= 16:
            value = self.bus.read_word_data(self.address, INPUT_PORT << 1)
        state_list = []
        for i in range(self.num_gpios):
            state_list.append((value >> i) & 0x01)
        return state_list
