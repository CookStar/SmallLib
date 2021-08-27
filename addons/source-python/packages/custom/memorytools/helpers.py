# ../addons/source-python/packages/custom/memorytools/helpers.py

"""Provides helper classes/functions for memory functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
#   Binascii
import binascii


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("as_op_codes",
           )


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def as_op_codes(manager, value):
    """Convert a string into a byte string."""
    return binascii.unhexlify(value.replace(' ', ""))

