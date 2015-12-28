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

from .obdcmd import OBDCommand
from .decoders import *

logger = logging.getLogger(__name__)

# Define command tables
# NOTE: the SENSOR NAME field will be used as the dict key for that sensor
# NOTE: commands MUST be in PID order, one command per PID (for fast lookup using __mode1__[pid])

__mode1__ = [
    #                  sensor name                          description                   mode  cmd bytes       decoder
    OBDCommand('PIDS_A'                     , 'Supported PIDs [01-20]'                  , b'01', b'00', 4, pid                   , True), # the first PID getter is assumed to be supported
    OBDCommand('STATUS'                     , 'Status since DTCs cleared'               , b'01', b'01', 4, status                ),
    OBDCommand('FREEZE_DTC'                 , 'Freeze DTC'                              , b'01', b'02', 2, noop                  ),
    OBDCommand('FUEL_STATUS'                , 'Fuel System Status'                      , b'01', b'03', 2, fuel_status           ),
    OBDCommand('ENGINE_LOAD'                , 'Calculated Engine Load'                  , b'01', b'04', 1, percent               ),
    OBDCommand('COOLANT_TEMP'               , 'Engine Coolant Temperature'              , b'01', b'05', 1, temp                  ),
    OBDCommand('SHORT_FUEL_TRIM_1'          , 'Short Term Fuel Trim - Bank 1'           , b'01', b'06', 1, percent_centered      ),
    OBDCommand('LONG_FUEL_TRIM_1'           , 'Long Term Fuel Trim - Bank 1'            , b'01', b'07', 1, percent_centered      ),
    OBDCommand('SHORT_FUEL_TRIM_2'          , 'Short Term Fuel Trim - Bank 2'           , b'01', b'08', 1, percent_centered      ),
    OBDCommand('LONG_FUEL_TRIM_2'           , 'Long Term Fuel Trim - Bank 2'            , b'01', b'09', 1, percent_centered      ),
    OBDCommand('FUEL_PRESSURE'              , 'Fuel Pressure'                           , b'01', b'0A', 1, fuel_pressure         ),
    OBDCommand('INTAKE_PRESSURE'            , 'Intake Manifold Pressure'                , b'01', b'0B', 1, pressure              ),
    OBDCommand('RPM'                        , 'Engine RPM'                              , b'01', b'0C', 2, rpm                   ),
    OBDCommand('SPEED'                      , 'Vehicle Speed'                           , b'01', b'0D', 1, speed                 ),
    OBDCommand('TIMING_ADVANCE'             , 'Timing Advance'                          , b'01', b'0E', 1, timing_advance        ),
    OBDCommand('INTAKE_TEMP'                , 'Intake Air Temp'                         , b'01', b'0F', 1, temp                  ),
    OBDCommand('MAF'                        , 'Air Flow Rate (MAF)'                     , b'01', b'10', 2, maf                   ),
    OBDCommand('THROTTLE_POS'               , 'Throttle Position'                       , b'01', b'11', 1, percent               ),
    OBDCommand('AIR_STATUS'                 , 'Secondary Air Status'                    , b'01', b'12', 1, air_status            ),
    OBDCommand('O2_SENSORS'                 , 'O2 Sensors Present'                      , b'01', b'13', 1, noop                  ),
    OBDCommand('O2_B1S1'                    , 'O2: Bank 1 - Sensor 1 Voltage'           , b'01', b'14', 2, sensor_voltage        ),
    OBDCommand('O2_B1S2'                    , 'O2: Bank 1 - Sensor 2 Voltage'           , b'01', b'15', 2, sensor_voltage        ),
    OBDCommand('O2_B1S3'                    , 'O2: Bank 1 - Sensor 3 Voltage'           , b'01', b'16', 2, sensor_voltage        ),
    OBDCommand('O2_B1S4'                    , 'O2: Bank 1 - Sensor 4 Voltage'           , b'01', b'17', 2, sensor_voltage        ),
    OBDCommand('O2_B2S1'                    , 'O2: Bank 2 - Sensor 1 Voltage'           , b'01', b'18', 2, sensor_voltage        ),
    OBDCommand('O2_B2S2'                    , 'O2: Bank 2 - Sensor 2 Voltage'           , b'01', b'19', 2, sensor_voltage        ),
    OBDCommand('O2_B2S3'                    , 'O2: Bank 2 - Sensor 3 Voltage'           , b'01', b'1A', 2, sensor_voltage        ),
    OBDCommand('O2_B2S4'                    , 'O2: Bank 2 - Sensor 4 Voltage'           , b'01', b'1B', 2, sensor_voltage        ),
    OBDCommand('OBD_COMPLIANCE'             , 'OBD Standards Compliance'                , b'01', b'1C', 1, obd_compliance        ),
    OBDCommand('O2_SENSORS_ALT'             , 'O2 Sensors Present (alternate)'          , b'01', b'1D', 1, noop                  ),
    OBDCommand('AUX_INPUT_STATUS'           , 'Auxiliary input status'                  , b'01', b'1E', 1, noop                  ),
    OBDCommand('RUN_TIME'                   , 'Engine Run Time'                         , b'01', b'1F', 2, seconds               ),

    #                  sensor name                          description                   mode  cmd bytes       decoder
    OBDCommand('PIDS_B'                     , 'Supported PIDs [21-40]'                  , b'01', b'20', 4, pid                   ),
    OBDCommand('DISTANCE_W_MIL'             , 'Distance Traveled with MIL on'           , b'01', b'21', 2, distance              ),
    OBDCommand('FUEL_RAIL_PRESSURE_VAC'     , 'Fuel Rail Pressure (relative to vacuum)' , b'01', b'22', 2, fuel_pres_vac         ),
    OBDCommand('FUEL_RAIL_PRESSURE_DIRECT'  , 'Fuel Rail Pressure (direct inject)'      , b'01', b'23', 2, fuel_pres_direct      ),
    OBDCommand('O2_S1_WR_VOLTAGE'           , '02 Sensor 1 WR Lambda Voltage'           , b'01', b'24', 4, sensor_voltage_big    ),
    OBDCommand('O2_S2_WR_VOLTAGE'           , '02 Sensor 2 WR Lambda Voltage'           , b'01', b'25', 4, sensor_voltage_big    ),
    OBDCommand('O2_S3_WR_VOLTAGE'           , '02 Sensor 3 WR Lambda Voltage'           , b'01', b'26', 4, sensor_voltage_big    ),
    OBDCommand('O2_S4_WR_VOLTAGE'           , '02 Sensor 4 WR Lambda Voltage'           , b'01', b'27', 4, sensor_voltage_big    ),
    OBDCommand('O2_S5_WR_VOLTAGE'           , '02 Sensor 5 WR Lambda Voltage'           , b'01', b'28', 4, sensor_voltage_big    ),
    OBDCommand('O2_S6_WR_VOLTAGE'           , '02 Sensor 6 WR Lambda Voltage'           , b'01', b'29', 4, sensor_voltage_big    ),
    OBDCommand('O2_S7_WR_VOLTAGE'           , '02 Sensor 7 WR Lambda Voltage'           , b'01', b'2A', 4, sensor_voltage_big    ),
    OBDCommand('O2_S8_WR_VOLTAGE'           , '02 Sensor 8 WR Lambda Voltage'           , b'01', b'2B', 4, sensor_voltage_big    ),
    OBDCommand('COMMANDED_EGR'              , 'Commanded EGR'                           , b'01', b'2C', 1, percent               ),
    OBDCommand('EGR_ERROR'                  , 'EGR Error'                               , b'01', b'2D', 1, percent_centered      ),
    OBDCommand('EVAPORATIVE_PURGE'          , 'Commanded Evaporative Purge'             , b'01', b'2E', 1, percent               ),
    OBDCommand('FUEL_LEVEL'                 , 'Fuel Level Input'                        , b'01', b'2F', 1, percent               ),
    OBDCommand('WARMUPS_SINCE_DTC_CLEAR'    , 'Number of warm-ups since codes cleared'  , b'01', b'30', 1, count                 ),
    OBDCommand('DISTANCE_SINCE_DTC_CLEAR'   , 'Distance traveled since codes cleared'   , b'01', b'31', 2, distance              ),
    OBDCommand('EVAP_VAPOR_PRESSURE'        , 'Evaporative system vapor pressure'       , b'01', b'32', 2, evap_pressure         ),
    OBDCommand('BAROMETRIC_PRESSURE'        , 'Barometric Pressure'                     , b'01', b'33', 1, pressure              ),
    OBDCommand('O2_S1_WR_CURRENT'           , '02 Sensor 1 WR Lambda Current'           , b'01', b'34', 4, current_centered      ),
    OBDCommand('O2_S2_WR_CURRENT'           , '02 Sensor 2 WR Lambda Current'           , b'01', b'35', 4, current_centered      ),
    OBDCommand('O2_S3_WR_CURRENT'           , '02 Sensor 3 WR Lambda Current'           , b'01', b'36', 4, current_centered      ),
    OBDCommand('O2_S4_WR_CURRENT'           , '02 Sensor 4 WR Lambda Current'           , b'01', b'37', 4, current_centered      ),
    OBDCommand('O2_S5_WR_CURRENT'           , '02 Sensor 5 WR Lambda Current'           , b'01', b'38', 4, current_centered      ),
    OBDCommand('O2_S6_WR_CURRENT'           , '02 Sensor 6 WR Lambda Current'           , b'01', b'39', 4, current_centered      ),
    OBDCommand('O2_S7_WR_CURRENT'           , '02 Sensor 7 WR Lambda Current'           , b'01', b'3A', 4, current_centered      ),
    OBDCommand('O2_S8_WR_CURRENT'           , '02 Sensor 8 WR Lambda Current'           , b'01', b'3B', 4, current_centered      ),
    OBDCommand('CATALYST_TEMP_B1S1'         , 'Catalyst Temperature: Bank 1 - Sensor 1' , b'01', b'3C', 2, catalyst_temp         ),
    OBDCommand('CATALYST_TEMP_B2S1'         , 'Catalyst Temperature: Bank 2 - Sensor 1' , b'01', b'3D', 2, catalyst_temp         ),
    OBDCommand('CATALYST_TEMP_B1S2'         , 'Catalyst Temperature: Bank 1 - Sensor 2' , b'01', b'3E', 2, catalyst_temp         ),
    OBDCommand('CATALYST_TEMP_B2S2'         , 'Catalyst Temperature: Bank 2 - Sensor 2' , b'01', b'3F', 2, catalyst_temp         ),

    #                  sensor name                          description                   mode  cmd bytes       decoder
    OBDCommand('PIDS_C'                     , 'Supported PIDs [41-60]'                  , b'01', b'40', 4, pid                   ),
    OBDCommand('STATUS_DRIVE_CYCLE'         , 'Monitor status this drive cycle'         , b'01', b'41', 4, todo                  ),
    OBDCommand('CONTROL_MODULE_VOLTAGE'     , 'Control module voltage'                  , b'01', b'42', 2, todo                  ),
    OBDCommand('ABSOLUTE_LOAD'              , 'Absolute load value'                     , b'01', b'43', 2, todo                  ),
    OBDCommand('COMMAND_EQUIV_RATIO'        , 'Command equivalence ratio'               , b'01', b'44', 2, todo                  ),
    OBDCommand('RELATIVE_THROTTLE_POS'      , 'Relative throttle position'              , b'01', b'45', 1, percent               ),
    OBDCommand('AMBIENT_AIR_TEMP'           , 'Ambient air temperature'                 , b'01', b'46', 1, temp                  ),
    OBDCommand('THROTTLE_POS_B'             , 'Absolute throttle position B'            , b'01', b'47', 1, percent               ),
    OBDCommand('THROTTLE_POS_C'             , 'Absolute throttle position C'            , b'01', b'48', 1, percent               ),
    OBDCommand('ACCELERATOR_POS_D'          , 'Accelerator pedal position D'            , b'01', b'49', 1, percent               ),
    OBDCommand('ACCELERATOR_POS_E'          , 'Accelerator pedal position E'            , b'01', b'4A', 1, percent               ),
    OBDCommand('ACCELERATOR_POS_F'          , 'Accelerator pedal position F'            , b'01', b'4B', 1, percent               ),
    OBDCommand('THROTTLE_ACTUATOR'          , 'Commanded throttle actuator'             , b'01', b'4C', 1, percent               ),
    OBDCommand('RUN_TIME_MIL'               , 'Time run with MIL on'                    , b'01', b'4D', 2, minutes               ),
    OBDCommand('TIME_SINCE_DTC_CLEARED'     , 'Time since trouble codes cleared'        , b'01', b'4E', 2, minutes               ),
    OBDCommand('MAX_VALUES'                 , 'Various Max values'                      , b'01', b'4F', 4, noop                  ), # todo: decode this
    OBDCommand('MAX_MAF'                    , 'Maximum value for mass air flow sensor'  , b'01', b'50', 4, max_maf               ),
    OBDCommand('FUEL_TYPE'                  , 'Fuel Type'                               , b'01', b'51', 1, fuel_type             ),
    OBDCommand('ETHANOL_PERCENT'            , 'Ethanol Fuel Percent'                    , b'01', b'52', 1, percent               ),
    OBDCommand('EVAP_VAPOR_PRESSURE_ABS'    , 'Absolute Evap system Vapor Pressure'     , b'01', b'53', 2, abs_evap_pressure     ),
    OBDCommand('EVAP_VAPOR_PRESSURE_ALT'    , 'Evap system vapor pressure'              , b'01', b'54', 2, evap_pressure_alt     ),
    OBDCommand('SHORT_O2_TRIM_B1'           , 'Short term secondary O2 trim - Bank 1'   , b'01', b'55', 2, percent_centered      ), # todo: decode seconds value for banks 3 and 4
    OBDCommand('LONG_O2_TRIM_B1'            , 'Long term secondary O2 trim - Bank 1'    , b'01', b'56', 2, percent_centered      ),
    OBDCommand('SHORT_O2_TRIM_B2'           , 'Short term secondary O2 trim - Bank 2'   , b'01', b'57', 2, percent_centered      ),
    OBDCommand('LONG_O2_TRIM_B2'            , 'Long term secondary O2 trim - Bank 2'    , b'01', b'58', 2, percent_centered      ),
    OBDCommand('FUEL_RAIL_PRESSURE_ABS'     , 'Fuel rail pressure (absolute)'           , b'01', b'59', 2, fuel_pres_direct      ),
    OBDCommand('RELATIVE_ACCEL_POS'         , 'Relative accelerator pedal position'     , b'01', b'5A', 1, percent               ),
    OBDCommand('HYBRID_BATTERY_REMAINING'   , 'Hybrid battery pack remaining life'      , b'01', b'5B', 1, percent               ),
    OBDCommand('OIL_TEMP'                   , 'Engine oil temperature'                  , b'01', b'5C', 1, temp                  ),
    OBDCommand('FUEL_INJECT_TIMING'         , 'Fuel injection timing'                   , b'01', b'5D', 2, inject_timing         ),
    OBDCommand('FUEL_RATE'                  , 'Engine fuel rate'                        , b'01', b'5E', 2, fuel_rate             ),
    OBDCommand('EMISSION_REQ'               , 'Designed emission requirements'          , b'01', b'5F', 1, noop                  ),
]


