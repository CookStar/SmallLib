# ../__init__.py

"""Provides Memory Tools based functionality."""

# =============================================================================
# >> FORWARD IMPORTS
# =============================================================================
# Memory Tools Imports
#   Ctypes
from .ctypes import get_ctype_argtypes
from .ctypes import get_ctype_calling_convention
from .ctypes import get_ctype_from_data_type
from .ctypes import get_ctype_function
from .ctypes import CDECL
from .ctypes import FASTCALL
from .ctypes import FASTCALL_CALLER
from .ctypes import THISCALL
from .ctypes import STDCALL


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_ctype_argtypes",
           "get_ctype_calling_convention",
           "get_ctype_from_data_type",
           "get_ctype_function",
           "CDECL",
           "FASTCALL",
           "FASTCALL_CALLER",
           "THISCALL",
           "STDCALL",
           )

