# ../addons/source-python/packages/custom/csbots/utl.py

"""Provides Counter-Strike bot utl based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Entities
from entities.entity import Entity
#   Filters
from filters.players import PlayerIter
from filters.weapons import WeaponClassIter
#   Weapons
from weapons.instance import WeaponClass
from weapons.entity import Weapon
from weapons.manager import weapon_manager

# CSBots Imports
#   Entity
#from csbots.entity import Bot


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('is_name_taken',
           'get_weapon_class',
           'weapon_class_table',
           )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
weapon_class_table = {
    weapon_class.id: weapon_class
    for weapon_class in WeaponClassIter()
}


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def is_name_taken(name, ignore_humans=False):
    for player in PlayerIter():
        if ignore_humans and not player.is_bot():
            continue

        if player.name == name:
            return True

        try:
            bot = Bot(player.index)
            if bot.profile.name == name:
                return True
        except ValueError:
            continue

    return False

def get_weapon_class(weapon):
    if isinstance(weapon, str):
        return weapon_manager[weapon]
    elif isinstance(weapon, Entity):
        if weapon.is_weapon():
            return weapon_manager[Weapon(weapon.index).weapon_name]
    elif isinstance(weapon, WeaponClass):
        return weapon
    elif isinstance(weapon, int):
        return weapon_class_table[weapon]

    raise ValueError('Unable to find weapon.')

