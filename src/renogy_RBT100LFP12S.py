from ast import List
from dataclasses import dataclass
import minimalmodbus


@dataclass
class Result:
    model: str
    serial: str
    firmware: str
    manufacturer: str
    cell_count: int
    cell_voltages_v: List[int]
    cell_temps_c: List[int]
    current_a: float
    voltage_v: float
    remaining_ah: float
    capacity_ah: float


def query(modbus: minimalmodbus.Instrument):
    model = modbus.read_string(0x1402, 8)
    serial = modbus.read_string(0x13F6, 8)
    firmware = modbus.read_string(0x140A, 2)
    manufacturer = modbus.read_string(0x140C, 4)
    cell_count = modbus.read_register(0x1388, 0, signed=False)

    cell_voltages_v = [
        modbus.read_register(0x1389 + index, 1, signed=False)
        for index in range(cell_count)
    ]
    cell_temps_c = [
        modbus.read_register(0x139A + index, 1, signed=False)
        for index in range(cell_count)
    ]

    current_a = modbus.read_register(0x13B2, 1, signed=True)
    voltage_v = modbus.read_register(0x13B3, 1, signed=False)
    remaining_ah = (
        int(
            f'{"%0X" % modbus.read_register(0x13b4 + 0)}{"%0X" % modbus.read_register(0x13b4 + 1)}',
            16,
        )
        * 0.001
    )
    capacity_ah = (
        int(
            f'{"%0X" % modbus.read_register(0x13b6 + 0)}{"%0X" % modbus.read_register(0x13b6 + 1)}',
            16,
        )
        * 0.001
    )

    return Result(
        model=model,
        serial=serial,
        firmware=firmware,
        manufacturer=manufacturer,
        cell_count=cell_count,
        cell_temps_c=cell_temps_c,
        cell_voltages_v=cell_voltages_v,
        current_a=current_a,
        voltage_v=voltage_v,
        remaining_ah=remaining_ah,
        capacity_ah=capacity_ah,
    )
