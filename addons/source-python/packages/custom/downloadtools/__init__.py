# ../addons/source-python/packages/custom/downloadtools/__init__.py

"""Provides Download based functionality."""

# =============================================================================
# >> FORWARD IMPORTS
# =============================================================================
# Python Imports
#   Ctypes
import ctypes
#   Pathlib
from pathlib import Path

# Source.Python Imports
#   Core
from core import SOURCE_ENGINE
#   Cvars
from cvars import ConVar
#   Paths
from paths import GAME_PATH
from paths import CUSTOM_DATA_PATH

# Cvar Tools Imports
#   Cvar Tools
from cvartools import CvarChecker

# Data Tools Imports
#   Data Tools
from datatools.ctypes import create_ctype_pipe_from_file


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("compress_file",
           "transfer_id",
          )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_ctype_pipe = create_ctype_pipe_from_file(
    CUSTOM_DATA_PATH / "downloadtools" / "data" / f"{SOURCE_ENGINE}.ini",
    auto_dealloc=False
)

net_buffer_to_buffer_compress = _ctype_pipe.net_buffer_to_buffer_compress
net_chan_is_file_in_waiting_list = _ctype_pipe.net_chan_is_file_in_waiting_list

net_compresspackets = ConVar("net_compresspackets")

sv_allowupload = CvarChecker("sv_allowupload", 1)

transfer_id = 0


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def compress_file(path, data=None):
    """Compresses the file or bytes and creates a ztmp file.

    Returns the compressed file size on successful compression,
    or the source file size on failure.

    :param pathlib.Path/str path:
        The source file path to be compressed.
    :param bytes data:
        The data to compress the file without opening it.
    :rtype: int
    """

    if isinstance(path, str):
        path = Path(GAME_PATH / path)

    suffix = path.suffix
    if suffix == ".ztmp":
        ztmp_path = path
    else:
        ztmp_path = path.with_suffix(suffix+".ztmp")

    if ztmp_path.exists():
        return ztmp_path.stat().st_size

    if data is None:
        with open(path, "rb") as file:
            data = file.read()

    input_length = len(data)

    output_data = bytearray(input_length)
    output = ctypes.c_char.from_buffer(output_data)

    output_length = ctypes.c_uint32(input_length)

    compressed = net_buffer_to_buffer_compress(
        ctypes.byref(output), ctypes.byref(output_length), data, input_length)
    if compressed:
        with open(ztmp_path, "wb") as file:
            file.write(output_data[:output_length.value])
        ztmp_path.chmod(0o644)
        return output_length.value
    else:
        return path.stat().st_size

