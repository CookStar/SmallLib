# ../addons/source-python/packages/custom/botstools/__init__.py

"""Provides bot based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
from ctypes import c_void_p
from ctypes import memset

# Source.Python Imports
#   Entities
from entities.entity import Entity
#   Memory
from memory import alloc
from memory import get_object_pointer
from memory import get_size
from memory.manager import manager
#   Paths
from paths import CUSTOM_DATA_PATH
#   Weapons
from weapons.instance import WeaponClass
from weapons.manager import weapon_manager

# Memory Tools Imports
#   Memory Tools
from memorytools import get_bytes
from memorytools import set_bytes

# Bots Tools Imports
#   Bots Tools
from botstools.constants import BotDifficulty


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('BotProfile',
           )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
BotProfile = manager.create_type_from_file('BotProfile',
    CUSTOM_DATA_PATH / 'botstools' / 'bot_profile' / 'BotProfile.ini')


# =============================================================================
# >> BOTPROFILE
# =============================================================================
def _constructor(self, name):
    memset(c_void_p(get_object_pointer(self).address), 0, get_size(self))

    self.name = name

    self.aggression = 0.5
    self.skill = 0.5
    self.teamwork = 0.75

    self.aim_focus_initial = 20
    self.aim_focus_decay = 0.7
    self.aim_focus_offset_scale = 0.30
    self.aim_focus_interval = 0.8

    self.difficulty = BotDifficulty.NORMAL

    self.voice_pitch = 100

    self.reaction_time = 0.3

    self.look_angle_max_accel_normal = 2000.0
    self.look_angle_stiffness_normal = 100.0
    self.look_angle_damping_normal = 25.0

    self.look_angle_max_accel_attacking = 3000.0
    self.look_angle_stiffness_attacking = 150.0
    self.look_angle_damping_attacking = 30.0

BotProfile._constructor = _constructor

def _destructor(self):
    self.get_pointer().dealloc()

BotProfile._destructor = _destructor

def get_name(self):
    return self.base_name

def set_name(self, name):
    self.get_pointer().dealloc()

    if name is not None:
        size = len(name.encode("utf-8"))+1
        base = alloc(size, False)
        base.set_string_array(name)
        self.set_pointer(base)
    else:
        self.base_name = None

BotProfile.name = property(get_name, set_name)

def get_weapon_preference(self, index):
    weapon_preference = self.weapon_preference[index]

    for weapon_class in weapon_manager.values():
        if weapon_preference == weapon_class.item_definition_index:
            return weapon_class.name

    return None

BotProfile.get_weapon_preference = get_weapon_preference

def set_weapon_preference(self, index, weapon):
    if isinstance(weapon, str):
        weapon_class = weapon_manager[weapon]
    elif isinstance(weapon, Entity):
        weapon_class = weapon_manager[weapon.classname]
    elif isinstance(weapon, WeaponClass):
        weapon_class = weapon
    else:
        raise ValueError('Unable to find weapon.')

    self.weapon_preference[index] = weapon_class.item_definition_index

BotProfile.set_weapon_preference = set_weapon_preference

def push_weapon_preference(self, weapon):
    if isinstance(weapon, str):
        weapon_class = weapon_manager[weapon]
    elif isinstance(weapon, Entity):
        weapon_class = weapon_manager[weapon.classname]
    elif isinstance(weapon, WeaponClass):
        weapon_class = weapon
    else:
        raise ValueError('Unable to find weapon.')

    count = self.weapon_preference_count
    self.weapon_preference[count] = weapon_class.item_definition_index
    self.weapon_preference_count += 1

BotProfile.push_weapon_preference = push_weapon_preference

def pop_weapon_preference(self):
    count = self.weapon_preference_count
    weapon = get_weapon_preference(count)
    self.weapon_preference[count] = 0
    self.weapon_preference_count -= 1
    return weapon

BotProfile.pop_weapon_preference = pop_weapon_preference

def reset_weapon_preference(self):
    for i in range(self.weapon_preference._length):
        self.weapon_preference[i] = 0

    self.weapon_preference_count = 0

BotProfile.reset_weapon_preference = reset_weapon_preference

def clone(self, bot_profile):
    name = bot_profile.name
    if name is not None:
        self.name = name
    data = get_bytes(get_object_pointer(bot_profile), 0x7C, 0x4)
    set_bytes(get_object_pointer(self), data, 0x4)

BotProfile.clone = clone

def copy(self):
    bot_profile = BotProfile(None)
    bot_profile.clone(self)
    return bot_profile

BotProfile.copy = copy

