
########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2015 Brendan Whitfield (bcw7044@rit.edu)                   #
#                                                                      #
########################################################################
#                                                                      #
# utils.py                                                             #
#                                                                      #
# This file is part of python-OBD (a derivative of pyOBD)              #
#                                                                      #
# python-OBD is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# python-OBD is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with python-OBD.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                      #
########################################################################

import serial
import errno
import logging
import string
import time
import glob
import sys


logger = logging.getLogger(__name__)


class Unit:
    NONE    = None
    RATIO   = "Ratio"
    COUNT   = "Count"
    PERCENT = "%"
    RPM     = "RPM"
    VOLT    = "Volt"
    F       = "F"
    C       = "C"
    SEC     = "Second"
    MIN     = "Minute"
    PA      = "Pa"
    KPA     = "kPa"
    PSI     = "psi"
    KPH     = "kph"
    MPH     = "mph"
    DEGREES = "Degrees"
    GPS     = "Grams per Second"
    MA      = "mA"
    KM      = "km"
    LPH     = "Liters per Hour"


class Response():
    def __init__(self, command=None, message=None):
        self.command  = command
        self.message  = message
        self.value    = None
        self.unit     = Unit.NONE
        self.time     = time.time()

    def is_null(self):
        return (self.message == None) or (self.value == None)

    def __str__(self):
        if self.unit != Unit.NONE:
            return "%s %s" % (str(self.value), str(self.unit))
        else:
            return str(self.value)


class Status():
    def __init__(self):
        self.MIL           = False
        self.DTC_count     = 0
        self.ignition_type = ""
        self.tests         = []


class Test():
    def __init__(self, name, available, incomplete):
        self.name       = name
        self.available  = available
        self.incomplete = incomplete

    def __str__(self):
        a = "Available" if self.available else "Unavailable"
        c = "Incomplete" if self.incomplete else "Complete"
        return "Test %s: %s, %s" % (self.name, a, c)


def numBitsSet(n):
    # TODO: there must be a better way to do this...
    total = 0
    ref = 1
    for b in range(8):
        total += int(bool(n & ref))
        ref = ref << 1
    return total

def unhex(_hex):
    _hex = "0" if _hex == "" else _hex
    return int(_hex, 16)

def unbin(_bin):
    return int(_bin, 2)

def bitstring(_hex, bits=None):
    b = bin(unhex(_hex))[2:]
    if bits is not None:
        b = ('0' * (bits - len(b))) + b
    return b

def bitToBool(_bit):
    return (_bit == '1')

def twos_comp(val, num_bits):
    """compute the 2's compliment of int value val"""
    if( (val&(1<<(num_bits-1))) != 0 ):
        val = val - (1<<num_bits)
    return val

def isHex(_hex):
    return all(c in string.hexdigits for c in _hex)


# checks that a list of integers are consequtive
def contiguous(l, start, end):
    if not l:
        return False
    if l[0] != start:
        return False
    if l[-1] != end:
        return False

    # for consequtiveness, look at the integers in pairs
    pairs = zip(l, l[1:])
    if not all([p[0]+1 == p[1] for p in pairs]):
        return False

    return True


# vim: sw=4:et:ai
