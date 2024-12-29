# ../addons/source-python/packages/custom/csbots/profile.py

"""Provides bot profile based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Random
import random

# Source.Python Imports
#   Core
from core import GAME_NAME
#   Memory
from memory import get_object_pointer
from memory import get_size
from memory.helpers import Type
#   Players
from players.teams import teams_by_name
from players.teams import teams_by_number
#   Weapons
from weapons.constants import WeaponID
from weapons.constants import WeaponType

# Utl Imports
#   Linkedlist
from utl.linkedlist import UtlLinkedList
from utl.vector import UtlVector

# CSBots Imports
#   CSBots
from csbots import csbots_type_manager
#   Constants
from csbots.constants import BotDifficulty
from csbots.constants import Team
#   Paths
from csbots.paths import CSBOTS_DATA_PATH
from csbots.paths import CSBOTS_GP_DATA_PATH
#   Utl
from csbots.utl import is_name_taken
from csbots.utl import get_weapon_class
from csbots.utl import weapon_class_table


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('BotProfile',
           'BotProfileList',
           'BotProfileManager',
           'BotProfileTemplates',
           'VoiceBankList',
           'bot_profile_manager',
           )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================


# =============================================================================
# >> CLASSES
# =============================================================================


# =============================================================================
# >> BotProfile
# =============================================================================
_BotProfile = csbots_type_manager.create_type_from_file(
    '_BotProfile',
    CSBOTS_DATA_PATH / 'bot_profile' / 'BotProfile.ini',
)

class BotProfile(_BotProfile, metaclass=csbots_type_manager):

    def _constructor(self, name):
        self.name = name

        self.aggression = 0.5
        self.skill = 0.5
        self.teamwork = 0.75

        self._difficulty_flags = BotDifficulty.NORMAL

        self.voice_pitch = 100

        self.reaction_time = 0.3

        if GAME_NAME == 'csgo':
            self.aim_focus_initial = 20
            self.aim_focus_decay = 0.7
            self.aim_focus_offset_scale = 0.30
            self.aim_focus_interval = 0.8

            self.look_angle_max_accel_normal = 2000.0
            self.look_angle_stiffness_normal = 100.0
            self.look_angle_damping_normal = 25.0

            self.look_angle_max_accel_attacking = 3000.0
            self.look_angle_stiffness_attacking = 150.0
            self.look_angle_damping_attacking = 30.0

    def get_aggression(self):
        return self._aggression

    def set_aggression(self, value):
        if value > 1 or teamwork < 0:
            raise ValueError('Value must be in percentages.')

        self._aggression = value

    aggression = property(get_aggression, set_aggression)

    def get_skill(self):
        return self._skill

    def set_skill(self, value):
        if value > 1 or teamwork < 0:
            raise ValueError('Value must be in percentages.')

        self._skill = value

    skill = property(get_skill, set_skill)

    def get_teamwork(self):
        return self._teamwork

    def set_teamwork(self, value):
        if value > 1 or teamwork < 0:
            raise ValueError('Value must be in percentages.')

        self._teamwork = value

    teamwork = property(get_teamwork, set_teamwork)

    def get_difficulty_flags(self):
        return BotDifficulty(self._difficulty_flags)

    def set_difficulty_flags(self, flags):
        self._difficulty_flags = flags

    difficulty_flags = property(get_difficulty_flags, set_difficulty_flags)

    def get_max_difficulty(self):
        for bot_difficulty in reversed(BotDifficulty):
            if bot_difficulty in self._difficulty_flags:
                return bot_difficulty

        return BotDifficulty.EASY

    def set_max_difficulty(self, flag):
        self._difficulty_flags &= flag - 1
        self._difficulty_flags |= flag

    max_difficulty = property(get_max_difficulty, set_max_difficulty)

    def is_difficulty(self, difficulty):
        return bool(difficulty & self.difficulty_flags)

    def is_max_difficulty(self, difficulty):
        return difficulty == self.get_max_difficulty()

    def get_team(self):
        return Team(self._team)

    def set_team(self, team):
        self._team = team

    team = property(get_team, set_team)

    def get_team_name(self):
        return teams_by_number.get(self._team, 'Unknown')

    def set_team_name(self, team):
        team = teams_by_name.get(team, None)
        if team is None:
            raise ValueError('Invalid team name.')

        self._team = team

    team_name = property(get_team_name, set_team_name)

    def is_valid_team(self, team):
        if isinstance(team, str):
            team = teams_by_name.get(team, None)
            if team is None:
                raise ValueError('Invalid team name.')

        return (team == Team.UNASSIGNED or
                self.team == team or
                self.team == Team.UNASSIGNED)

    def get_voice_bank(self):
        for index, voice_bank in enumerate(bot_profile_manager.voice_banks):
            if self.voice_bank_index == index:
                return voice_bank

        return None

    def set_voice_bank(self, filename):
        next_voice_bank_index = 0
        for index, voice_bank in enumerate(bot_profile_manager.voice_banks):
            if voice_bank == filename:
                self.voice_bank_index = index
                return

            next_voice_bank_index += 1

        bot_profile_manager.find_voice_bank_index(filename)
        # bot_phrase_init(filename, next_voice_bank_index)
        self.voice_bank_index = next_voice_bank_index

    voice_bank = property(get_voice_bank, set_voice_bank)

    def has_primary_preference(self):
        for weapon_class in self.weapon_preference:
            if weapon_class is not None and 'primary' in weapon_class.tags:
                return True

        return False

    def has_secondary_preference(self):
        for weapon_class in self.weapon_preference:
            if weapon_class is not None and 'secondary' in weapon_class.tags:
                return True

        return False

    def inherits_from(self, name):
        if self.name == name:
            return True

        for template in self.templates:
            if self.template.inherits_from(name):
                return True

        return False

    def clone(self, bot_profile):
        size = get_size(self) - 0x14
        get_object_pointer(bot_profile).copy(self, size)

        self.name = bot_profile.name

    def copy(self, name=None):
        bot_profile = BotProfile(name)

        size = get_size(self) - 0x14
        get_object_pointer(bot_profile).copy(self, size)

        return bot_profile

    def get_info(self, times=0):
        tab = '    ' * times
        info = (
            f'{tab}Bot Profile "{self.name}":\n'
            f'{tab}    Name: {self.name}\n'
            f'{tab}    Aggression: {round(self.aggression, 5)}\n'
            f'{tab}    Skill: {round(self.skill, 5)}\n'
            f'{tab}    Teamwork: {round(self.teamwork, 5)}\n'
            f'{tab}    Cost: {self.cost}\n'
            f'{tab}    Skin: {self.skin}\n'
            f'{tab}    Difficulty Flags: {str(self.difficulty_flags)}\n'
            f'{tab}    Voice Pitch: {self.voice_pitch}\n'
            f'{tab}    Reaction Time: {round(self.reaction_time, 5)}\n'
            f'{tab}    Attack Delay: {round(self.attack_delay, 5)}\n'
            f'{tab}    Team: {str(self.team)}\n'
            f'{tab}    Prefers Silencer: {self.prefers_silencer}\n'
            f'{tab}    Voice Bank Index: {self.voice_bank_index}\n'
            f'{tab}    Voice Bank: {self.voice_bank}\n'
        )

        info += '\n'

        if GAME_NAME == 'csgo':
            info += (
                f'{tab}    Aim Focus Initial: {round(self.aim_focus_initial, 5)}\n'
                f'{tab}    Aim Focus Decay: {round(self.aim_focus_decay, 5)}\n'
                f'{tab}    Aim Focus Offset Scale: {round(self.aim_focus_offset_scale, 5)}\n'
                f'{tab}    Aim focus Interval: {round(self.aim_focus_interval, 5)}\n'
            )
            
            info += '\n'

            info += (
                f'{tab}    Look Angle Max Accel Normal: {round(self.look_angle_max_accel_normal, 5)}\n'
                f'{tab}    Look Angle Stiffness Normal: {round(self.look_angle_stiffness_normal, 5)}\n'
                f'{tab}    Look Angle Damping Normal: {round(self.look_angle_damping_normal, 5)}\n'
                f'{tab}    Look Angle Max Accel Attacking: {round(self.look_angle_max_accel_attacking, 5)}\n'
                f'{tab}    Look Angle Stiffness Attacking: {round(self.look_angle_stiffness_attacking, 5)}\n'
                f'{tab}    Look Angle Damping Attacking: {round(self.look_angle_damping_attacking, 5)}\n'
            )

            info += '\n'

        info += f'{tab}    Weapon Preference Count: {len(self.weapon_preference)}\n'
        for index in range(len(self.weapon_preference)):
            info += f'{tab}    Weapon Preference {index}: {self.weapon_preference.get_name(index)}\n'

        info += '\n'

        info += f'{tab}    Bot Templates: {len(self.templates)}\n'

        for template in self.templates:
            info += '\n'

            info += template.get_info(times+1)

        return info


# =============================================================================
# >> WeaponPreference
# =============================================================================
_WeaponPreference = csbots_type_manager.create_type_from_file(
    '_WeaponPreference',
    CSBOTS_DATA_PATH / 'bot_profile' / 'WeaponPreference.ini',
)

class WeaponPreference(_WeaponPreference, metaclass=csbots_type_manager):

    def __getitem__(self, index):
        if index < 0 or index >= self.array._length:
            raise IndexError('weapon_preference index out of range.')

        return weapon_class_table.get(self.array[index], None)

    def __setitem__(self, index, weapon):
        if index < 0 or index >= self.array._length:
            raise IndexError('weapon_preference index out of range.')

        if weapon is None or weapon == WeaponID.NONE:
            self.array[index] = 0

            if (index + 1) == self.count:
                self.count -= 1
        else:
            self.array[index] = get_weapon_class(weapon).id

            if index >= self.count:
                self.count = index + 1

    def __contains__(self, weapon):
        weapon_id = get_weapon_class(weapon).id
        for index in range(min(self.count, self.array._length)):
            if self.array[index] == weapon_id:
                return True

        return False

    def __iter__(self):
        for index in range(min(self.count, self.array._length)):
            yield weapon_class_table.get(self.array[index], None)

    def __len__(self):
        return self.count

    @property
    def array_length(self):
        return self.array._length

    def get_name(self, index):
        if index < 0 or index >= self.array._length:
            raise IndexError('weapon_preference index out of range.')

        weapon_class = weapon_class_table.get(self.array[index], None)
        if weapon_class is not None:
            return weapon_class.name

        return None

    def append(self, weapon):
        count = self.count
        if count >= self.array._lengh:
            raise IndexError('weapon_preference is full.')

        self.array[count] = get_weapon_class(weapon).id
        self.count = count + 1 if count >= 0 else 1

    def pop(self, index=None):
        count = self.count
        if not count:
            raise IndexError('Pop from empty weapon_preference.')

        if index is None:
            index = count - 1

        if index < 0 or index >= min(count, self.array._length):
            raise IndexError('Pop index out of range.')

        weapon_class = weapon_class_table.get(self.array[index], None)
        self.array[index] = 0
        self.count -= 1
        return weapon_class

    def reset(self):
        for index in range(self.array._length):
            self.array[index] = 0

        self.count = 0


# =============================================================================
# >> BotProfileTemplates
# =============================================================================
class BotProfileTemplates(UtlVector, metaclass=csbots_type_manager):
    _is_ptr = True
    _type = BotProfile


# =============================================================================
# >> BotProfileManager
# =============================================================================
_BotProfileManager = csbots_type_manager.create_type_from_file(
    '_BotProfileManager',
    CSBOTS_DATA_PATH / 'bot_profile' / 'BotProfileManager.ini',
)

class BotProfileManager(_BotProfileManager, metaclass=csbots_type_manager):

    def get_profile(self, profile_name, team=Team.UNASSIGNED):
        for profile in bot_profile_manager.profile_list:
            if profile.name == profile_name and profile.is_valid_team(team):
                return profile

        return None

    def get_template(self, template_name):
        for template in bot_profile_manager.template_list:
            if template.name == template_name:
                return template

        return None

    def get_profile_with_template(self, template_name, difficulty=None, team=Team.UNASSIGNED, max_difficulty=False, skip_taken=True):
        for profile in bot_profile_manager.profile_list:
            if not profile.inherits_from(template_name):
                continue

            if difficulty is not None:
                if max_difficulty:
                    if not profile.is_max_difficulty(difficulty):
                        continue
                else:
                    if not profile.is_difficulty(difficulty):
                        continue

            if not profile.is_valid_team(team):
                continue

            if not skip_taken and is_name_taken(profile.name):
                continue

            return profile

        return None

    def get_random_profile(difficulty=None, weapon_type=WeaponType.UNKNOWN, team=Team.UNASSIGNED, force_max_difficulty=False, skip_taken=True):
        profile_list = []

        for profile in bot_profile_manager.profile_list:
            if difficulty is not None:
                if force_max_difficulty:
                    if not profile.is_max_difficulty(difficulty):
                        continue
                else:
                    if not profile.is_difficulty(difficulty):
                        continue

            if weapon_type != WeaponType.UNKNOWN:
                weapon_class = profile.weapon_preference[0]
                if weapon_class is None:
                    continue

                if weapon_class.type != weapon_type:
                    continue

            if not profile.is_valid_team(team):
                continue

            if not skip_taken and is_name_taken(profile.name):
                continue

            profile_list.append(profile)

        if not profile_list:
            return None

        return random.choice(profile_list)


# =============================================================================
# >> BotProfileList
# =============================================================================
class BotProfileList(UtlLinkedList, metaclass=csbots_type_manager):
    _is_ptr = True
    _type = BotProfile


# =============================================================================
# >> VoiceBankList
# =============================================================================
class VoiceBankList(UtlVector, metaclass=csbots_type_manager):
    _is_ptr = False
    _type = Type.STRING_POINTER


# =============================================================================
# >> GLOBAL POINTERS
# =============================================================================
csbots_type_manager.create_global_pointers_from_file(
    CSBOTS_GP_DATA_PATH / 'bot_profile' / 'BotProfileManager.ini')

bot_profile_manager = csbots_type_manager.get_global_pointer(
    BotProfileManager)

