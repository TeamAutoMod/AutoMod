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
        "xp": randint(15, 25),
        "lvl": 1
    }