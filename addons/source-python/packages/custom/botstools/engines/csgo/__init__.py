# ../botstools/engines/csgo/__init__.py

"""Provides CS:GO specific Bot based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core.cache import cached_property
#   Cvars
from cvars import ConVar
#   Memory
from memory import make_object
from memory.helpers import MemberFunction
#   Paths
from paths import CUSTOM_DATA_PATH
#   Players
from players.helpers import playerinfo_from_index
from players.helpers import index_from_userid

# Memory Tools Imports
#   Memory Tools
from memorytools.manager import create_type_from_file

# Bots Tools Imports
#   Bots Tools
from botstools._base import Bot as _Bot


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
CCSBot = create_type_from_file('CCSBot',
    CUSTOM_DATA_PATH / 'botstools' / 'entities' / 'CCSBot.ini')


# =============================================================================
# >> CLASSES
# =============================================================================
class Bot(_Bot):
    """Class used to interact directly with bots."""

    # Instances of this class will be cached by default
    caching = True

    def __init__(self, index, caching=True):
        """Initialize the object.

        :param int index:
            A valid bot index.
        :param bool caching:
            Whether to lookup the cache for an existing instance or not.
        :raise ValueError:
            Raised if the index is invalid or not a bot.
        """
        playerinfo = playerinfo_from_index(index)
        if not playerinfo.is_fake_client() and playerinfo.steamid != 'BOT':
            raise ValueError('Invalid bot index.')

        super().__init__(index, caching)

    @classmethod
    def from_userid(cls, userid, caching=None):
        """Create an instance from a userid.

        :param int userid:
            The userid.
        :param bool caching:
            Whether to lookup the cache for an existing instance or not.
        :rtype: Bot
        """
        return cls(index_from_userid(userid), caching=caching)

    def __getattr__(self, attr):
        """Find if the attribute is valid and returns the appropriate value."""
        try:
            # Get the CCSBot attribute's value
            value = getattr(self.cs_bot, attr)
        except AttributeError:
            # No attribute was found, call superclass
            return super().__getattr__(attr)

        # Is the value a dynamic function?
        if isinstance(value, MemberFunction):

            # Cache the value
            with suppress(AttributeError):
                object.__setattr__(self, attr, value)

        # Return the attribute's value
        return value

    def __setattr__(self, attr, value):
        """Find if the attribute is valid and sets its value."""
        # Is the given attribute a property?
        if (attr in super().__dir__() and isinstance(
                getattr(self.__class__, attr, None), property)):

            # Set the property's value
            object.__setattr__(self, attr, value)

            # No need to go further
            return

        # Does the CCSBot contain the given attribute?
        if hasattr(CCSBot, attr):

            # Set the attribute's value
            setattr(self.cs_bot, attr, value)

            # No need to go further
            return

        # If the attribute is not found, just set the attribute
        super().__setattr__(attr, value)

    def __dir__(self):
        """Return an alphabetized list of attributes for the instance."""
        # Get the base attributes
        attributes = set(super().__dir__())

        # Loop through all of the CCSBot' attributes
        for attr in dir(CCSBot):

            # Add the attribute if it is not private
            if not attr.startswith('_'):
                attributes.add(attr)

        # Return a sorted list of attributes
        return sorted(attributes)

    @classmethod
    def create(cls, bot_profile, team, name=None):
        if name is not None:
            bot_profile.name = name

        if bot_profile.name is None:
            raise ValueError('Name not specified.')

        bot = make_object(cls, CCSBot._create_bot(bot_profile, team))
        bot_quota = ConVar("bot_quota")
        bot_quota.set_int(bot_quota.get_int()+1)
        return bot

    @cached_property
    def cs_bot(self):
        return make_object(CCSBot, self.pointer)

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

