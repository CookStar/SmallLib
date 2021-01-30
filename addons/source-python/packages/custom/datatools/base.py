# ../addons/source-python/packages/custom/datatools/base.py

"""Provides a base way to get and set data from config file."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import GameConfigObj
#   Memory
from memory.helpers import parse_data
from memory.helpers import Key
from memory.helpers import NO_DEFAULT
from memory.manager import manager
from memory.manager import TypeManager

# Memory Tools Imports
#   Memory Tools
from memorytools import get_pointer


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def create_pointer_pipe_from_file(file):
    """Create a value pointer pipe from a file."""
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

def set_pointer_from_file(cls, file):
    """Registers a new value pointers from a file."""
    pointer_pipe = create_pointer_pipe_from_file(file)

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

