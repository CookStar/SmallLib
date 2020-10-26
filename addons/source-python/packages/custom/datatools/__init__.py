# ../addons/source-python/packages/custom/datatools/__init__.py

"""Provides Data based functionality."""

# =============================================================================
# >> FORWARD IMPORTS
# =============================================================================
# Data Tools Imports
#   Base
from datatools.base import get_pointer
from datatools.base import create_pointer_pipe_from_file
from datatools.base import set_data_from_file
from datatools.base import set_pointer_from_file


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_pointer",
           "create_pointer_pipe_from_file",
           "set_data_from_file",
           "set_pointer_from_file",
           )

