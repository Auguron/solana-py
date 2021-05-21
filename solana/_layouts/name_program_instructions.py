"""Byte layouts for name program instructions."""
from enum import IntEnum

from construct import Int32ul, Int64ul, Bytes, Padding, Byte
from construct import Struct as cStruct
from construct import Switch, this

from .shared import PUBLIC_KEY_LAYOUT


class InstructionType(IntEnum):
    """Instruction types for system program."""
    CREATE = 0
    UPDATE = 1
    TRANSFER = 2
    DELETE = 3


_CREATE_LAYOUT = cStruct(
    # Javascript side of SPL Name Service does this -- do I also?
    "hashed_name_size" / Int32ul,
    "hashed_name" / Bytes(32),
    "lamports" / Int64ul,
    "space" / Int32ul
)

_UPDATE_LAYOUT = cStruct(
        "offset" / Int32ul,
        "size" / Int32ul,
        "input_data" / Bytes(this.size)
        )

_TRANSFER_LAYOUT = cStruct(
        "new_owner" / PUBLIC_KEY_LAYOUT
        )

_DELETE_LAYOUT = cStruct()


NAME_PROGRAM_INSTRUCTIONS_LAYOUT = cStruct(
    "instruction_type" / Byte,
    "args"
    / Switch(
        lambda this: this.instruction_type,
        {
            InstructionType.CREATE: _CREATE_LAYOUT,
            InstructionType.UPDATE: _UPDATE_LAYOUT,
            InstructionType.TRANSFER: _TRANSFER_LAYOUT,
            InstructionType.DELETE: _DELETE_LAYOUT,
        },
    ),
)
