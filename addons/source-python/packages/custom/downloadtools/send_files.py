# ../send_files.py

"""Provides file sending functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Ctypes
import ctypes
#   Pathlib
import pathlib
#   Weakref
from weakref import WeakValueDictionary

# Source.Python Imports
#   Engines
from engines.server import server
#   Listeners
from listeners import OnClientDisconnect
from listeners.tick import Delay
#   Paths
from paths import GAME_PATH
#   Player
from players.entity import Player

# Download Tools Imports
#   Download Tools
from downloadtools import compress_file
from downloadtools import net_chan_is_file_in_waiting_list
from downloadtools import net_compresspackets
from downloadtools import sv_allowupload
from downloadtools import transfer_id


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("SendFiles",
           )


# =============================================================================
# >> CLASSES
# =============================================================================
class SendFiles:
    _send_files = WeakValueDictionary()

    def __init__(self, index, files, callback, time_multiplier=1.5, size=0):
        """Initialize the send_files.

        :param int index:
            Index of the receiver.
        :param tuple files:
            The files to be sent.
        :param callback:
            A callable object to be called after all transfers are complete.
        :param float time_multiplier:
            The multiplier for the wait time to stop the downloader.
        :param int size:
            Total compressed file size to skip compression.
        """

        global transfer_id

        self.index = index
        self.files = files
        self.callback = callback
        self.size = size

        self.file = self.files[-1].encode("utf-8")

        if not self.size:
            compress = net_compresspackets.get_bool()
            for file in files:
                path = pathlib.Path(GAME_PATH / file)
                self.size += compress_file(path) if compress else path.stat().st_size

        self.estimated_time = (self.size/256)*server.tick_interval
        self.transfer_time = self.estimated_time
        self.time_limit = self.estimated_time*time_multiplier

        net_channel = Player(index).client.net_channel
        for file in self.files:
            if not net_channel.send_file(file, transfer_id):
                self.delay = Delay(0.1, self.transfer_error, cancel_on_level_end=True)
                break
            transfer_id += 1
        else:
            self.net_channel = ctypes.c_void_p(net_channel._ptr().address)
            self.delay = Delay(self.estimated_time, self.transfer_end, cancel_on_level_end=True)

        self._send_files[id(self)] = self

    def transfer_error(self):
        self.delay = None
        self.callback(self, False)

    def transfer_end(self):
        sv_allowupload.update_index(self.index)
        self.check_files()

    def check_files(self):
        self.delay = None

        if not net_chan_is_file_in_waiting_list(
            self.net_channel, self.file):
            if self.index not in sv_allowupload:
                return self.callback(self, True)
            else:
                return self.callback(self, False)

        if self.transfer_time >= self.time_limit:
            return self.callback(self, False)

        self.transfer_time += 1
        self.delay = Delay(1, self.check_files, cancel_on_level_end=True)

    @OnClientDisconnect
    def on_client_disconnect(index):
        for send_files in SendFiles._send_files.values():
            if (send_files.index == index and
                send_files.delay is not None):
                if send_files.delay.running:
                    send_files.delay.cancel()
                send_files.delay = None

