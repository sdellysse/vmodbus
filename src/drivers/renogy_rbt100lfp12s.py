from dataclasses import dataclass
from typing import List
import minimalmodbus


import opt.velib.vedbus


@dataclass(frozen=True)
class Payload:
    address: int
    cell_count: int
    dev_pathname: str
    env_temp_count: int
    modbus: minimalmodbus.Instrument
    service: opt.velib.vedbus.VeDbusService


def setup(address: int, dev_pathname: str, process_name: str, process_version: str):
    modbus = minimalmodbus.Instrument(
        dev_pathname,
        address,
        close_port_after_each_call=True,
    )

    modbus.serial.baudrate = 9600
    modbus.serial.timeout = 0.2

    serial = modbus.read_string(0x13F6, 4)
    manufacturer_version = modbus.read_string(0x13FE, 1)
    mainline_version = modbus.read_string(0x13FF, 2)
    communication_protocol_version = modbus.read_string(0x1401, 1)
    model = modbus.read_string(0x1402, 8)
    software_version = modbus.read_string(0x140A, 2)
    manufacturer_name = modbus.read_string(0x140C, 4)

    cell_count = modbus.read_register(0x1388, signed=False)
    env_temp_count = modbus.read_register(0x13AC, signed=False)

    high_voltage_limit_v = modbus.read_register(0x13B9, signed=False) * 0.1
    low_voltage_limit_v = modbus.read_register(0x13BA, signed=False) * 0.1
    maximum_charge_current_a = modbus.read_register(0x13BB, signed=True) * 0.01
    maximum_discharge_current_a = modbus.read_register(0x13BC, signed=True) * 0.01

    service = opt.velib.vedbus.VeDbusService(
        f"com.victronenergy.{dev_pathname}_{address}"
    )

    # static paths
    service.add_path("/Connected", 1)
    service.add_path("/DeviceInstance", f"{address}@{dev_pathname}")
    service.add_path(
        "/Info/BatteryLowVoltage",
        low_voltage_limit_v,
        gettextcallback=lambda _path, value: "{:0.2f}V".format(value),
    )
    service.add_path(
        "/Info/MaxChargeCurrent",
        maximum_charge_current_a,
        gettextcallback=lambda _path, value: "{:0.2f}A".format(value),
    )
    service.add_path(
        "/Info/MaxChargeVoltage",
        high_voltage_limit_v,
        gettextcallback=lambda _path, value: "{:0.2f}V".format(value),
    )
    service.add_path(
        "/Info/MaxDischargeCurrent",
        maximum_discharge_current_a,
        gettextcallback=lambda _path, value: "{:0.2f}A".format(value),
    )
    service.add_path(
        "/InstalledCapacity",
        100.0,
        gettextcallback=lambda _path, value: "{:0.2f}Ah".format(value),
    )
    service.add_path("/Management/Connection", f"Modbus: {address}@{dev_pathname}")
    service.add_path("/Management/ProcessName", process_name)
    service.add_path("/Management/ProcessVersion", process_version)
    service.add_path(
        "/ProductId", 0x0000
    )  # TODO Cannot find `products.c` this references
    service.add_path("/ProductName", f"RBT100LFP12S: {serial}")
    service.add_path("/System/NrOfCellsPerBattery", cell_count)
    service.add_path("/System/NrOfModulesOnline", cell_count)  # TODO check
    service.add_path("/System/NrOfModulesOffline", 0)  # TODO check
    service.add_path("/System/NrOfModulesBlockingCharge", 0)  # TODO check
    service.add_path("/System/NrOfModulesBlockingDischarge", 0)  # TODO check

    # dynamic paths
    service.add_path("/Alarms/CellImbalance", None, writeable=True)
    service.add_path("/Alarms/HighCellVoltage", None, writeable=True)
    service.add_path("/Alarms/HighChargeCurrent", None, writeable=True)
    service.add_path("/Alarms/HighChargeTemperature", None, writeable=True)
    service.add_path("/Alarms/HighDischargeCurrent", None, writeable=True)
    service.add_path("/Alarms/HighTemperature", None, writeable=True)
    service.add_path("/Alarms/HighVoltage", None, writeable=True)
    service.add_path("/Alarms/InternalFailure", None, writeable=True)
    service.add_path("/Alarms/LowCellVoltage", None, writeable=True)
    service.add_path("/Alarms/LowSoc", None, writeable=True)
    service.add_path("/Alarms/LowVoltage", None, writeable=True)
    service.add_path("/Alarms/LowChargeTemperature", None, writeable=True)
    service.add_path("/Alarms/LowTemperature", None, writeable=True)
    service.add_path("/Balancing", None, writeable=True)
    service.add_path(
        "/Capacity",
        None,
        writeable=True,
        gettextcallback=lambda _path, value: "{:0.2f}Ah".format(value),
    )
    service.add_path(
        "/Dc/0/Current",
        None,
        writeable=True,
        gettextcallback=lambda _path, value: "{:2.2f}A".format(value),
    )
    service.add_path(
        "/Dc/0/Power",
        None,
        writeable=True,
        gettextcallback=lambda _path, value: "{:0.2f}W".format(value),
    )
    service.add_path("/Dc/0/Temperature", None, writeable=True)
    service.add_path(
        "/Dc/0/Voltage",
        None,
        writeable=True,
        gettextcallback=lambda _path, value: "{:0.3f}V".format(value),
    )
    service.add_path("/History/ChargeCycles", None)
    service.add_path("/History/TotalAhDrawn", None, writeable=True)
    service.add_path("/Io/AllowToCharge", None, writeable=True)
    service.add_path("/Soc", None, writeable=True)
    service.add_path("/System/MaxCellTemperature", None, writeable=True)
    service.add_path("/System/MaxVoltageCellId", None, writeable=True)
    service.add_path("/System/MinCellTemperature", None, writeable=True)
    service.add_path(
        "/System/MinCellVoltage",
        None,
        writeable=True,
        gettextcallback=lambda _path, value: "{:0.3f}V".format(value),
    )
    service.add_path("/System/MinVoltageCellId", None, writeable=True)

    return Payload(
        address=address,
        cell_count=cell_count,
        dev_pathname=dev_pathname,
        env_temp_count=env_temp_count,
        modbus=modbus,
        service=service,
    )


