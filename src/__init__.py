from dataclasses import dataclass
from pprint import pprint
from typing import List
import minimalmodbus
import renogy_RBT100LFP12S
import dbus
import dbus.service


DEV_PATHNAME = "/dev/ttyUSB0"
BATTERY_ADDRESSES = [0x0030, 0x0031, 0x0032, 0x0033]
POLL_INTERVAL = 1_000

# Setup the serial port once
with minimalmodbus.Instrument(
    DEV_PATHNAME, 0, close_port_after_each_call=True
) as setup:
    setup.serial.baudrate = 9600
    setup.serial.timeout = 0.2


batteries = dict(
    (
        address,
        minimalmodbus.Instrument(
            DEV_PATHNAME,
            address,
            close_port_after_each_call=True,
        ),
    )
    for address in BATTERY_ADDRESSES
)

for address, battery_modbus in batteries:
    pprint(address)

    initial_query = renogy_RBT100LFP12S.query(battery_modbus)
    pprint(initial_query)

    service_name = f"com.victronenergy.{DEV_PATHNAME}_{address}"
