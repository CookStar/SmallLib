# ../addons/source-python/packages/custom/memorytools/__init__.py

"""Provides Memory based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Memory
from memory import find_binary


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_pointer",
           )


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_pointer(binary, identifier, offset=0, level=0, srv_check=True):
    """Return the pointer."""
    # Get the binary
    binary = find_binary(binary, srv_check)

    # Get the pointer
    ptr = binary.find_pointer(identifier, offset, level)

    # Raise an error if the pointer is invalid
    if not ptr:
        raise ValueError("Unable to find the pointer.")

    return ptr