def update(payload: Payload):
    cycle_count = payload.modbus.read_register(0x13B8, signed=False)
    bms_temp_c = payload.modbus.read_register(0x13AB, signed=True) * 0.1
    cell_voltages_v = [
        payload.modbus.read_register(0x1389 + index, signed=False) * 0.1
        for index in range(payload.cell_count)
    ]
    cell_temps_c = [
        payload.modbus.read_register(0x139A + index, signed=False) * 0.1
        for index in range(payload.cell_count)
    ]
    env_temps_c = [
        payload.modbus.read_register(0x13AD + index, sign=True) * 0.1
        for index in range(payload.env_temp_count)
    ]
    current_a = payload.modbus.read_register(0x13B2, signed=True) * 0.01
    voltage_v = payload.modbus.read_register(0x13B3, signed=False) * 0.1

    remaining_ah = (
        int(
            f'{"%0X" % payload.modbus.read_register(0x13b4 + 0)}{"%0X" % payload.modbus.read_register(0x13b4 + 1)}',
            16,
        )
        * 0.001
    )

    capacity_ah = (
        int(
            f'{"%0X" % payload.modbus.read_register(0x13b6 + 0)}{"%0X" % payload.modbus.read_register(0x13b6 + 1)}',
            16,
        )
        * 0.001
    )

    payload.service["/Capacity"] = capacity_ah
    payload.service["/Dc/0/Current"] = current_a
    payload.service["/Dc/0/Power"] = current_a * voltage_v
    payload.service["/Dc/0/Temperature"] = bms_temp_c
    payload.service["/Dc/0/Voltage"] = voltage_v
    payload.service["/History/ChargeCycles"] = cycle_count
    payload.service["/Soc"] = (remaining_ah / capacity_ah) * 100.0
    payload.service["/System/MaxCellTemperature"] = max(cell_temps_c)
    payload.service["/System/MaxVoltageCellId"] = cell_voltages_v.index(
        max(cell_voltages_v)
    )
    payload.service["/System/MinCellTemperature"] = min(cell_temps_c)
    payload.service["/System/MinVoltageCellId"] - cell_voltages_v.index(
        min(cell_voltages_v)
    )
