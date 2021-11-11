# ../addons/source-python/packages/custom/cvartools/cvar_query.py

"""Provides Cvar Querying functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import WeakAutoUnload
#   Engines
from engines.server import QueryCvarStatus
from engines.server import engine_server
#   Listeners
from listeners import OnQueryCvarValueFinished


# =============================================================================
# >> CLASSES
# =============================================================================
class CvarQuery(WeakAutoUnload):
    _cvar_queries = {}

    def __init__(self, edict, callback, cvar_name, cvar_value=None, **kwargs):
        self.callback = callback
        self.cvar_value = cvar_value
        self.kwargs = kwargs

        self.cookie = engine_server.start_query_cvar_value(edict, cvar_name)
        if self.cookie < 0:
            raise ValueError("Invalid entity.")

        self._cvar_queries[self.cookie] = self

    def _unload_instance(self):
        self._cvar_queries.pop(self.cookie, None)

    @OnQueryCvarValueFinished
    def on_query_cvar_value_finished(
        cookie, index, status, cvar_name, cvar_value):
        if cookie not in CvarQuery._cvar_queries:
            return

        cvar_query = CvarQuery._cvar_queries.pop(cookie)

        if status is not QueryCvarStatus.SUCCESS:
            return

        if (cvar_query.cvar_value is not None and
            cvar_value == str(cvar_query.cvar_value)):
            return

        if cvar_query.kwargs:
            cvar_query.callback(
                index, cvar_name, cvar_value, **cvar_query.kwargs)
        else:
            cvar_query.callback(
                index, cvar_name, cvar_value)

