import sys

sys.path.append("../opt")
sys.path.append("../src")

from dataclasses import dataclass
from pprint import pprint
from typing import List
import minimalmodbus
from time import sleep

import src.drivers.renogy_rbt100lfp12s
import opt.velib.vedbus

PROCESS_NAME = "VModbus"
PROCESS_VERSION = "0.0.2022-06-09"

# These will eventually be from the config file
DEV_PATHNAME = "/dev/ttyUSB0"
BATTERY_ADDRESSES = [0x0030, 0x0031, 0x0032, 0x0033]
POLL_INTERVAL = 1_000
MODBUS_BAUD_RATE = 9600
MODBUS_TIMEOUT = 0.2

setup_once = minimalmodbus.Instrument(DEV_PATHNAME, 0, close_port_after_each_call=True)


@dataclass(frozen=True)
class Battery:
    address: int
    metadata: src.drivers.renogy_rbt100lfp12s.Metadata
    modbus: minimalmodbus.Instrument
    service: opt.velib.vedbus.VeDbusService


batteries: List[Battery] = []

print(f"<<<registering modbus: {DEV_PATHNAME}>>>")
for address in BATTERY_ADDRESSES:
    print(f"<<<address: {address}>>>")

    modbus = minimalmodbus.Instrument(
        DEV_PATHNAME,
        address,
        close_port_after_each_call=True,
    )
    modbus.serial.baudrate = MODBUS_BAUD_RATE
    modbus.serial.timeout = MODBUS_TIMEOUT

    metadata = src.drivers.renogy_rbt100lfp12s.metadata(modbus)
    pprint(metadata)

    service = src.drivers.renogy_rbt100lfp12s.service(
        address=address,
        dev_pathname=DEV_PATHNAME,
        process_name=PROCESS_NAME,
        process_version=PROCESS_VERSION,
    )
    pprint(service)

    battery = Battery(
        address=address, metadata=metadata, modbus=modbus, service=service
    )
    pprint(battery)

    batteries.append(battery)

while True:
    print("<<<polling>>>")
    for battery in batteries:
        pprint(battery)

        status = src.drivers.renogy_rbt100lfp12s.status(
            modbus=battery.modbus, metadata=battery.metadata
        )
        pprint(status)

        src.drivers.renogy_rbt100lfp12s.publish(service=battery.service, status=status)

    sleep(POLL_INTERVAL / 1_000)
