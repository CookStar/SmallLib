# ../cvar_warning.py

"""Provides Cvar Warning functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections import defaultdict

# Source.Python Imports
#   Core
from core import AutoUnload
#   Entities
from entities.helpers import edict_from_index
#   Events
from events.manager import event_manager
#   Listeners
from listeners import OnClientDisconnect
#   Messages
from messages import HudDestination
from messages import SayText2
from messages import TextMsg
#   Players
from players.entity import Player

# Cvar Tools Imports
#   Cvar Checker
from .cvar_checker import CvarChecker
#   Cvar Query
from .cvar_query import CvarQuery
#   Translations
from .translations import cvartools_strings


# =============================================================================
# >> CLASSES
# =============================================================================
class CvarWarning(CvarChecker, AutoUnload):
    _warnings = dict()
    _events = defaultdict(lambda: defaultdict(int))

    def __init__(self, cvar_name, cvar_value, *events, kick=0):
        for cvar_warning in self._warnings.values():
            if (cvar_warning.cvar_name == cvar_name and
                cvar_warning.cvar_value != cvar_value):
                raise ValueError("Warning already exists.")

        super().__init__(cvar_name, cvar_value)

        if events:
            self.events = set(events)
        else:
            self.events = {"player_death"}

        self.kick = kick
        self.warned = defaultdict(int)

        unregistered_events = set(self.events)
        for cvar_warning in self._warnings.values():
            unregistered_events -= cvar_warning.events
        for event_name in unregistered_events:
            event_manager.register_for_event(event_name, self.game_event)

        self._warnings[id(self)] = self

    def warn(self, index, cvar_name, cvar_value, event_name):
        self.add(index)

        events = self._events[event_name]
        events[index] -= 1

        if events[index] == 0:
            cvars = ""
            kick = False
            remains = 0
            for cvar_warning in self._warnings.values():
                if cvar_warning.kick:
                    warned = cvar_warning.warned
                    remain = cvar_warning.kick - warned[index]
                    if remain == 0:
                        kick = True
                    else:
                        if remains:
                            remains = remain if remain < remains else remains
                        else:
                            remains = remain
                    warned[index] += 1
                cvars += (cvar_warning.cvar_name
                          + " "
                          + str(cvar_warning.cvar_value)
                          + ";")

            if kick:
                player = Player(index)
                message = cvartools_strings["kick"].get_string(
                    player.language,
                    tag=cvartools_strings["tag"],
                    cvars=cvars,
                )
                player.kick(message)
                return

            SayText2(cvartools_strings["warning"]).send(
                index,
                tag=cvartools_strings["tag"],
                cvars=cvars,
                remains=remains,
            )
            TextMsg(cvartools_strings["warning"], HudDestination.CONSOLE).send(
                index,
                tag=cvartools_strings["tag"],
                cvars=cvars,
                remains=remains,
            )

    def _unload_instance(self):
        del self._warnings[id(self)]

        registered_events = set()
        for cvar_warning in self._warnings.values():
            registered_events = registered_events | cvar_warning.events
        for event_name in self.events-registered_events:
            event_manager.unregister_for_event(event_name, self.game_event)
            self._events.pop(event_name, None)

        super()._unload_instance()

    @staticmethod
    def game_event(game_event):
        try:
            player = Player.from_userid(game_event["userid"])
        except KeyError:
            player = None

        if player is not None:
            CvarWarning._events[game_event.name][player.index] = 0
        else:
            CvarWarning._events.pop(game_event.name, None)

        for cvar_warning in CvarWarning._warnings.values():
            if not game_event.name in cvar_warning.events:
                continue

            if player is not None:
                if player.index in cvar_warning:
                    CvarQuery(
                        player.edict,
                        cvar_warning.warn,
                        cvar_warning.cvar_name,
                        cvar_warning.cvar_value,
                        event_name=game_event.name,
                    )
                    CvarWarning._events[game_event.name][player.index] += 1
                    cvar_warning.discard(player.index)
                    continue

            else:
                for index in cvar_warning:
                    CvarQuery(
                        edict_from_index(index),
                        cvar_warning.warn,
                        cvar_warning.cvar_name,
                        cvar_warning.cvar_value,
                        event_name=game_event.name,
                    )
                    CvarWarning._events[game_event.name][index] += 1
                cvar_warning.clear()

    @OnClientDisconnect
    def on_client_disconnect(index):
        for cvar_warning in CvarWarning._warnings.values():
            cvar_warning.warned.pop(index, None)
        for events in CvarWarning._events.values():
            events.pop(index, None)
