# ../addons/source-python/packages/custom/downloadtools/downloader.py

"""Provides downloader functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Ctypes
import ctypes
#   Pathlib
from pathlib import Path
#   Weakref
from weakref import WeakValueDictionary

# Source.Python Imports
#   Engines
from engines.server import server
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners import OnClientDisconnect
from listeners.tick import Delay
#   Paths
from paths import GAME_PATH

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
__all__ = ("Downloader",
           )


# =============================================================================
# >> CLASSES
# =============================================================================
class Downloader:
    _downloader = WeakValueDictionary()

    def __init__(self, files, callback, downloadables=None, time_multiplier=1.5, size=0):
        """Initialize the downloader.

        :param tuple files:
            The files to be sent.
        :param callback:
            A callable object to be called after all transfers are complete.
        :param Downloadables downloadables:
            The downloadables to allow new players to download files.
        :param float time_multiplier:
            The multiplier for the wait time to stop the downloader.
        :param int size:
            Total compressed file size to skip compression.
        """

        global transfer_id

        self.files = files
        self.callback = callback
        self.downloadables = downloadables
        self.size = size

        self.file = self.files[-1].encode("utf-8")

        if self.size:
            if self.downloadables is not None:
                for file in files:
                    self.downloadables.add(file)
        else:
            compress = net_compresspackets.get_bool()
            for file in files:
                path = Path(GAME_PATH / file)
                self.size += compress_file(path) if compress else path.stat().st_size
                if self.downloadables is not None:
                    self.downloadables.add(file)

        self.estimated_time  = (self.size/256)*server.tick_interval
        self.transfer_time = self.estimated_time
        self.time_limit = self.estimated_time*time_multiplier

        self.success = list()
        self.failed = list()
        self.receivers = dict()

        for slot in range(server.client_count):
            client = server.get_client(slot)
            if not client.is_connected or client.is_fake_client:
                continue
            index = slot + 1
            net_channel = client.net_channel

            for file in self.files:
                if not net_channel.send_file(file, transfer_id):
                    self.failed.append(index)
                    break
                transfer_id += 1
            else:
                self.receivers[index] = (client.userid, ctypes.c_void_p(net_channel._ptr().address))

        self.delay = Delay(self.estimated_time - 1, self.transfer_end, cancel_on_level_end=True)

        self._downloader[id(self)] = self

    def transfer_end(self):
        sv_allowupload.update()
        self.delay = Delay(1, self.check_files, cancel_on_level_end=True)

    def check_files(self):
        self.delay = None

        if self.transfer_time < self.time_limit:
            for index, value in list(self.receivers.items()):
                userid, net_channel = value
                client = server.get_client(index - 1)
                if not client.is_connected or client.userid != userid:
                    del self.receivers[index]
                    continue

                if not net_chan_is_file_in_waiting_list(net_channel, self.file):
                    if index not in sv_allowupload:
                        self.success.append(index)
                    else:
                        self.failed.append(index)
                    del self.receivers[index]
                else:
                    break
            else:
                return self.callback(self, self.success, self.failed)

        else:
            for index, value in self.receivers.items():
                userid, net_channel = value
                client = server.get_client(index - 1)
                if not client.is_connected or client.userid != userid:
                    continue
                if (not net_chan_is_file_in_waiting_list(net_channel, self.file) and
                    index not in sv_allowupload):
                    self.success.append(index)
                else:
                    self.failed.append(index)
            self.receivers.clear()
            return self.callback(self, self.success, self.failed)

        self.transfer_time += 1
        self.delay = Delay(1, self.check_files, cancel_on_level_end=True)

    @OnClientDisconnect
    def on_client_disconnect(index):
        for downloader in Downloader._downloader.values():
            receivers = downloader.receivers
            if receivers and receivers.pop(index, None) is None:
                if index in downloader.success:
                    downloader.success.remove(index)
                elif index in downloader.failed:
                    downloader.failed.remove(index)

