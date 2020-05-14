# ../__init__.py

"""Provides Net Channel Handler listener based functionality."""

# =============================================================================
# >> FORWARD IMPORTS
# =============================================================================
# Net Channel Handler Listener Imports
#   Listeners
from .listeners import NetChannelHandlerLMD
from .listeners import OnConnectionStart
from .listeners import OnConnectionStop
from .listeners import OnConnectionClosing
from .listeners import OnConnectionCrashed
from .listeners import OnPacketStart
from .listeners import OnPacketEnd
from .listeners import OnFileRequested
from .listeners import OnFileReceived
from .listeners import OnFileDenied
from .listeners import OnFileSent
from .listeners import OnChangeSplitscreenUser
from .listeners import on_connection_start_listener_manager
from .listeners import on_connection_stop_listener_manager
from .listeners import on_connection_closing_listener_manager
from .listeners import on_connection_crashed_listener_manager
from .listeners import on_packet_start_listener_manager
from .listeners import on_packet_end_listener_manager
from .listeners import on_file_requested_listener_manager
from .listeners import on_file_received_listener_manager
from .listeners import on_file_denied_listener_manager
from .listeners import on_file_sent_listener_manager
from .listeners import on_change_splitscreen_user_listener_manager


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("NetChannelHandlerLMD",
           "OnConnectionStart",
           "OnConnectionStop",
           "OnConnectionClosing",
           "OnConnectionCrashed",
           "OnPacketStart",
           "OnPacketEnd",
           "OnFileRequested",
           "OnFileReceived",
           "OnFileDenied",
           "OnFileSent",
           "OnChangeSplitscreenUser",
           "on_connection_start_listener_manager",
           "on_connection_stop_listener_manager",
           "on_connection_closing_listener_manager",
           "on_connection_crashed_listener_manager",
           "on_packet_start_listener_manager",
           "on_packet_end_listener_manager",
           "on_file_requested_listener_manager",
           "on_file_received_listener_manager",
           "on_file_denied_listener_manager",
           "on_file_sent_listener_manager",
           "on_change_splitscreen_user_listener_manager",
           )
