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

import asyncio
import functools
import logging
import re
import serial
import time
from .protocols import *
from .utils import numBitsSet

logger = logging.getLogger(__name__)

# 30s to read data from serial device until prompt
TIMEOUT = 30

# get rid of
#
# - 0x00 (ELM spec page 9)
# - ELM prompt character
#
RE_CLEAN = re.compile(b'[\x00>]')
RE_SPLIT = re.compile(b'[\r\n]')

clean_data = functools.partial(RE_CLEAN.sub, b'')
split_data = RE_SPLIT.split

class ELM327:
    """
        Provides interface for the vehicles primary ECU.
        After instantiation with a portname (/dev/ttyUSB0, etc...),
        the following functions become available:

            query()
            is_connected()
            close()
    """

    _SUPPORTED_PROTOCOLS = {
        #"0" : None, # automatic mode
        "1" : SAE_J1850_PWM,
        "2" : SAE_J1850_VPW,
        "3" : ISO_9141_2,
        "4" : ISO_14230_4_5baud,
        "5" : ISO_14230_4_fast,
        "6" : ISO_15765_4_11bit_500k,
        "7" : ISO_15765_4_29bit_500k,
        "8" : ISO_15765_4_11bit_250k,
        "9" : ISO_15765_4_29bit_250k,
        "A" : SAE_J1939,
        #"B" : None, # user defined 1
        #"C" : None, # user defined 2
    }

    def __init__(self, portname, baudrate, loop=None):
        """Initializes port by resetting device and gettings supported PIDs. """

        self.__connected   = False
        self.__port        = None
        self.__protocol    = None
        self.__primary_ecu = None # message.tx_id

        # ------------- open port -------------

        logger.debug('opening serial port {}'.format(portname))

        self.__port = serial.Serial(
            portname,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=1,
            bytesize=8,
            timeout=0,
        )

        self._loop = asyncio.get_event_loop() if loop is None else loop
        self._queue = asyncio.Queue()
        self._loop.add_reader(self.__port.fileno(), self._read_data)
        logger.debug(
            'started to watch serial port file descriptior {}'
            .format(self.__port.fileno())
        )


    async def connect(self):
        # ---------------------------- ATZ (reset) ----------------------------
        await self._send(b'ATZ') # wait 1 second for ELM to initialize
        # return data can be junk, so don't bother checking

        # -------------------------- ATE0 (echo OFF) --------------------------
        r = await self._send(b'ATE0')
        if not self.__isok(r, expectEcho=True):
            raise OBDError("ATE0 did not return 'OK'")

        # ------------------------- ATH1 (headers ON) -------------------------
        r = await self._send(b'ATH1')
        if not self.__isok(r):
            raise OBDError("ATH1 did not return 'OK', or echoing is still ON")

        # ------------------------ ATL0 (linefeeds OFF) -----------------------
        r = await self._send(b'ATL0')
        if not self.__isok(r):
            raise OBDError("ATL0 did not return 'OK'")

        # ---------------------- ATSPA8 (protocol AUTO) -----------------------
        r = await self._send(b'ATSPA8')
        if not self.__isok(r):
            raise OBDError("ATSPA8 did not return 'OK'")

        # -------------- 0100 (first command, SEARCH protocols) --------------
        # TODO: rewrite this using a "wait for prompt character"
        # rather than a fixed wait period
        r0100 = await self._send(b'0100')

        # ------------------- ATDPN (list protocol number) -------------------
        r = await self._send(b'ATDPN')

        if not r:
            raise OBDError("Describe protocol command didn't return ")

        p = r[0]

        # suppress any "automatic" prefix
        p = p[1:] if (len(p) > 1 and p.startswith("A")) else p[:-1]

        logger.info('protocol id: {}'.format(p))
        if p not in self._SUPPORTED_PROTOCOLS:
            raise OBDError("ELM responded with unknown protocol")

        # instantiate the correct protocol handler
        self.__protocol = self._SUPPORTED_PROTOCOLS[p]()

        # Now that a protocol has been selected, we can figure out
        # which ECU is the primary.

        m = self.__protocol(r0100)
        self.__primary_ecu = self.__find_primary_ecu(m)
        if self.__primary_ecu is None:
            raise OBDError("Failed to choose primary ECU")

        # ------------------------------- done -------------------------------
        logger.debug("Connection successful")
        self.__connected = True


    def __isok(self, lines, expectEcho=False):
        if not lines:
            return False
        if expectEcho:
            return len(lines) == 2 and lines[1] == 'OK'
        else:
            return len(lines) == 1 and lines[0] == 'OK'


    def __find_primary_ecu(self, messages):
        """
            Given a list of messages from different ECUS,
            (in response to the 0100 PID listing command)
            choose the ID of the primary ECU
        """

        if len(messages) == 0:
            return None
        elif len(messages) == 1:
            return messages[0].tx_id
        else:
            # first, try filtering for the standard ECU IDs
            test = lambda m: m.tx_id == self.__protocol.PRIMARY_ECU

            if bool([m for m in messages if test(m)]):
                return self.__protocol.PRIMARY_ECU
            else:
                # last resort solution, choose ECU
                # with the most PIDs supported
                best = 0
                tx_id = None

                for message in messages:
                    bits = sum([numBitsSet(b) for b in message.data_bytes])

                    if bits > best:
                        best = bits
                        tx_id = message.tx_id

                return tx_id


    def is_connected(self):
        return self.__connected and (self.__port is not None)


    def close(self):
        """
        Close serial port and set `ELM327` instance to unconnected state.
        """
        try:
            if self.is_connected():
                self.__write(b'ATZ')
                self.__port.close()
        finally:
            self.__connected = False
            self.__port = None
            self.__protocol = None
            self.__primary_ecu = None

            logger.debug('connection closed')


    async def query(self, cmd):
        """
            send() function used to service all OBDCommands

            Sends the given command string (rejects "AT" command),
            parses the response string with the appropriate protocol object.

            Returns the Message object from the primary ECU, or None,
            if no appropriate response was recieved.
        """
        if not self.is_connected():
            raise OBDError('Device not connected')

        if b'AT' in cmd.upper():
            raise OBDError('AT command not allowed')

        lines = await self._send(cmd)

        # parses string into list of messages
        messages = self.__protocol(lines)

        # select the first message with the ECU ID we're looking for
        # TODO: use ELM header settings to query ECU by address directly
        for message in messages:
            if message.tx_id == self.__primary_ecu:
                return message

        return None # no suitable response was returned


    def __write(self, cmd):
        """
            "low-level" function to write a string to the port
        """
        cmd += b'\r\n' # terminate
        logger.debug('sending: ' + repr(cmd))
        self.__port.flushInput() # dump everything in the input buffer
        self.__port.write(cmd) # turn the string into bytes and write
        self.__port.flush() # wait for the output buffer to finish transmitting
        logger.debug('data sent')


    def _read_data(self):
        data = self.__port.read(1024)
        self._queue.put_nowait(data)


    async def _read_until(self, stop):
        data = bytearray()
        try:
            while True:
                v = await asyncio.wait_for(self._queue.get(), timeout=TIMEOUT)

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('received: {}'.format(v))

                data.extend(v)
                if stop in v:
                    break
        except asyncio.TimeoutError:
            logger.warning('{} never received'.format(stop))
        return data


    async def _send(self, cmd):
        self.__write(cmd)

        data = await self._read_until(b'>')
        data = clean_data(data)
        data = split_data(data)

        lines = (s.strip() for s in data)
        lines = [s.decode() for s in lines if s]
        return lines



class OBDError(Exception):
    pass


# vim: sw=4:et:ai
