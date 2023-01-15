# type: ignore

import discord

import datetime
from typing import Dict, Union



def CustomCommand(ctx: discord.Interaction, name: str, content: str, ephemeral: bool, description: str) -> Dict[str, Union[str, bool]]:
    return {
        "id": f"{ctx.guild.id}-{name}",
        "uses": 0,

        "name": name,
        "content": content,
        "description": description,
        "ephemeral": ephemeral,

        "author": f"{ctx.user.id}",
        "editor": None,

        "created": datetime.datetime.utcnow(),
        "edited": None,
    }