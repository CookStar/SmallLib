# ../addons/source-python/plugins/dt_warning_blocker/dt_warning_blocker.py

"""Blocks the DataTable_Warning."""

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
patchers = create_patchers_from_file(PLUGIN_DATA_PATH / "dt_warning_blocker" / "patcher.ini")
patchers.patch()

