# randomish-port
Small Python script to generate a randomish unregistered port

## Overview

Purpose is to help developers, home-labbers, etc come up with and use a port
scheme for services they develop or run.

### Problem

There are 2^16 TCP and UDP ports.  The first 1024 are for "well known services."  The last 16k or so are reserved for dynamic/outbound, etc.  The rest are available for registrations etc. This is plenty!

Typically, when we build or test something with a framework, a default port is used of 5000, 8000, 8080, or something of that nature.  For those of us who play with the same tools, this means that we need to pick additional ports, and we are stuck cycling through the same ports.  It is possible to just pick a random port, but that can be hard to keep track of.

If the first 1024 are reserved for well known services, what if an individual could carve our another 1024 for his/her own services, and manage those in an easy way, while reserving the ability to in the future register them with IANA.

### Solution

Here is where randomish-port comes in: it randomly "assigns" (picks) a block of 1024 that has a large number of available ports (there are about 23 such blocks).  Then, the user can specify a 2-letter code for a service they are developing.  Those 2 letters are converted into a 10 bit number, based on the 5-bit ASCII value of each letter, and an individual port is assigned.  randomish-port ensures the port is not currently assigned by IANA.

From there, a port can easily be "reverse lookuped" to determine the 2-letter code.

The advantages of this vs random or using lazy defaults:
- No conflict between systems
- All of one's services are grouped in a smallish managable range.  This aids in auditing, remembering, understanding what's out there
- Ability to recognize [more] easily what services are running on a given system based on port number
- Can hard-code default ports in clients, vs always having to look up and specify random port
- Allows one to attempt to register with IANA in the future if desired (probably rare but nice to have)

## Install

```
$ git clone https://github.com/ctengel/randomish-port.git
$ cd randomish-port
$ pip install -r requirements.txt
```

## Run CLI

Help:

```
$ ./randomish_port.py -h
usage: randomish_port.py [-h] [-i IANA_FILE] [-s START_PORT] letters

positional arguments:
  letters

options:
  -h, --help            show this help message and exit
  -i, --iana-file IANA_FILE
  -s, --start-port START_PORT
```

Assign a random from a new random range:


```
$ ./randomish_port.py rp
35840 669
36432
```

The range is 35840+; there are 669 available ports.  The port for service RP is 3642

Find an additional port in the same range

```
$ ./randomish_port.py -s 35840 ce
35941
```

The 35840 starting port in the range is provided.  The port for service CE is 35941

Reverse lookup from CLI is not currently possible.

## Incorporating Python module

Import and help:


```
>>> import randomish_port
>>> help(randomish_port)

FUNCTIONS

    load_iana_list(filename: str = None) -> list[bool]
        Load IANA port CSV list from a file

    pick_a_start(port_list: list[bool]) -> tuple[int, int]
        Randomly pick a start port and list how many are available

        port_list is a list of ports whether they are available or not

    port_assign(start: int, chars: str) -> int
        Given a start and two characters, assign a port

        Note that the 'start' specified needs to be the actual start port

    reverse_port_lookup(port_number: int) -> tuple[str, int]
        Given a port number, return the 2-letter code

        Also returns the 'start port' of the range.
```

Select a range randomly

```
>>> port_list = randomish_port.load_iana_list()
>>> start_port, _ = randomish_port.pick_a_start(port_list)
>>> start_port
35840
```

35840 was randomly selected as the starting port for this user.


Assign a port:

```
>>> randomish_port.port_assign(start_port, "RP")
36432
```

36432 is the port for the RP service

Reverse lookup:

```
>>> randomish_port.reverse_port_lookup(36432)
('RP', 35840)
```

36432 is for RP - additionally, we see 35480 is the starting port for this range, so it can be used for additional related services

## Dependencies
* requests
* pytests (development only)

## Developing

Pull requests and issues are welcome

Please ensure clean code and testing

pylint:
```
$ pylint-3 randomish_port.py 

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

pytest:
```
$ pytest test_randomish_port.py 
============================= test session starts ==============================
platform linux -- Python 3.13, pytest-8.3, pluggy-1.5
rootdir: /path/to/randomish-port
plugins: anyio-3.7
collected 7 items                                                              

test_randomish_port.py .......                                           [100%]

============================== 7 passed in 0.94s ===============================
```

## License

Copyright 2025 Chris Engelhart

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
