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

import logging
import time

from .__version__ import __version__
from .elm327 import ELM327
from .commands import commands
from .utils import Response


logger = logging.getLogger(__name__)


class OBD:
    """
        Class representing an OBD-II connection with it's assorted commands/sensors
    """

    def __init__(self, device, baudrate=38400):
        self.supported_commands = []
        self.port = ELM327(device, baudrate)


    async def connect(self):
        await self.port.connect()
        #await self.__load_commands() FIXME


    def close(self):
        """
        Close ELM327 port and set OBD instance to unconnected state.
        """
        logger.info('closing obd-ii port')
        try:
            if self.connected:
                self.port.close()
        finally:
            self.port = None
            self.supported_commands = []


    @property
    def connected(self):
        """ Returns a boolean for whether a successful serial connection was made """
        return self.port is not None and self.port.connected


    async def __load_commands(self):
        """
            Queries for available PIDs, sets their support status,
            and compiles a list of command objects.
        """

        logger.debug("querying for supported PIDs (commands)...")

        self.supported_commands = []

        pid_getters = commands.pid_getters()

        for get in pid_getters:
            # PID listing commands should sequentialy become supported
            # Mode 1 PID 0 is assumed to always be supported
            if not self.supports(get):
                continue

            response = await self.__send(get) # ask nicely

            if response.is_null():
                continue
            
            supported = response.value # string of binary 01010101010101

            # loop through PIDs binary
            for i in range(len(supported)):
                if supported[i] == "1":

                    mode = get.get_mode_int()
                    pid  = get.get_pid_int() + i + 1

                    if commands.has_pid(mode, pid):
                        c = commands[mode][pid]
                        c.supported = True

                        # don't add PID getters to the command list
                        if c not in pid_getters:
                            self.supported_commands.append(c)

        logger.debug("finished querying with %d commands supported" % len(self.supported_commands))


    def print_commands(self):
        """
            Utility function meant for working in interactive mode.
            Prints all commands supported by the car.
        """
        for c in self.supported_commands:
            print(str(c))


    def supports(self, c):
        """ Returns a boolean for whether the car supports the given command """
        return commands.has_command(c) and c.supported


    async def __send(self, c):
        """
            Back-end implementation of query()
            sends the given command, retrieves and parses the response
        """

        if not self.connected:
            logger.debug("Query failed, no connection available", True)
            return Response() # return empty response

        logger.debug("Sending command: %s" % str(c))

        # send command and retrieve message
        m = await self.port.query(c.get_command())

        if m is None:
            return Response() # return empty response
        else:
            return c(m) # compute a response object


    async def query(self, c, force=False):
        """
            primary API function. Sends commands to the car, and
            protects against sending unsupported commands.
        """

        # check that the command is supported
        if self.supports(c) or force:
            r = await self.__send(c)
            return r
        else:
            logger.debug("'%s' is not supported" % str(c), True)
            return Response() # return empty response