# mode 2 is the same as mode 1, but returns values from when the DTC occured
__mode2__ = []
for c in __mode1__:
    c = c.clone()
    c.mode = '02'
    c.name = 'DTC_' + c.name
    c.desc = 'DTC ' + c.desc
    __mode2__.append(c)


__mode3__ = [
    #                  sensor name                          description                   mode  cmd bytes       decoder
    OBDCommand('GET_DTC'                    , 'Get DTCs'                                , b'03', b'' , 0, dtc                    , True),
]

__mode4__ = [
    #                  sensor name                          description                   mode  cmd bytes       decoder
    OBDCommand('CLEAR_DTC'                  , 'Clear DTCs and Freeze data'              , b'04', b'' , 0, noop                   , True),
]

__mode7__ = [
    #                  sensor name                          description                   mode  cmd bytes       decoder
    OBDCommand('GET_FREEZE_DTC'             , 'Get Freeze DTCs'                         , b'07', b'' , 0, dtc                    , True),
]



# assemble the command tables by mode, and allow access by sensor name
class Commands():
    def __init__(self):

        # allow commands to be accessed by mode and PID
        self.modes = [
            [],
            __mode1__,
            __mode2__,
            __mode3__,
            __mode4__,
            [],
            [],
            __mode7__
        ]

        # allow commands to be accessed by sensor name
        self.__dict__.update({c.name: c for m in self.modes for c in m})


    def __getitem__(self, key):
        """
        Get command by name or (mode, pid).

        For example::

            obd.commands.RPM
            obd.commands["RPM"]
            obd.commands[1][12] # mode 1, PID 12 (RPM)

        """

        if isinstance(key, int):
            return self.modes[key]
        elif isinstance(key, str) or isinstance(key, unicode):
            return self.__dict__[key]
        else:
            raise TypeError('OBD command can be retrieved by name or PID value')


    def __len__(self):
        """
        Return number of supported commands.
        """
        return sum(len(m) for m in self.modes)


    def pid_getters(self):
        """
        Get list of PID GET commands.
        """
        # pid: GET commands have a special decoder
        return [c for m in self.modes for c in m if c.decode == pid]


    def has_command(self, cmd):
        """
        Check if command exists.
        """
        if not isinstance(cmd, OBDCommand):
            raise TypeError('Command should be OBDCommand instance')
        return c in self.__dict__.values()


    def has_pid(self, mode, pid):
        """
        Checks if command exists using mode and pid.
        """
        if not isinstance(mode, int) or not isinstance(pid, int):
            raise TypeError('Mode and pid should be integer values')
        return 0 <= mode < len(self.modes) and 0 <= pid < len(self.modes[mode])


# export this object
commands = Commands()

# vim: sw=4:et:ai
