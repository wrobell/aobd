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


import aobd
from aobd.decoders import pid


def test_list_integrity():
    for mode, cmds in enumerate(aobd.commands._modes):
        for pid, cmd in enumerate(cmds):

            # make sure the command tables are in mode & PID order
            assert mode == cmd.get_mode_int(),      "Command is in the wrong mode list: %s" % cmd.name
            assert pid == cmd.get_pid_int(),        "The index in the list must also be the PID: %s" % cmd.name

            # make sure all the fields are set
            assert cmd.name != "",                  "Command names must not be null"
            assert cmd.name.isupper(),              "Command names must be upper case"
            assert ' ' not in cmd.name,             "No spaces allowed in command names"
            assert cmd.desc != "",                  "Command description must not be null"
            assert (mode >= 1) and (mode <= 9),     "Mode must be in the range [1, 9] (decimal)"
            assert (pid >= 0) and (pid <= 196),     "PID must be in the range [0, 196] (decimal)"
            assert cmd.bytes >= 0,                  "Number of return bytes must be >= 0"
            assert hasattr(cmd.decode, '__call__'), "Decode is not callable"


def test_unique_names():
    # make sure no two commands have the same name
    names = {}

    for cmds in aobd.commands._modes:
        for cmd in cmds:
            assert not names.__contains__(cmd.name), "Two commands share the same name: %s" % cmd.name
            names[cmd.name] = True


def test_getitem():
    # ensure that __getitem__ works correctly
    for cmds in aobd.commands._modes:
        for cmd in cmds:

            # by [mode][pid]
            mode = cmd.get_mode_int()
            pid  = cmd.get_pid_int()
            assert cmd == aobd.commands[mode, pid], "mode %d, PID %d could not be accessed through __getitem__" % (mode, pid)

            # by [name]
            assert cmd == aobd.commands[cmd.name], "command name %s could not be accessed through __getitem__" % (cmd.name)


def test_contains():

    for cmds in aobd.commands._modes:
        for cmd in cmds:

            # by (command)
            assert cmd in aobd.commands

            # by (mode, pid)
            mode = cmd.get_mode_int()
            pid  = cmd.get_pid_int()
            assert (mode, pid) in aobd.commands

            # by (name)
            assert cmd.name in aobd.commands

    # test things NOT in the tables, or invalid parameters
    assert '_modes' not in aobd.commands
    assert (-1, 0) not in aobd.commands
    assert (1, -1) not in aobd.commands
    try:
        [] in aobd.commands
        assert False, 'TypeError expected'
    except TypeError:
        pass


def test_pid_getters():
    # ensure that all pid getters are found
    pid_getters = aobd.commands.pid_commands()

    for cmds in aobd.commands._modes:
        for cmd in cmds:
            if cmd.decode == pid:
                assert cmd in pid_getters
