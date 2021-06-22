# ../addons/source-python/packages/custom/memorytools/__init__.py

"""Provides Memory based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Ctypes
from ctypes import c_ubyte
from ctypes import c_void_p
from ctypes import memmove

# Source.Python Imports
#   Memory
from memory import alloc
from memory import find_binary
from memory import BinaryFile
from memory import Pointer
#from memory.helpers import Array
#from memory.manager import manager
from memory.manager import Type


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_bytes",
           "get_call_bytes",
           "get_jmp_address",
           "get_jmp_bytes",
           "get_jmp_short_address",
           "get_offset",
           "get_pointer",
           "get_relative_pointer",
           "get_relative_pointer_from_pointer",
           "load_binary",
           "mem_print",
           "mem_write",
           "set_bytes",
           "set_global_addresses",
           "set_local_addresses",
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

def set_local_addresses(pointer, value, offsets):
    if isinstance(pointer, int):
        pointer = Pointer(pointer)

    value = int(value)
    for offset in offsets:
        pointer.set_uint(value, offset)

def set_global_addresses(pointer, offsets):
    if isinstance(pointer, int):
        pointer = Pointer(pointer)

    address = int(pointer)
    for offset in offsets:
        pointer.set_uint(pointer.get_uint(offset) + address, offset)

def get_bytes(pointer, length, offset=0):
    return bytes((c_ubyte*length).from_address(int(pointer)+offset))

def set_bytes(pointer, data, offset=0):
    if isinstance(data, bytearray):
        data = bytes(data)

    memmove(c_void_p(int(pointer)+offset), data, len(data))

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

def get_call_bytes(base, dest):
    return b"\xe8"+((get_jmp_address(base, dest)).to_bytes(4, "little"))

def get_jmp_bytes(base, dest, short=True):
    if short:
        jmp_address = get_jmp_short_address(base, dest)
        if jmp_address is not None:
            return b"\xeb"+((jmp_address).to_bytes(1, "little"))

    return b"\xe9"+((get_jmp_address(base, dest)).to_bytes(4, "little"))

def load_binary(path, auto_dealloc=True):
    with open(path, "rb") as file:
        data = file.read()

    length = len(data)

    binary = alloc(length, auto_dealloc)
    binary.unprotect(length)

    memmove(c_void_p(binary.address), data, length)

    return binary, length

def mem_print(pointer, length, offset=0):
    #data = Array(manager, False, Type.UCHAR, pointer, length)
    #print(' '.join("{:02X}".format(i) for i in data))
    data = get_bytes(pointer, length, offset)
    print(' '.join("{:02X}".format(i) for i in data))

def mem_write(path, pointer, length, offset=0):
    #data = Array(manager, False, Type.UCHAR, pointer, length)
    #with open(path, "wb") as file:
    #    file.write(bytes([i for i in data]))
    data = get_bytes(pointer, length, offset)
    with open(path, "wb") as file:
        file.write(data)

