# type: ignore

import discord

from random import randint
from typing import Union



def UserLevel(
    guild: discord.Guild, 
    user: Union[
        discord.Member, 
        discord.User
    ]
) -> dict:
    return {
        "id": f"{guild.id}-{user.id}",
        "guild": f"{guild.id}",
        "xp": randint(5, 15),
        "lvl": 1
    }