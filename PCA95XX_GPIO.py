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
from PCA95XX import PCA95XX


class PCA95XX_GPIO(object):
    """
    RPi.GPIO compatible interface for PCA95XX You can pass this class along to anything that expects an RPi.GPIO
    module and it should work fine.
    """
    OUT: int = 0
    IN: int = 1
    BCM: int = 0
    BOARD: int = 0

    def __init__(self, busnum, address, num_gpios):
        self.chip = PCA95XX(busnum, address, num_gpios)

    def setmode(self, mode):
        # do nothing
        pass

    def setup(self, pin, mode):
        self.chip.config(pin, mode)

    def input(self, pin):
        return self.chip.input(pin)

    def output(self, pin, value):
        self.chip.output(pin, value)
