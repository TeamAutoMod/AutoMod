from discord import (
    Member,
    User,
    Guild,
    Message,
    Role,
    TextChannel,
    VoiceChannel,
    Thread
)
from discord.ext.commands import (
    Command,
    GroupMixin,
    GroupCog
)
from discord.app_commands import (
    AppCommand,
    ContextMenu,
    AppCommandGroup
)

from typing import (
    Union, 
    Iterable,
    List, 
    Dict, 
    Set, 
    FrozenSet,
    Any
)



# Discord
_DISCORD_BASE = Union[Member, User, Guild, Message, Role, TextChannel, VoiceChannel, Thread]
_LEGACY_COMMANDS = Union[Command, GroupMixin, GroupCog]
_APP_COMMANDS = Union[AppCommand, ContextMenu, AppCommandGroup]
DISCORD = Union[_DISCORD_BASE, _LEGACY_COMMANDS, _APP_COMMANDS]

# Defaults
KEY_TYPE = Union[str, int]
DEFAULT = Union[str, int, bool]
DEFAULT_WITH_EXTRAS = Union[DEFAULT, List[Any], Dict[KEY_TYPE, Any], Set[Any], FrozenSet[Any], DISCORD]

# Iterators
LIST = List[Union[DEFAULT, Dict[KEY_TYPE, Union[DEFAULT, List[DEFAULT_WITH_EXTRAS], Dict[KEY_TYPE, DEFAULT_WITH_EXTRAS]]]]]
DICT = Dict[KEY_TYPE, Union[DEFAULT, Dict[KEY_TYPE, Union[DEFAULT, List[DEFAULT_WITH_EXTRAS]]], LIST]]
SET = Set[Union[DEFAULT, Dict[KEY_TYPE, Union[DEFAULT, List[DEFAULT_WITH_EXTRAS], Dict[KEY_TYPE, DEFAULT_WITH_EXTRAS]]]]]
FROZENSET = Set[Union[DEFAULT, Dict[KEY_TYPE, Union[DEFAULT, List[DEFAULT_WITH_EXTRAS], Dict[KEY_TYPE, DEFAULT_WITH_EXTRAS]]]]]

# Special
S = Union[range, complex, float]

# Final
_PY_TYPES = Union[DEFAULT, LIST, DICT, SET, FROZENSET, Any]
_PY_TYPES_DISCORD = Union[_PY_TYPES, DISCORD, S]
_PY_TYPES_DISCORD_POSSIBLE_ITER = Iterable[_PY_TYPES_DISCORD]