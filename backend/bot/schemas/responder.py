# type: ignore

import discord

import datetime
from typing import Union



def Responder(ctx: discord.Interaction, name: str, content: str, trigger: Union[str, list], position: str, ignore_mods: bool) -> dict:
    return {
        "id": f"{ctx.guild.id}-{name}",
        "uses": 0,

        "name": name,
        "content": content,
        "trigger": trigger,
        "position": position.lower(),
        "ignore_mods": ignore_mods,

        "author": f"{ctx.user.id}",
        "editor": None,

        "created": datetime.datetime.utcnow(),
        "edited": None,
    }