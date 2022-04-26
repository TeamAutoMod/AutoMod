<<<<<<< HEAD
from discord.ext import commands

import datetime



def Tag(ctx: commands, name: str, content: str) -> dict:
    return {
        "id": f"{ctx.guild.id}-{name}",
        "uses": 0,

        "name": name,
        "content": content,

        "author": f"{ctx.author.id}",
        "editor": None,

        "created": datetime.datetime.utcnow(),
        "edited": None,
=======
from discord.ext import commands

import datetime



def Tag(ctx: commands, name: str, content: str) -> dict:
    return {
        "id": f"{ctx.guild.id}-{name}",
        "uses": 0,

        "name": name,
        "content": content,

        "author": f"{ctx.author.id}",
        "editor": None,

        "created": datetime.datetime.utcnow(),
        "edited": None,
>>>>>>> 049ddcde2a090ba7492f82b75ee62cc010bbc290
    }