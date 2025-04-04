# ../addons/source-python/packages/custom/csbots/entity.py

"""Provides a class used to interact with a specific Counter-Strike bot."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Importlib
from importlib import import_module

# Source.Python Imports
#   Core
from core import GAME_NAME
from core import SOURCE_ENGINE
#   Paths
from paths import CUSTOM_PACKAGES_PATH

# CSBots Imports
#   CSBots
import csbots._base


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('Bot',
           )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
if CUSTOM_PACKAGES_PATH.joinpath(
    'csbots', 'engines', SOURCE_ENGINE, GAME_NAME + '.py'
).isfile():

    # Import the game-specific 'Bot' class
    Bot = csbots._base.Bot = import_module(
        'csbots.engines.{engine}.{game}'.format(
            engine=SOURCE_ENGINE,
            game=GAME_NAME,
        )
    ).Bot

elif CUSTOM_PACKAGES_PATH.joinpath(
    'csbots', 'engines', SOURCE_ENGINE, '__init__.py'
).isfile():

    # Import the engine-specific 'Bot' class
    Bot = csbots._base.Bot = import_module(
        'csbots.engines.{engine}'.format(
            engine=SOURCE_ENGINE,
        )
    ).Bot

else:

    # Import the base 'Bot' class
    Bot = csbots._base.Bot

