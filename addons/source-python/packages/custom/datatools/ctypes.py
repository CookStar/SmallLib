# ../addons/source-python/packages/custom/datatools/ctypes.py

"""Provides a base way to get and set ctype data from config file."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory.manager import manager

# Memory Tools Imports
#   Memory Tools
from memorytools.ctypes import get_ctype_function


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("create_ctype_pipe_from_file",
           "set_ctype_data_from_file",
           )


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def create_ctype_pipe_from_file(file, auto_dealloc=True):
    """Create a ctype pipe from a file."""
    pipe = manager.create_pipe_from_file(file)
    cls_dict = {}
    for name in [attr for attr in pipe.__dict__.keys() if not attr.startswith("__")]:
        if auto_dealloc:
            cls_dict[name] = get_ctype_function(getattr(pipe, name))
        else:
            cls_dict[name] = get_ctype_function(getattr(pipe, name), auto_dealloc=False).ctype

    return type("CtypePipe", (object,), cls_dict)

def set_ctype_data_from_file(cls, file, auto_dealloc=True):
    """Registers a new ctype data from a file."""
    ctype_pipe = create_ctype_pipe_from_file(file, auto_dealloc)

    for name, value in ctype_pipe.__dict__.items():
        if not name.startswith("__"):
            setattr(cls, name, value)

