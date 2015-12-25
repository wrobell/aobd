Python library for handling realtime sensor data from OBD-II vehicle
ports.

The code is fork of

-   <https://github.com/brendan-w/python-OBD>
-   <https://github.com/peterh/pyobd>
-   <https://github.com/Pbartek/pyobd-pi>

The goals

- use bytes only for command handling
- asyncio based API
- speed up serial port communication by getting all data at once instead of
  single byte reads
- multi-command communication
- improved error handling

Required Python 3.5 or later and `pySerial <https://pythonhosted.org/pyserial/>`_
library


Installation
------------

```Shell
$ pip install aobd
```

Basic Usage
-----------

```Python

import asyncio
import aobd

async def reader(dev):
    cmd = aobd.commands.RPM # select an OBD command (sensor)

    await dev.connect()             # connect to OBD-II device
    response = await dev.query(cmd) # send the command and parse the response

    print(response.value)
    print(response.unit)

loop = asyncio.get_event_loop()
dev = aobd.OBD('/dev/rfcomm0')
loop.run_until_complete(reader(dev))
```

Documentation
-------------

Commands
--------

Here are a handful of the supported commands (sensors). For a full list, see [the wiki](https://github.com/brendanwhitfield/python-OBD/wiki/Command-Tables)

*note: support for these commands will vary from car to car*

-   Calculated Engine Load
-   Engine Coolant Temperature
-   Fuel Pressure
-   Intake Manifold Pressure
-   Engine RPM
-   Vehicle Speed
-   Timing Advance
-   Intake Air Temp
-   Air Flow Rate (MAF)
-   Throttle Position
-   Engine Run Time
-   Fuel Level Input
-   Number of warm-ups since codes cleared
-   Barometric Pressure
-   Ambient air temperature
-   Commanded throttle actuator
-   Time run with MIL on
-   Time since trouble codes cleared
-   Hybrid battery pack remaining life
-   Engine fuel rate

License
-------

GNU GPL v2

This library is forked from:

Enjoy and drive safe!
