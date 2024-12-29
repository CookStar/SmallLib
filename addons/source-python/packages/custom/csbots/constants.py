# ../addons/source-python/packages/custom/csbots/constants.py

"""Provides constant values that are Counter-Strike bot based."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Enum
from enum import auto
from enum import IntEnum
from enum import IntFlag


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('BotDifficulty',
           'Team',
           )


# =============================================================================
# >> ENUMERATORS
# =============================================================================
class BotDifficulty(IntFlag):
    """Bot difficulty wrapper enumerator."""

    EASY = auto()
    NORMAL = auto()
    HARD = auto()
    EXPERT = auto()


class Team(IntEnum):
    """Counter-Strike team wrapper enumerator."""

    UNASSIGNED = 0
    SPECTATOR = auto()
    TERRORIST = auto()
    CT = auto()

