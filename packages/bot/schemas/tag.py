# type: ignore

import discord

import datetime



def Tag(
    ctx: discord.Interaction, 
    name: str, 
    content: str,
    ephemeral: bool,
    description: str
) -> dict:
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