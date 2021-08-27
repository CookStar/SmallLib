# ../addons/source-python/packages/custom/botstools/_base.py

"""Provides a class used to interact with a specific bot."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Players
from players.entity import Player


# =============================================================================
# >> CLASSES
# =============================================================================
class Bot(Player):
    """Class used to interact directly with Bots."""

    # Instances of this class will be cached by default
    caching = True

