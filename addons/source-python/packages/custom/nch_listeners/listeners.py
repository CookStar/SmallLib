# ../addons/source-python/packages/custom/nch_listeners/listeners.py

"""Provides Net Channel Handler listeners."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Listeners
from listeners import ListenerManagerDecorator

# Net Channel Handler Listeners Imports
#   Net Channel Handler Listeners
from nch_listeners.manager import on_connection_start_listener_manager
from nch_listeners.manager import on_connection_stop_listener_manager
from nch_listeners.manager import on_connection_closing_listener_manager
from nch_listeners.manager import on_connection_crashed_listener_manager
from nch_listeners.manager import on_packet_start_listener_manager
from nch_listeners.manager import on_packet_end_listener_manager
from nch_listeners.manager import on_file_requested_listener_manager
from nch_listeners.manager import on_file_received_listener_manager
from nch_listeners.manager import on_file_denied_listener_manager
from nch_listeners.manager import on_file_sent_listener_manager
from nch_listeners.manager import on_change_splitscreen_user_listener_manager


# =============================================================================
# >> CLASSES
# =============================================================================
class OnConnectionStart(ListenerManagerDecorator):
    """Register/unregister a ConnectionStart listener."""

    manager = on_connection_start_listener_manager


class OnConnectionStop(ListenerManagerDecorator):
    """Register/unregister a ConnectionStop listener."""

    manager = on_connection_stop_listener_manager


class OnConnectionClosing(ListenerManagerDecorator):
    """Register/unregister a ConnectionClosing listener."""

    manager = on_connection_closing_listener_manager


class OnConnectionCrashed(ListenerManagerDecorator):
    """Register/unregister a ConnectionCrashed listener."""

    manager = on_connection_crashed_listener_manager


class OnPacketStart(ListenerManagerDecorator):
    """Register/unregister a PacketStart listener."""

    manager = on_packet_start_listener_manager


class OnPacketEnd(ListenerManagerDecorator):
    """Register/unregister a PacketEnd listener."""

    manager = on_packet_end_listener_manager


class OnFileRequested(ListenerManagerDecorator):
    """Register/unregister a FileRequested listener."""

    manager = on_file_requested_listener_manager


class OnFileReceived(ListenerManagerDecorator):
    """Register/unregister a FileReceived listener."""

    manager = on_file_received_listener_manager


class OnFileDenied(ListenerManagerDecorator):
    """Register/unregister a FileDenied listener."""

    manager = on_file_denied_listener_manager


class OnFileSent(ListenerManagerDecorator):
    """Register/unregister a FileSent listener."""

    manager = on_file_sent_listener_manager


class OnChangeSplitscreenUser(ListenerManagerDecorator):
    """Register/unregister a ChangeSplitscreenUser listener."""

    manager = on_change_splitscreen_user_listener_manager

