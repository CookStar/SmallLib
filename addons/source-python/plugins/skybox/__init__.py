# ../addons/source-python/plugins/skybox/__init__.py

"""Provides skybox based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import AutoUnload
#   Cvars
from cvars import ConVar
from cvars import cvar
#   Events
from events import Event
from events.manager import event_manager
#   Listeners
from listeners import OnConVarChanged
from listeners import OnLevelEnd
from listeners import OnLevelInit
from listeners import OnServerActivate
#   Stringtables
from stringtables.downloads import Downloadables


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("SkyBox",
           "nextskybox",
           )


# =============================================================================
# >> CONVARS
# =============================================================================
nextskybox = ConVar("nextskybox", "", "Force the skybox on the next map.")


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
current_skyname = None

downloadables = Downloadables()

sv_skyname = cvar.find_var("sv_skyname")


# =============================================================================
# >> CALLBACKS
# =============================================================================
@Event("server_spawn")
def on_server_spawn(game_event):
    set_skyname()

@OnLevelInit
def on_level_init(map_name):
    set_skyname()

@OnServerActivate
def on_server_activate(edicts, edict_count, max_clients):
    set_skyname()

@OnLevelEnd
def on_level_end():
    global current_skyname
    current_skyname = None

    downloadables.clear()

@OnConVarChanged
def on_convar_changed(convar, old_value):
    if convar.name != "sv_skyname":
        return

    if current_skyname is None:
        return

    if old_value == current_skyname:
        convar.set_string(current_skyname)


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def set_skyname():
    global current_skyname

    skyname = nextskybox.get_string()
    if not skyname:
        return

    current_skyname = skyname

    sv_skyname.set_string(skyname)
    add_skybox(skyname)

def add_skybox(skyname):
    for position in ("bk", "dn", "ft", "lf", "rt", "up"):
        for material in ("vmt", "vtf"):
            downloadables.add(f"materials/skybox/{skyname}{position}.{material}")


# =============================================================================
# >> CLASSES
# =============================================================================
class SkyBox(AutoUnload):
    skyname = None

    def __init__(self, skyname):
        if self.skyname is not None:
            raise RuntimeError("The skybox is already setup.")

        self.change_skybox(skyname)
        event_manager.register_for_event("server_spawn", self.on_server_spawn)

    def change_skybox(self, skyname):
        nextskybox.set_string(skyname)
        set_skyname()

        SkyBox.skyname = skyname

    @staticmethod
    def on_server_spawn(game_event):
        nextskybox.set_string(SkyBox.skyname)
        set_skyname()

    def _unload_instance(self):
        SkyBox.skyname = None
        nextskybox.set_string("")
        event_manager.unregister_for_event("server_spawn", self.on_server_spawn)

