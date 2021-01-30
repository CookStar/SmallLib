# ../addons/source-python/packages/custom/nch_listeners/manager.py

"""Provides Net Channel Handler listeners."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import SOURCE_ENGINE
#   Engines
from engines.server import server
#   Entities
from entities.helpers import index_from_edict
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners import on_client_connect_listener_manager
from listeners import ListenerManager
#   Memory
from memory import get_virtual_function
from memory import make_object
#   Net Channel
from net_channel import NetChannelHandler
#   Players
from players import Client


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_has_replay_demo_file = bool(SOURCE_ENGINE in ("blade", "csgo", "l4d2"))


# =============================================================================
# >> CLASSES
# =============================================================================
class NetChannelHandlerListenerManager(ListenerManager):
    """Register/unregister an NetChannelHandler listener."""

    def __init__(self):
        self.function = None
        super().__init__()

    def initialize(self):
        """Called when the first callback is being registered."""
        for player in PlayerIter("human"):
            net_channel_handler = make_object(NetChannelHandler, player.client.net_channel.msg_handler)
            self.function = get_virtual_function(net_channel_handler, self.function_info)
            self.function.add_pre_hook(self.notifyer)
            break
        else:
            if self.on_client_connect not in on_client_connect_listener_manager:
                on_client_connect_listener_manager.register_listener(self.on_client_connect)

    def finalize(self):
        """Called when the last callback is being unregistered."""
        if self.function is None:
            return

        self.function.remove_pre_hook(self.notifyer)

    def on_client_connect(self, allow_connect_ptr, edict, name, address, reject_msg_ptr, reject_msg_len):
        """Hook the notifyer."""
        on_client_connect_listener_manager.unregister_listener(self.on_client_connect)

        if len(self) == 0:
            return

        client = server.get_client(index_from_edict(edict) - 1)
        net_channel_handler = make_object(NetChannelHandler, client.net_channel.msg_handler)
        self.function = get_virtual_function(net_channel_handler, self.function_info)
        self.function.add_pre_hook(self.notifyer)

    @property
    def function_info(self):
        """Return the name of the member function on the C++ side."""
        raise NotImplementedError("No function_info defined for class.")

    @staticmethod
    def notifyer(args):
        """Return a :class:`function` object."""
        raise NotImplementedError("No notifyer defined for class.")


class OnConnectionStartListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a ConnectionStart listener."""

    function_info = "ConnectionStart"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        net_channel = args[1]

        on_connection_start_listener_manager.notify(client, net_channel)

        return 0

on_connection_start_listener_manager = OnConnectionStartListenerManager()


class OnConnectionStopListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a ConnectionStop listener."""

    function_info = "ConnectionStop"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])

        on_connection_stop_listener_manager.notify(client)

        return 0

on_connection_stop_listener_manager = OnConnectionStopListenerManager()


class OnConnectionClosingListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a ConnectionClosing listener."""

    function_info = "ConnectionClosing"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        reason = args[1]

        on_connection_closing_listener_manager.notify(client, reason)

        return 0

on_connection_closing_listener_manager = OnConnectionClosingListenerManager()


class OnConnectionCrashedListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a ConnectionCrashed listener."""

    function_info = "ConnectionCrashed"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        reason = args[1]

        on_connection_crashed_listener_manager.notify(client, reason)

        return 0

on_connection_crashed_listener_manager = OnConnectionCrashedListenerManager()


class OnPacketStartListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a PacketStart listener."""

    function_info = "PacketStart"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        incoming_sequence = args[1]
        outgoing_acknowledged = args[2]

        on_packet_start_listener_manager.notify(client, incoming_sequence, outgoing_acknowledged)

        return 0

on_packet_start_listener_manager = OnPacketStartListenerManager()


class OnPacketEndListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a PacketEnd listener."""

    function_info = "PacketEnd"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])

        on_packet_end_listener_manager.notify(client)

        return 0

on_packet_end_listener_manager = OnPacketEndListenerManager()


class OnFileRequestedListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a FileRequested listener."""

    function_info = "FileRequested"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if _has_replay_demo_file:
            is_replay_demo_file = args[3]

            on_file_requested_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_requested_listener_manager.notify(client, file_name, transfer_id)

        return 0

on_file_requested_listener_manager = OnFileRequestedListenerManager()


class OnFileReceivedListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a FileReceived listener."""

    function_info = "FileReceived"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if _has_replay_demo_file:
            is_replay_demo_file = args[3]

            on_file_received_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_received_listener_manager.notify(client, file_name, transfer_id)

        return 0

on_file_received_listener_manager = OnFileReceivedListenerManager()


class OnFileDeniedListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a FileDenied listener."""

    function_info = "FileDenied"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if _has_replay_demo_file:
            is_replay_demo_file = args[3]

            on_file_denied_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_denied_listener_manager.notify(client, file_name, transfer_id)

        return 0

on_file_denied_listener_manager = OnFileDeniedListenerManager()


class OnFileSentListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a FileSent listener."""

    function_info = "FileSent"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if _has_replay_demo_file:
            is_replay_demo_file = args[3]

            on_file_sent_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_sent_listener_manager.notify(client, file_name, transfer_id)

        return 0

on_file_sent_listener_manager = OnFileSentListenerManager()


class OnChangeSplitscreenUserListenerManager(NetChannelHandlerListenerManager):
    """Register/unregister a ChangeSplitscreenUser listener."""

    function_info = "ChangeSplitscreenUser"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        split_screen_user_slot = args[1]

        on_change_splitscreen_user_listener_manager.notify(client, split_screen_user_slot)

        return 0

on_change_splitscreen_user_listener_manager = OnChangeSplitscreenUserListenerManager()

