# ../addons/source-python/packages/custom/memorytools/conventions.py

"""Provides a helper calling conventions."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory import CallingConvention
from memory import Convention
from memory.manager import manager


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("CDECL_RETURN4",
           "FASTCALL_CALLER",
           )


# =============================================================================
# >> CLASSES
# =============================================================================
class CDECL_RETURN4(CallingConvention):
    default_convention = Convention.CDECL

    def get_pop_size(self):
        return 4


class FASTCALL_CALLER(CallingConvention):
    default_convention = Convention.FASTCALL

    def get_pop_size(self):
        return 0


manager.register_convention("CDECL_RETURN4", CDECL_RETURN4)
manager.register_convention("FASTCALL_CALLER", FASTCALL_CALLER)

