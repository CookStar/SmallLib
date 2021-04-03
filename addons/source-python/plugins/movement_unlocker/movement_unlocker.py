# ../addons/source-python/plugins/movement_unlocker/movement_unlocker.py

"""Removes max speed limitation from players on the ground. Feels like CS:S."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Paths
from paths import PLUGIN_DATA_PATH

# Memory Tools Imports
#   Memory Tools
from memorytools.manager import create_patchers_from_file


# =============================================================================
# >> PATCHERS
# =============================================================================
patchers = create_patchers_from_file(PLUGIN_DATA_PATH / "movement_unlocker" / "patcher.ini")
patchers.patch()

