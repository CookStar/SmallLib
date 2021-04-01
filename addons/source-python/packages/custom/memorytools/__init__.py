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
from memory.manager import Type


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_offset",
           "get_pointer",
           "get_relative_pointer",
           "get_relative_pointer_from_pointer",
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

