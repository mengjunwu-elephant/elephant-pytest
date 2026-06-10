"""P1 Modbus RTU serial client."""

from p1_modbus.commands import P1Client
from p1_modbus.errors import ProtocolError
from p1_modbus.events import decode_collision_event, decode_limit_event
from p1_modbus.models import (
    ConveyorParams,
    PreviewPose,
    RgbColor,
    GripperParams,
)
from p1_modbus.ultra_api import UltraArmP1Modbus

__version__ = "0.1.0"
__all__ = [
    "P1Client",
    "UltraArmP1Modbus",
    "ProtocolError",
    "PreviewPose",
    "RgbColor",
    "GripperParams",
    "ConveyorParams",
    "decode_limit_event",
    "decode_collision_event",
    "__version__",
]
