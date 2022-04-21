import discord

from typing import Union



def Slowmode(guild: discord.Guild, channel: discord.TextChannel, mod: Union[discord.Member, discord.User], time: str, pretty: str, mode: str) -> dict:
    return {
        "id": f"{guild.id}-{channel.id}",
        "time": f"{time}",
        "pretty": pretty,
        "mode": mode,
        "mod": f"{mod.id}",
        "users": {}
    }