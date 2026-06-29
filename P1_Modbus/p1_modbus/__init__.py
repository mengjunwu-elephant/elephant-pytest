"""P1 Modbus RTU serial client."""



from p1_modbus.command_address import CommandAddress, UNVERIFIED_ADDRS

from p1_modbus.commands import P1Client

from p1_modbus.errors import ProtocolError

from p1_modbus.events import decode_collision_event, decode_limit_event

from p1_modbus.modbus_rtu import (

    ModbusRTU,

    build_read_pdu,

    build_write_pdu,

    parse_read_payload,

)

from p1_modbus.models import (

    BaseIoOutput,

    ConveyorControl,

    ConveyorParams,

    DigitalIoOutput,

    GripperParams,

    KinematicsInput,

    PreviewPose,

    RgbColor,

)

from p1_modbus.ultra_api import UltraArmP1Modbus



__version__ = "0.3.0"

__all__ = [

    "ModbusRTU",

    "P1Client",

    "UltraArmP1Modbus",

    "CommandAddress",

    "UNVERIFIED_ADDRS",

    "ProtocolError",

    "PreviewPose",

    "RgbColor",

    "GripperParams",

    "ConveyorParams",

    "ConveyorControl",

    "BaseIoOutput",

    "DigitalIoOutput",

    "KinematicsInput",

    "build_read_pdu",

    "build_write_pdu",

    "parse_read_payload",

    "decode_limit_event",

    "decode_collision_event",

    "__version__",

]


