"""pytests for randomish port"""


import csv
import io
import random
import statistics
import randomish_port


def _write_fake_csv(buffer: io.StringIO):
    writer = csv.DictWriter(buffer, fieldnames=['Port Number',
                                                'Transport Protocol',
                                                'Service Name',
                                                'Description'])
    writer.writeheader()
    for port in range(randomish_port.MIN_PORT):
        for proto in ('TCP', 'UDP'):
            writer.writerow({'Port Number': port,
                             'Transport Protocol': proto,
                             'Service Name': 'ABC',
                             'Description': 'A well known service'})
    for port in range(randomish_port.MIN_PORT, randomish_port.MIN_PORT * 2):
        for proto in ('TCP', 'UDP'):
            writer.writerow({'Port Number': port,
                             'Transport Protocol': 'TCP',
                             'Service Name': 'ABC',
                             'Description': 'A lesser known service'})
    port = randomish_port.MIN_PORT * 2
    while port <= randomish_port.MAX_PORT:
        writer.writerow({'Port Number': port,
                         'Transport Protocol': 'TCP',
                         'Service Name': 'ABC',
                         'Description': 'A random service'})
        next_port = min(port + random.randint(1,512), randomish_port.MAX_PORT)
        if next_port == port:
            break
        if next_port - port == 1:
            port = next_port
            continue
        if next_port - port == 2:
            writer.writerow({'Port Number': port + 1,
                             'Transport Protocol': '',
                             'Service Name': '',
                             'Description': 'Unassigned'})
            port = next_port
            continue
        writer.writerow({'Port Number': f"{port+1}-{next_port-1}",
                         'Transport Protocol': '',
                         'Service Name': '',
                         'Description': 'Unassigned'})
        port = next_port

def fake_port_list() -> list[bool]:
    """Return a fake port list"""
    buffer = io.StringIO()
    _write_fake_csv(buffer)
    buffer.seek(0)
    return randomish_port.csv2list(csv.DictReader(buffer))

def test_gen_alphanum():
    alphanum_list = randomish_port.gen_alphanum()
    assert len(alphanum_list) == 1024
    assert sum(alphanum_list) == 676

def test_port_assign():
    assert randomish_port.port_assign(1024, "CE") == 1024 + 3 * 32 + 5

def test_reverse_port_lookup():
    letters, start_port = randomish_port.reverse_port_lookup(1024 + 3 * 32 + 5)
    assert letters == "CE"
    assert start_port == 1024

def test_csv2list():
    port_list = fake_port_list()
    assert not port_list[53]
    assert sum(port_list)

def test_open_counts():
    counts_four = randomish_port.open_count([False]*(1024*64))
    for count in counts_four:
        assert count == 0
    counts_three = randomish_port.open_count_alpha([True]*(1024*64))
    for count in counts_three:
        assert count == 676
    port_list = fake_port_list()
    counts_one = randomish_port.open_count(port_list)
    assert len(counts_one) == 64
    assert counts_one[0] == 0
    assert statistics.mean(counts_one[1:48]) > 512
    counts_two = randomish_port.open_count_alpha(port_list)
    assert len(counts_two) == 64
    assert counts_two[0] == 0
    counts_two_mean = statistics.mean(counts_two[1:48])
    assert counts_two_mean > 676/2
    assert counts_two_mean < 676

def test_pick_a_start():
    port_list = fake_port_list()
    start, count = randomish_port.pick_a_start(port_list)
    assert start > 1024
    assert start < 48 * 1024
    assert count > 676/2

def test_load_iana_list():
    port_list = randomish_port.load_iana_list()
    assert len(port_list) == 1024*64
    assert not port_list[53]
    assert sum(port_list)
