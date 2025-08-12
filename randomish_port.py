#!/usr/bin/env python3

"""Software to attempt to come up with a random port for a new project"""

# Copyright 2025 Chris Engelhart
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import csv
import statistics
import random
import io
import requests


IANA_LIST = 'https://www.iana.org/assignments/service-names-port-numbers/' \
            'service-names-port-numbers.csv'
MIN_PORT = 1024
MAX_PORT = 49151


def csv2list(csvreader: csv.DictReader) -> list[bool]:
    """Turn a CSV DictReader into a list of True or False available ports"""
    full_list = [False] * 65536
    for line in csvreader:
        if not line['Port Number']:
            continue
        begin, _, end = line['Port Number'].partition('-')
        if not end:
            end = begin
        begin = int(begin)
        end = int(end)
        if begin < MIN_PORT or end > MAX_PORT:
            continue
        if line['Service Name'] or line['Transport Protocol']:
            continue
        if line['Description'] != 'Unassigned':
            continue
        for port in range(begin, end + 1):
            full_list[port] = True
    return full_list

def gen_alphanum() -> list[bool]:
    """Assuming 2 5-bit ASCII letters, return true/false list

    True is all the used numbers, False would be for non-alphabetic combos
    """
    char_list = [False] * 1024
    alpha = range(1, 27)
    for chars in range(1024):
        if int(chars / 32) in alpha and chars % 32 in alpha:
            char_list[chars] = True
    return char_list

def open_count(full_list: list[bool]) -> int:
    """Return a list of available ports for each block of 1024 ports"""
    msb_counts = [0] * 64
    for msb in range(64):
        msb_counts[msb] = sum(full_list[msb*1024:(msb+1)*1024])
    return msb_counts

def open_count_alpha(full_list: list[bool]) -> int:
    """Return a list of available alphabetically significant ports for each block of 1024 ports"""    
    msb_counts = [0] * 64
    alphanum = gen_alphanum()
    for msb in range(64):
        msb_counts[msb] = sum(a and b for a, b in zip(full_list[msb*1024:(msb+1)*1024], alphanum))
    return msb_counts

def load_iana_list(filename: str = None) -> list[bool]:
    """Load IANA port CSV list from a file"""
    if filename:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            port_list = csv2list(csv.DictReader(csvfile))
        return port_list
    result = requests.get(IANA_LIST, timeout=5)
    result.raise_for_status()
    port_list = csv2list(csv.DictReader(io.StringIO(result.text)))
    return port_list

def pick_a_start(port_list: list[bool]) -> tuple[int, int]:
    """Randomly pick a start port and list how many are available

    port_list is a list of ports whether they are available or not
    """
    opencounts = open_count(port_list)
    opencounts_a = open_count_alpha(port_list)
    weights = [a/1024.0 + b/676.0 for a, b in zip(opencounts, opencounts_a)]
    med = statistics.median(weights[1:48])
    while True:
        selected_start = random.choices(range(64), weights=weights)[0]
        if weights[selected_start] > med:
            return selected_start * 1024, opencounts_a[selected_start]

def _port_assign(start: int, chars: str) -> int:
    letters = [ord(x) for x in chars]
    assert len(letters) == 2
    for letter in letters:
        assert letter in range(64, 96)
    return (start*1024) + ((letters[0] % 32) * 32) + (letters[1] % 32)

def port_assign(start: int, chars: str) -> int:
    """Given a start and two characters, assign a port

    Note that the 'start' specified needs to be the actual start port
    """
    block_number, remainder = divmod(start, 1024)
    assert remainder == 0
    return _port_assign(block_number, chars)

def reverse_port_lookup(port_number: int) -> tuple[str, int]:
    """Given a port number, return the 2-letter code

    Also returns the 'start port' of the range.
    """
    msb, lsb = divmod(port_number, 1024)
    start_port = msb * 1024
    letter_nums = divmod(lsb, 32)
    letters = ''.join([chr(num + 64) for num in letter_nums])
    return letters, start_port

def cmd():
    """CMD line interface"""
    parser = argparse.ArgumentParser()
    parser.add_argument('letters')
    parser.add_argument('-i', '--iana-file')
    parser.add_argument('-s', '--start-port')
    args = parser.parse_args()
    port_list = load_iana_list(args.iana_file)
    if args.start_port:
        start = int(args.start_port)
    else:
        start, quality = pick_a_start(port_list)
        print(start, quality)
    port = port_assign(start, args.letters.upper())
    print(port)
    assert port_list[port]

if __name__ == '__main__':
    cmd()
