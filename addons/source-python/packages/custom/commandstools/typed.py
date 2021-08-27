# ../addons/source-python/packages/custom/commandstools/typed.py

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Commands
from commands.typed import TypedClientCommand
from commands.typed import TypedSayCommand
from commands.typed import TypedServerCommand
#   Core
from core import echo_console
#   Messages
from messages import SayText2
from messages import TextMsg
from messages import HudDestination
#   Translations
from translations.strings import TranslationStrings


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('reply'
           )


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def reply(command_info, message, language=None, **tokens):
    if command_info.typed_command_cls is TypedClientCommand:
        TextMsg(message, HudDestination.CONSOLE).send(command_info.index, **tokens)

    elif command_info.typed_command_cls is TypedSayCommand:
        SayText2(message, chat=True, color="​").send(command_info.index, **tokens)

    elif command_info.typed_command_cls is TypedServerCommand:
        if isinstance(message, TranslationStrings):
            message = message.get_string(language, **tokens)

        echo_console(message)

