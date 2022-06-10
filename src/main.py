import sys

sys.path.append("../opt")
sys.path.append("../src")

from dataclasses import dataclass
from typing import List
from time import sleep

import src.drivers.renogy_rbt100lfp12s

PROCESS_NAME = "VModbus"
PROCESS_VERSION = "0.0.2022-06-09"


@dataclass(frozen=True)
class ClientDef:
    address: int
    driver: str


@dataclass(frozen=True)
class DeviceDef:
    dev_pathname: str
    client_defs: List[ClientDef]


POLL_INTERVAL = 1_000
DEVICE_DEFS: List[DeviceDef] = [
    DeviceDef(
        dev_pathname="/dev/ttyUSB0",
        client_defs=[
            ClientDef(address=0x0030, driver="renogy_rbt100lfp12s"),
            ClientDef(address=0x0031, driver="renogy_rbt100lfp12s"),
            ClientDef(address=0x0032, driver="renogy_rbt100lfp12s"),
            ClientDef(address=0x0033, driver="renogy_rbt100lfp12s"),
        ],
    )
]


@dataclass(frozen=True)
class Client:
    driver: str
    payload: any


clients: List[Client] = []

for device_def in DEVICE_DEFS:
    print(f"<<<registering modbus: {device_def.dev_pathname}>>>")

    for client_def in device_def.client_defs:
        if client_def.driver == "renogy_rbt100lfp12s":
            clients.append(
                Client(
                    driver="renogy_rbt100lfp12s",
                    payload=src.drivers.renogy_rbt100lfp12s.setup(
                        address=client_def.address,
                        dev_pathname=device_def.dev_pathname,
                        process_name=PROCESS_NAME,
                        process_version=PROCESS_VERSION,
                    ),
                )
            )

while True:
    print("<<<polling>>>")
    for client in clients:
        if client.driver == "renogy_rbt100lfp12s":
            src.drivers.renogy_rbt100lfp12s.update(client.payload)

    sleep(POLL_INTERVAL / 1_000)
