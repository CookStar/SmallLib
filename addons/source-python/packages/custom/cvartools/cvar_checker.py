# ../addons/source-python/packages/custom/cvartools/cvar_checker.py

"""Provides Cvar Checking functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Weakref
from weakref import WeakValueDictionary

# Source.Python Imports
#   Core
from core import WeakAutoUnload
#   Entities
from entities.helpers import edict_from_index
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners import OnClientDisconnect
from listeners import OnClientPutInServer

# Cvar Tools Imports
from cvartools.cvar_query import CvarQuery


# =============================================================================
# >> CLASSES
# =============================================================================
class CvarChecker(WeakAutoUnload, set):
    _cvars = WeakValueDictionary()

    def __init__(self, cvar_name, cvar_value):
        super().__init__()

        self.cvar_name = cvar_name
        self.cvar_value = cvar_value

        self._cvars[id(self)] = self

        for player in PlayerIter("human"):
            CvarQuery(
                player.edict,
                self.store,
                self.cvar_name,
                self.cvar_value,
            )

    def store(self, index, cvar_name, cvar_value):
        self.add(index)

    def update(self):
        for index in self:
            CvarQuery(
                edict_from_index(index),
                self.store,
                self.cvar_name,
                self.cvar_value,
            )
        self.clear()

    def update_index(self, index):
        if index in self:
            CvarQuery(
                edict_from_index(index),
                self.store,
                self.cvar_name,
                self.cvar_value,
            )
            self.remove(index)

    def restore(self):
        for player in PlayerIter("human"):
            CvarQuery(
                player.edict,
                self.store,
                self.cvar_name,
                self.cvar_value,
            )
        self.clear()

    def _unload_instance(self):
        del self._cvars[id(self)]

    @OnClientPutInServer
    def on_client_put_in_server(edict, name):
        for cvar in CvarChecker._cvars.values():
            CvarQuery(
                edict,
                cvar.store,
                cvar.cvar_name,
                cvar.cvar_value,
            )

    @OnClientDisconnect
    def on_client_disconnect(index):
        for cvar in CvarChecker._cvars.values():
            cvar.discard(index)

