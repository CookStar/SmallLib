# ../addons/source-python/packages/custom/cvartools/cvar_warning.py

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
from messages import SayText2
#   Players
from players.entity import Player

# Cvar Tools Imports
from cvartools.cvar_checker import CvarChecker
from cvartools.cvar_query import CvarQuery
from cvartools.translations import cvartools_strings


# =============================================================================
# >> CLASSES
# =============================================================================
class CvarWarning(CvarChecker, AutoUnload):
    _warnings = dict()
    _events = defaultdict(lambda: defaultdict(int))

    events = {"player_death"}
    state = False

    def __init__(self, cvar_name, cvar_value, kick=0):
        for cvar_warning in self._warnings.values():
            if (cvar_warning.cvar_name == cvar_name and
                cvar_warning.cvar_value != cvar_value):
                raise ValueError("Warning already exists.")

        super().__init__(cvar_name, cvar_value)

        self.kick = kick
        self.warned = defaultdict(int)

        for event in self.events:
            if self.game_event not in event_manager[event]:
                event_manager.register_for_event(event, self.game_event)

        self.state = True

        self._warnings[id(self)] = self

    def warn(self, index, cvar_name, cvar_value, event_name):
        self.add(index)

        event = self._events[event_name]
        event[index] -= 1

        if event[index] == 0:
            cvars = ""
            kick = False
            remains = 0
            for cvar_warning in self._warnings.values():
                if index not in cvar_warning:
                    continue

                if cvar_warning.kick:
                    warned = cvar_warning.warned
                    remain = cvar_warning.kick - warned[index]
                    if remain == 0:
                        kick = True
                    else:
                        if remains == 0 or remains > remain:
                            remains = remain
                    warned[index] += 1

                if cvar_warning.cvar_name not in cvars:
                    cvars += (cvar_warning.cvar_name
                              + " "
                              + str(cvar_warning.cvar_value)
                              + ";")

            if kick:
                player = Player(index)
                message = cvartools_strings["kick"].get_string(
                    player.language,
                    cvars=cvars,
                )
                player.kick(message)
                return

            SayText2(cvartools_strings["warning"], chat=True, color="​").send(
                index,
                tag=cvartools_strings["tag"],
                cvars=cvars,
                until=cvartools_strings["until"].tokenized(remains=remains) if remains else "",
            )

    def _unload_instance(self):
        del self._warnings[id(self)]

        if not self._warnings:
            self.disable()

        super()._unload_instance()

    @classmethod
    def enable(cls):
        for event in cls.events:
            if cls.game_event not in event_manager[event]:
                event_manager.register_for_event(event, cls.game_event)

        for warning in cls._warnings.values():
            warning.restore()

        cls.state = True

    @classmethod
    def disable(cls):
        cls._events.clear()

        for event in cls.events:
            if cls.game_event in event_manager[event]:
                event_manager.unregister_for_event(event, cls.game_event)

        for warning in cls._warnings.values():
            warning.warned.clear()

        cls.state = False

    @classmethod
    def add_event(cls, event_name):
        events.add(event_name)

        if cls.state and cls.game_event not in event_manager[event_name]:
            event_manager.register_for_event(event_name, cls.game_event)

    @classmethod
    def remove_event(cls, event_name):
        events.discard(event_name)

        if not cls.state and cls.game_event in event_manager[event_name]:
            event_manager.unregister_for_event(event_name, cls.game_event)

    @staticmethod
    def game_event(game_event):
        event_name = game_event.name
        if event_name not in CvarWarning.events:
            return

        try:
            player = Player.from_userid(game_event["userid"])
            event = CvarWarning._events[event_name]
            event[player.index] = 0
        except KeyError:
            player = None
            event = CvarWarning._events[event_name]
            event.clear()

        if player is not None:
            index = player.index
            for cvar_warning in CvarWarning._warnings.values():
                if index in cvar_warning:
                    CvarQuery(
                        player.edict,
                        cvar_warning.warn,
                        cvar_warning.cvar_name,
                        cvar_warning.cvar_value,
                        event_name=event_name,
                    )
                    event[index] += 1
                    cvar_warning.discard(index)

        else:
            for cvar_warning in CvarWarning._warnings.values():
                for index in cvar_warning:
                    CvarQuery(
                        edict_from_index(index),
                        cvar_warning.warn,
                        cvar_warning.cvar_name,
                        cvar_warning.cvar_value,
                        event_name=event_name,
                    )
                    event[index] += 1
                cvar_warning.clear()

    @OnClientDisconnect
    def on_client_disconnect(index):
        for cvar_warning in CvarWarning._warnings.values():
            cvar_warning.warned.pop(index, None)
        for event in CvarWarning._events.values():
            event.pop(index, None)

