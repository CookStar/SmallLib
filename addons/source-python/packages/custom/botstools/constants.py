# ../addons/source-python/packages/custom/botstools/constants.py

"""Provides constant values that are bot based."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Enum
from enum import IntEnum


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('BotDifficulty',
           )


# =============================================================================
# >> ENUMERATORS
# =============================================================================
class BotDifficulty(IntEnum):
    """Bot difficulty wrapper enumerator."""

    EASY = 1
    NORMAL = 2
    HARD = 4
    EXPERT = 8

