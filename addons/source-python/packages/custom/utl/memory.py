# ../addons/source-python/packages/custom/utl/memory.py

"""Provides UtlMemory based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Paths
from paths import CUSTOM_DATA_PATH

# Utl Imports
#   Manager
from utl.manager import type_manager


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('UtlMemory',
           )


# =============================================================================
# >> UtlMemory
# =============================================================================
UtlMemory = type_manager.create_type_from_file(
    'UtlMemory',
    CUSTOM_DATA_PATH / 'utl' / 'memory' / 'CUtlMemory.ini',
)

