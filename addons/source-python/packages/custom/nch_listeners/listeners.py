# ../listeners.py

"""Provides Net Channel Handler listener based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections import defaultdict
#   Sys
import sys

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
from listeners import ListenerManager
from listeners import ListenerManagerDecorator
from listeners import OnClientConnect
#   Memory
from memory import get_virtual_function
from memory import make_object
from memory.hooks import HookType
#   Net Channel
from net_channel import NetChannelHandler
#   Players
from players import Client


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
on_connection_start_listener_manager = ListenerManager()
on_connection_stop_listener_manager = ListenerManager()
on_connection_closing_listener_manager = ListenerManager()
on_connection_crashed_listener_manager = ListenerManager()
on_packet_start_listener_manager = ListenerManager()
on_packet_end_listener_manager = ListenerManager()
on_file_requested_listener_manager = ListenerManager()
on_file_received_listener_manager = ListenerManager()
on_file_denied_listener_manager = ListenerManager()
on_file_sent_listener_manager = ListenerManager()
on_change_splitscreen_user_listener_manager = ListenerManager()


# =============================================================================
# >> CLASSES
# =============================================================================
class NetChannelHandlerLMD(ListenerManagerDecorator):
    """Derived decorator class used to register/unregister a listener."""

    _hooked = defaultdict(lambda: None)
    _callbacks = defaultdict(list)

    def __init__(self, callback):
        """Store the callback and hook the notifyer."""
        super().__init__(callback)

        self._callbacks[self.function_info].append(self.callback)

        if self._hooked[self.function_info] is None:
            for player in PlayerIter("human"):
                net_channel_handler = make_object(NetChannelHandler, player.client.net_channel.msg_handler)
                function = get_virtual_function(net_channel_handler, self.function_info)
                function.add_hook(HookType.PRE, self.notifyer)
                self._hooked[self.function_info] = function
                return

    @property
    def function_info(self):
        """Return the name of the member function on the C++ side."""
        raise NotImplementedError("No function_info defined for class.")

    @staticmethod
    def notifyer(args):
        """Return a :class:`function` object."""
        raise NotImplementedError("No notifyer defined for class.")

    def _unload_instance(self):
        """Unhook the notifyer."""
        callbacks = self._callbacks[self.function_info]
        callbacks.remove(self.callback)

        if not callbacks and self._hooked[self.function_info] is not None:
            function = self._hooked.pop(self.function_info)
            function.remove_hook(HookType.PRE, self.notifyer)

            del self._callbacks[self.function_info]

        super()._unload_instance()

    @OnClientConnect
    def on_client_connect(allow_connect_ptr, edict, name, address, reject_msg_ptr, reject_msg_len):
        """Hook the notifyer."""
        for function_info, function in NetChannelHandlerLMD._hooked.items():
            if function is None:
                client = server.get_client(index_from_edict(edict) - 1)
                net_channel_handler = make_object(NetChannelHandler, client.net_channel.msg_handler)
                function = get_virtual_function(net_channel_handler, function_info)
                notifyer = getattr(sys.modules[__name__], "On"+function_info).notifyer
                function.add_hook(HookType.PRE, notifyer)
                NetChannelHandlerLMD._hooked[function_info] = function


class OnConnectionStart(NetChannelHandlerLMD):
    """Register/unregister a ConnectionStart listener."""

    manager = on_connection_start_listener_manager

    function_info = "ConnectionStart"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        net_channel = args[1]

        on_connection_start_listener_manager.notify(client, net_channel)

        return 0


class OnConnectionStop(NetChannelHandlerLMD):
    """Register/unregister a ConnectionStop listener."""

    manager = on_connection_stop_listener_manager

    function_info = "ConnectionStop"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])

        on_connection_stop_listener_manager.notify(client)

        return 0


class OnConnectionClosing(NetChannelHandlerLMD):
    """Register/unregister a ConnectionClosing listener."""

    manager = on_connection_closing_listener_manager

    function_info = "ConnectionClosing"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        reason = args[1]

        on_connection_closing_listener_manager.notify(client, reason)

        return 0


class OnConnectionCrashed(NetChannelHandlerLMD):
    """Register/unregister a ConnectionCrashed listener."""

    manager = on_connection_crashed_listener_manager

    function_info = "ConnectionCrashed"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        reason = args[1]

        on_connection_crashed_listener_manager.notify(client, reason)

        return 0


class OnPacketStart(NetChannelHandlerLMD):
    """Register/unregister a PacketStart listener."""

    manager = on_packet_start_listener_manager

    function_info = "PacketStart"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        incoming_sequence = args[1]
        outgoing_acknowledged = args[2]

        on_packet_start_listener_manager.notify(client, incoming_sequence, outgoing_acknowledged)

        return 0


class OnPacketEnd(NetChannelHandlerLMD):
    """Register/unregister a PacketEnd listener."""

    manager = on_packet_end_listener_manager

    function_info = "PacketEnd"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])

        on_packet_end_listener_manager.notify(client)

        return 0


class OnFileRequested(NetChannelHandlerLMD):
    """Register/unregister a FileRequested listener."""

    manager = on_file_requested_listener_manager

    function_info = "FileRequested"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if SOURCE_ENGINE in ("blade", "csgo", "l4d2"):
            is_replay_demo_file = args[3]

            on_file_requested_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_requested_listener_manager.notify(client, file_name, transfer_id)

        return 0


class OnFileReceived(NetChannelHandlerLMD):
    """Register/unregister a FileReceived listener."""

    manager = on_file_received_listener_manager

    function_info = "FileReceived"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if SOURCE_ENGINE in ("blade", "csgo", "l4d2"):
            is_replay_demo_file = args[3]

            on_file_received_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_received_listener_manager.notify(client, file_name, transfer_id)

        return 0


class OnFileDenied(NetChannelHandlerLMD):
    """Register/unregister a FileDenied listener."""

    manager = on_file_denied_listener_manager

    function_info = "FileDenied"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if SOURCE_ENGINE in ("blade", "csgo", "l4d2"):
            is_replay_demo_file = args[3]

            on_file_denied_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_denied_listener_manager.notify(client, file_name, transfer_id)

        return 0


class OnFileSent(NetChannelHandlerLMD):
    """Register/unregister a FileSent listener."""

    manager = on_file_sent_listener_manager

    function_info = "FileSent"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        file_name = args[1]
        transfer_id = args[2]

        if SOURCE_ENGINE in ("blade", "csgo", "l4d2"):
            is_replay_demo_file = args[3]

            on_file_sent_listener_manager.notify(client, file_name, transfer_id, is_replay_demo_file)
        else:
            on_file_sent_listener_manager.notify(client, file_name, transfer_id)

        return 0


class OnChangeSplitscreenUser(NetChannelHandlerLMD):
    """Register/unregister a ChangeSplitscreenUser listener."""

    manager = on_change_splitscreen_user_listener_manager

    function_info = "ChangeSplitscreenUser"

    @staticmethod
    def notifyer(args):
        client = make_object(Client, args[0])
        split_screen_user_slot = args[1]

        on_change_splitscreen_user_listener_manager.notify(client, split_screen_user_slot)

        return 0

