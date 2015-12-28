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

import collections
import functools
import logging
import time

from .__version__ import __version__
from .elm327 import ELM327, OBDError
from .commands import COMMANDS
from .obdcmd import OBDCommand
from .utils import Response


logger = logging.getLogger(__name__)


def dispatch(func):
    """
    Like `functools.singledispatch` but for class methods.

    http://stackoverflow.com/a/24602374/722424
    """
    dispatcher = functools.singledispatch(func)
    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


class OBD:
    """
        Class representing an OBD-II connection with it's assorted commands/sensors
    """

    def __init__(self, device, baudrate=38400):
        self._commands = tuple()
        self.port = ELM327(device, baudrate)


    async def connect(self):
        await self.port.connect()
        await self._load_commands()


    @dispatch
    def query(self, cmd):
        raise NotImplementedError('Not implemented for {}'.format(type(cmd)))


    @query.register(OBDCommand)
    async def _query(self, cmd):
        logger.debug('sending command: {}'.format(cmd))
        msg = await self.port.query(cmd.get_command())
        return Response() if msg is None else cmd(msg)


    @query.register(collections.Iterable)
    def _query(self, cmd):
        return OBDIterator(self.port, cmd)


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
        return cmd in COMMANDS and cmd.supported


    @property
    def connected(self):
        """ Returns a boolean for whether a successful serial connection was made """
        return self.port is not None and self.port.connected


    @property
    def commands(self):
        return self._commands


    async def _load_commands(self):
        """
        Query vehicle OBD port for supported commands.

        Check if each PID available, set its support status and create
        collection of supported command objects.
        """
        logger.debug('querying for supported PID commands...')

        # Mode 1 PID 0 is assumed to always be supported
        pid_cmds = COMMANDS.pid_commands()
        responses = []
        for p in pid_cmds:
            r = await self.query(p)
            responses.append((p, r.value)) # if no response, then fail hard
            logger.debug('pid response: {}'.format(r.value))

            # r.value is string of 32 bits,
            # i.e.: 10111110001111101011100000010000
            assert len(r.value) == 32

            # if next pid not supported, bail out
            if r.value[-1] == '0':
                break

        items = (
            (p.get_mode_int(), p.get_pid_int() + i + 1)
            for p, v in responses
            for i, s in enumerate(v) if s == '1'
        )
        items = (
            COMMANDS[mode, pid] for mode, pid in items
            if (mode, pid) in COMMANDS
        )
        # skip PID commands
        items = tuple(c for c in items if c not in pid_cmds)
        for c in items:
            c.supported = True
        self._commands = items

        n = len(self._commands)
        logger.info('number of commands supported: {}'.format(n))



class OBDIterator:
    def __init__(self, port, commands):
        self.port = port
        self.commands = iter(commands)


    async def __aiter__(self):
        return self


    async def __anext__(self):
        cmd = next(self.commands, None)
        if not cmd:
            raise StopAsyncIteration()

        msg = await self.port.query(cmd.get_command())
        return Response() if msg is None else cmd(msg)


# vim: sw=4:et:ai
