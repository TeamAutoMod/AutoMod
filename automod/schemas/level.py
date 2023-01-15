# type: ignore

import discord

from random import randint
from typing import Union, Dict



def UserLevel(guild: discord.Guild, user: Union[discord.Member, discord.User]) -> Dict[str, Union[str, int]]:
    return {
        "id": f"{guild.id}-{user.id}",
        "guild": f"{guild.id}",
        "xp": randint(5, 10),
        "lvl": 1
    }