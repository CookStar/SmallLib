# ../addons/source-python/plugins/timescale_override/timescale_override.py

"""Disables overriding of host_timescale by sv_cheats."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import PLATFORM
#   Cvars
from cvars import cvar
from cvars.flags import ConVarFlags
#   Paths
from paths import PLUGIN_DATA_PATH

# Memory Tools Imports
#   Memory Tools
from memorytools.manager import create_patchers_from_file


# =============================================================================
# >> CONVARS
# =============================================================================
host_timescale = cvar.find_var("host_timescale")
host_timescale.flags &= ~ConVarFlags.CHEAT


# =============================================================================
# >> PATCHERS
# =============================================================================
if PLATFORM == "windows":
    patchers = create_patchers_from_file(PLUGIN_DATA_PATH / "timescale_override" / "patcher.ini")
    patchers.patch()

