# ../addons/source-python/packages/custom/csbots/engines/csgo/__init__.py

"""Provides CS:GO specific Counter-Strike bot based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Cvars
from cvars import cvar
#   Memory
from memory import make_object
from memory.helpers import MemberFunction
#   Players
from players.helpers import index_from_userid

# CSBots Imports
#   CSBots
from csbots import create_bot
#   Base
from csbots._base import Bot as _Bot


# =============================================================================
# >> CONVARS
# =============================================================================
bot_quota = cvar.find_var("bot_quota")


# =============================================================================
# >> CLASSES
# =============================================================================
class Bot(_Bot):
    """Class used to interact directly with bots."""

    # Instances of this class will be cached by default
    caching = True

    @classmethod
    def create(cls, bot_profile, team, name=None):
        if name is not None:
            bot_profile = bot_profile.copy(name)

        #if bot_profile.name is None:
        #    raise ValueError('Name not specified.')

        bot = make_object(cls, create_bot(bot_profile, team))
        bot_quota.set_int(bot_quota.get_int()+1)

        return bot

    def get_bot_profile(self):
        """Return the bot's bot profile instance.

        :rtype: BotProfile
        """
        return self._bot_profile

    def set_bot_profile(self, bot_profile):
        """Set the bot's bot profile instance.

        :param BotProfile bot_profile:
            The bot profile to set.
        """
        self._bot_profile.clone(bot_profile)

    bot_profile = property(get_bot_profile, set_bot_profile)

