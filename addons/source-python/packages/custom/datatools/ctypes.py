# ../ctypes.py

"""Provides a base way to get and set ctype data from config file."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory.manager import manager

# Memory Tools Imports
#   Conventions
from memorytools.ctypes import get_ctype_function


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("create_ctype_pipe_from_file",
           )


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def create_ctype_pipe_from_file(file, auto_dealloc=True):
    pipe = manager.create_pipe_from_file(file)
    cls_dict = {}
    for name in [attr for attr in pipe.__dict__.keys() if not attr.startswith("__")]:
        if auto_dealloc:
            cls_dict[name] = get_ctype_function(getattr(pipe, name))
        else:
            cls_dict[name] = get_ctype_function(getattr(pipe, name), auto_dealloc=False).ctype

    return type("CtypePipe", (object,), cls_dict)

