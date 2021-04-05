# ../addons/source-python/packages/custom/memorytools/__init__.py

"""Provides Memory based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory import find_binary
from memory import BinaryFile
from memory import Pointer
from memory.helpers import Array
from memory.manager import manager
from memory.manager import Type


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_jmp_address",
           "get_jmp_bytes",
           "get_jmp_short_address",
           "get_offset",
           "get_pointer",
           "get_relative_pointer",
           "get_relative_pointer_from_pointer",
           "mem_print",
           "mem_write",
           )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_singed_size_type = {
    1:Type.CHAR,
    4:Type.INT,
}

_unsinged_size_type = {
    1:Type.UCHAR,
    2:Type.USHORT,
    4:Type.UINT,
}


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_offset(binary, identifier, offset, size=4, srv_check=True):
    """Return the offset."""
    # Get the binary
    if not isinstance(binary, BinaryFile):
        binary = find_binary(binary, srv_check)

    return getattr(binary.find_address(identifier), 'get_' + _unsinged_size_type[size])(offset)

def get_pointer(binary, identifier, offset=0, level=0, srv_check=True):
    """Return the pointer."""
    # Get the binary
    if not isinstance(binary, BinaryFile):
        binary = find_binary(binary, srv_check)

    # Get the pointer
    pointer = binary.find_pointer(identifier, offset, level)

    # Raise an error if the pointer is invalid
    if not pointer:
        raise ValueError("Unable to find the pointer.")

    return pointer

def get_relative_pointer(binary, identifier, offset, size=4, srv_check=True):
    """Return the relative pointer."""
    # Get the binary
    if not isinstance(binary, BinaryFile):
        binary = find_binary(binary, srv_check)

    # Get the pointer
    pointer = binary.find_address(identifier)
    pointer += getattr(pointer, 'get_' + _singed_size_type[size])(offset)+offset+size

    return pointer

def get_relative_pointer_from_pointer(pointer, offset, size=4):
    """Return the relative pointer."""
    # Get the pointer
    pointer = Pointer(pointer)
    pointer += getattr(pointer, 'get_' + _singed_size_type[size])(offset)+offset+size

    return pointer

def get_jmp_address(base, dest):
    base_address = int(base)
    dest_address = int(dest)

    return ((dest_address - (base_address + 5)) & 0xFFFFFFFF)

def get_jmp_short_address(base, dest):
    base_address = int(base)
    dest_address = int(dest)

    relative_address = (dest_address - (base_address + 2))
    if (relative_address and
        relative_address <= 127 and
        relative_address >= -128):
        return (relative_address & 0xFF)

    return None

def get_jmp_bytes(base, dest, short=True):
    if short:
        jmp_address = get_jmp_short_address(base, dest)
        if jmp_address is not None:
            return b"\xeb"+((jmp_address).to_bytes(1, "little"))

    return b"\xe9"+((get_jmp_address(base, dest)).to_bytes(4, "little"))

def mem_print(pointer, length):
    data = Array(manager, False, Type.UCHAR, pointer, length)
    print(' '.join("{:02X}".format(i) for i in data))

def mem_write(path, pointer, length):
    data = Array(manager, False, Type.UCHAR, pointer, length)
    with open(path, "wb") as file:
        file.write(bytes([i for i in data]))

