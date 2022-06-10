from dataclasses import dataclass
from typing import List
import minimalmodbus


import opt.velib.vedbus

MODBUS_BAUD_RATE = 9600
MODBUS_TIMEOUT = 0.2


@dataclass(frozen=True)
class Metadata:
    cell_count: int
    communication_protocol_version: str
    env_temp_count: int
    high_voltage_limit_v: float
    low_voltage_limit_v: float
    mainline_version: str
    manufacturer_name: str
    manufacturer_version: str
    maximum_charge_current_a: float
    maximum_discharge_current_a: float
    model: str
    serial: str
    software_version: str


def metadata(modbus: minimalmodbus.Instrument):
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

    return Metadata(
        cell_count=cell_count,
        communication_protocol_version=communication_protocol_version,
        env_temp_count=env_temp_count,
        high_voltage_limit_v=high_voltage_limit_v,
        low_voltage_limit_v=low_voltage_limit_v,
        mainline_version=mainline_version,
        manufacturer_name=manufacturer_name,
        manufacturer_version=manufacturer_version,
        maximum_charge_current_a=maximum_charge_current_a,
        maximum_discharge_current_a=maximum_discharge_current_a,
        model=model,
        serial=serial,
        software_version=software_version,
    )


def service(address: int, dev_pathname: str, process_name: str, process_version: str):
    service = opt.velib.vedbus.VeDbusService(
        f"com.victronenergy.{dev_pathname}_{address}"
    )

    # static paths
    service.add_path("/Connected", 1)
    service.add_path("/DeviceInstance", f"{address}@{dev_pathname}")
    service.add_path(
        "/Info/BatteryLowVoltage",
        metadata.low_voltage_limit_v,
        gettextcallback=lambda _path, value: "{:0.2f}V".format(value),
    )
    service.add_path(
        "/Info/MaxChargeCurrent",
        metadata.maximum_charge_current_a,
        gettextcallback=lambda _path, value: "{:0.2f}A".format(value),
    )
    service.add_path(
        "/Info/MaxChargeVoltage",
        metadata.high_voltage_limit_v,
        gettextcallback=lambda _path, value: "{:0.2f}V".format(value),
    )
    service.add_path(
        "/Info/MaxDischargeCurrent",
        metadata.maximum_discharge_current_a,
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
    service.add_path("/ProductName", "Renogy RBT100LFP12S Battery")
    service.add_path("/System/NrOfCellsPerBattery", metadata.cell_count)
    service.add_path("/System/NrOfModulesOnline", metadata.cell_count)  # TODO check
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

    return service


@dataclass(frozen=True)
class Status:
    bms_temp_c: float
    capacity_ah: float
    cell_temps_c: List[float]
    cell_voltages_v: List[float]
    current_a: float
    cycle_count: int
    env_temps_c: List[float]
    remaining_ah: float
    voltage_v: float


def status(modbus: minimalmodbus.Instrument, metadata: Metadata):
    cycle_count = modbus.read_register(0x13B8, signed=False)
    bms_temp_c = modbus.read_register(0x13AB, signed=True) * 0.1
    cell_voltages_v = [
        modbus.read_register(0x1389 + index, signed=False) * 0.1
        for index in range(metadata.cell_count)
    ]
    cell_temps_c = [
        modbus.read_register(0x139A + index, signed=False) * 0.1
        for index in range(metadata.cell_count)
    ]
    env_temps_c = [
        modbus.read_register(0x13AD + index, sign=True) * 0.1
        for index in range(metadata.env_temp_count)
    ]
    current_a = modbus.read_register(0x13B2, signed=True) * 0.01
    voltage_v = modbus.read_register(0x13B3, signed=False) * 0.1
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

    return Status(
        bms_temp_c=bms_temp_c,
        capacity_ah=capacity_ah,
        cell_temps_c=cell_temps_c,
        cell_voltages_v=cell_voltages_v,
        current_a=current_a,
        cycle_count=cycle_count,
        env_temps_c=env_temps_c,
        remaining_ah=remaining_ah,
        voltage_v=voltage_v,
    )


def publish(service: opt.velib.vedbus.VeDbusService, status: Status):
    service["/Capacity"] = status.capacity_ah
    service["/Dc/0/Current"] = status.current_a
    service["/Dc/0/Power"] = status.current_a * status.voltage_v
    service["/Dc/0/Temperature"] = status.bms_temp_c
    service["/Dc/0/Voltage"] = status.voltage_v
    service["/History/ChargeCycles"] = status.cycle_count
    service["/Soc"] = (status.remaining_ah / status.capacity_ah) * 100.0
    service["/System/MaxCellTemperature"] = max(status.cell_temps_c)
    service["/System/MaxVoltageCellId"] = status.cell_voltages_v.index(
        max(status.cell_voltages_v)
    )
    service["/System/MinCellTemperature"] = min(status.cell_temps_c)
    service["/System/MinVoltageCellId"] - status.cell_voltages_v.index(
        min(status.cell_voltages_v)
    )
