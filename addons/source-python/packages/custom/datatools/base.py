# ../addons/source-python/packages/custom/datatools/base.py

"""Provides a base way to get and set data from config file."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Core
from core import GameConfigObj
#   Memory
from memory import find_binary
from memory.helpers import parse_data
from memory.helpers import Key
from memory.helpers import NO_DEFAULT
from memory.manager import TypeManager


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_pointer(binary, identifier, offset=0, level=0, srv_check=True):
    """Return the value pointer."""
    # Get the binary
    binary = find_binary(binary, srv_check)

    # Get the value pointer
    ptr = binary.find_pointer(identifier, offset, level)

    # Raise an error if the pointer is invalid
    if not ptr:
        raise ValueError("Unable to find the value pointer.")

    return ptr

def create_pointer_pipe_from_file(file, manager=None):
    """Create a value pointer pipe from a file."""
    if manager is None:
        manager = TypeManager()

    # Parse pointer data
    pointers = parse_data(
        manager,
        GameConfigObj(file), (
            (Key.BINARY, Key.as_str, NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, 0),
            (Key.LEVEL, Key.as_int, 0),
            (Key.SRV_CHECK, Key.as_bool, True),
        )
    )

    # Create the pointers
    cls_dict = {}
    for name, data in pointers:
        cls_dict[name] = get_pointer(*data)

    return type("PointerPipe", (object,), cls_dict)

def set_pointer_from_file(cls, file, manager=None):
    """Registers a new value pointers from a file."""
    pointer_pipe = create_pointer_pipe_from_file(file, manager)

    # Set the value pointer attribute
    for name, value in pointer_pipe.__dict__.items():
        if not name.startswith("__"):
            setattr(cls, name, value)

def set_data_from_file(cls, file, manager=None):
    """Registers a new data from a file."""
    if manager is None:
        manager = TypeManager()

    cls_dict = vars(manager.create_type_from_dict(
        cls.__class__.__name__,
        GameConfigObj(file),
    ))

    for name, value in cls_dict.items():
        if not name.startswith("_"):
            setattr(cls, name, value)

