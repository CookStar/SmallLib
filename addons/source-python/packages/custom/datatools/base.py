# ../base.py

"""Provides a base way to get and set data from config file."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Core
from core import GameConfigObj
#   Memory
from memory import find_binary
from memory.manager import TypeManager
from memory.helpers import Key
from memory.helpers import NO_DEFAULT
from memory.helpers import parse_data


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def value_pointer(binary, identifier, offset=0, level=0, srv_check=True):
    """Return the value pointers."""
    # Get the binary
    binary = find_binary(binary, srv_check)

    # Get the value pointer
    ptr = binary.find_pointer(identifier, offset, level)

    # Raise an error if the pointer is invalid
    if not ptr:
        raise ValueError("Unable to find the value pointer.")

    return ptr

def set_value_pointers_from_file(cls, f):
    """Registers a new value pointers from a file."""
    # Parse pointer data
    pointers = parse_data(
        TypeManager(),
        GameConfigObj(f), (
            (Key.BINARY, Key.as_str, NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, 0),
            (Key.LEVEL, Key.as_int, 0),
            (Key.SRV_CHECK, Key.as_bool, True),
        )
    )

    # Create the value pointer attribute
    for name, data in pointers:
        setattr(cls, name, value_pointer(*data))

def set_data_from_file(cls, f):
    """Registers a new data from a file."""
    cls_dict = vars(TypeManager().create_type_from_dict(
        cls.__class__.__name__,
        GameConfigObj(f),
    ))

    for name, value in cls_dict.items():
        setattr(cls, name, value)