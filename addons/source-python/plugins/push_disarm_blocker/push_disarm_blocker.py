# ../addons/source-python/plugins/push_disarm_blocker/push_disarm_blocker.py

"""Blocks weapon disarm caused by weapon_shield push."""

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
patchers = create_patchers_from_file(PLUGIN_DATA_PATH / "push_disarm_blocker" / "patcher.ini")
patchers.patch()

