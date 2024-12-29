# ../addons/source-python/packages/custom/csbots/_base.py

"""Provides a class used to interact with a specific Counter-Strike bot."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core.cache import cached_property
#   Memory
from memory import make_object
from memory.helpers import MemberFunction
#   Players
from players.entity import Player
from players.helpers import index_from_userid

# CSBots Imports
#   CSBots
from csbots import CSBot


# =============================================================================
# >> CLASSES
# =============================================================================
class Bot(Player):
    """Class used to interact directly with Bots."""

    # Instances of this class will be cached by default
    caching = True

    def __init__(self, index, caching=True):
        """Initialize the object.

        :param int index:
            A valid Counter-Strike bot index.
        :param bool caching:
            Whether to lookup the cache for an existing instance or not.
        :raise ValueError:
            Raised if the index is invalid or not a Counter-Strike bot.
        """
        super().__init__(index, caching)

        if not self.pointer.type_info.is_derived_from('CCSBot'):
            raise ValueError('Invalid Counter-Strike Bot index.')

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
            # Get the CSBot attribute's value
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

        # Does the CSBot contain the given attribute?
        if hasattr(CSBot, attr):

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

    @cached_property
    def cs_bot(self):
        return make_object(CCSBot, self.pointer)

