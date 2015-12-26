#
# aobd - vehicle on-board diagnostics library
#
# Copyright (C) 2015 by Artur Wroblewski <wrobell@pld-linux.org>
#
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
# Copyright 2009 Peter J. Creath
# Copyright 2015 Brendan Whitfield (bcw7044@rit.edu)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import binascii
import re
from .utils import *


FMT_CMD = '{}{}: {}'.format


class OBDCommand:
    def __init__(self, name, desc, mode, pid, returnBytes, decoder, supported=False):
        self.name       = name
        self.desc       = desc
        self.mode       = mode
        self.pid        = pid
        self.bytes      = returnBytes # number of bytes expected in return
        self.decode     = decoder
        self.supported  = supported

    def clone(self):
        return OBDCommand(self.name,
                          self.desc,
                          self.mode,
                          self.pid,
                          self.bytes,
                          self.decode)

    def get_command(self):
        return self.mode + self.pid # the actual command transmitted to the port

    def get_mode_int(self):
        return unhex(self.mode)

    def get_pid_int(self):
        return unhex(self.pid)

    def __call__(self, message):

        # create the response object with the raw data recieved
        # and reference to original command
        r = Response(self, message)
        
        # combine the bytes back into a hex string
        # TODO: rewrite decoders to handle raw byte arrays
        data = message.data_bytes
        if self.bytes: # zero bytes means flexible response
            data = data[:self.bytes]
        data = binascii.hexlify(data).decode().upper()

        # decoded value into the response object
        d = self.decode(data)
        r.value = d[0]
        r.unit  = d[1]

        return r

    def __str__(self):
        return FMT_CMD(self.mode.decode(), self.pid.decode(), self.desc)

    def __hash__(self):
        # needed for using commands as keys in a dict (see async.py)
        return hash((self.mode, self.pid))

    def __eq__(self, other):
        if isinstance(other, OBDCommand):
            return (self.mode, self.pid) == (other.mode, other.pid)
        else:
            return False
