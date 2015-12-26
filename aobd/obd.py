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
from .elm327 import ELM327, OBDError
from .commands import commands
from .utils import Response


logger = logging.getLogger(__name__)


class OBD:
    """
        Class representing an OBD-II connection with it's assorted commands/sensors
    """

    def __init__(self, device, baudrate=38400):
        self._commands = tuple()
        self.port = ELM327(device, baudrate)


    async def connect(self):
        await self.port.connect()
        #await self.__load_commands()


    async def query(self, cmd):
        logger.debug('sending command: {}'.format(cmd))

        msg = await self.port.query(cmd.get_command())
        return Response() if msg is None else cmd(msg)


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
            self._commands = []


    def supports(self, cmd):
        """ Returns a boolean for whether the car supports the given command """
        return commands.has_command(cmd) and cmd.supported


    @property
    def connected(self):
        """ Returns a boolean for whether a successful serial connection was made """
        return self.port is not None and self.port.connected


    @property
    def commands(self):
        return self._commands


    async def __load_commands(self):
        """
            Queries for available PIDs, sets their support status,
            and compiles a list of command objects.
        """

        logger.debug("querying for supported PIDs (commands)...")

        items = []

        pid_getters = commands.pid_getters()

        for get in pid_getters:
            # PID listing commands should sequentialy become supported
            # Mode 1 PID 0 is assumed to always be supported
            if not self.supports(get):
                continue

            response = await self.query(get) # ask nicely

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
                            items.append(c)

        self._commands = tuple(items)
        logger.info(
            'number of commands supported: {}'.format(len(self._commands))
        )


# vim: sw=4:et:ai
