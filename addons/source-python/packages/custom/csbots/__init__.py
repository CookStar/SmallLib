# ../addons/source-python/packages/custom/csbots/__init__.py

"""Provides Counter-Strike bot based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory.manager import TypeManager

# Memory Tools Imports
#   Manager
from memorytools.manager import create_function_pipe_from_file
from memorytools.manager import create_type_from_file

# CSBots Imports
#   Paths
from csbots.paths import CSBOTS_ENTITIES_DATA_PATH
from csbots.paths import CSBOTS_FUNCTIONS_DATA_PATH


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('create_bot',
           'csbots_type_manager',
           )


# =============================================================================
# >> CSBOTS TYPE MANAGER
# =============================================================================
csbots_type_manager = TypeManager()


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
CSBot = create_type_from_file('CCSBot',
    CSBOTS_ENTITIES_DATA_PATH / 'CCSBot.ini', manager=csbots_type_manager)

functions = create_function_pipe_from_file(
    CSBOTS_FUNCTIONS_DATA_PATH / 'functions.ini', csbots_type_manager)


# =============================================================================
# >> FUNCTIONS
# =============================================================================
create_bot = functions.create_bot

