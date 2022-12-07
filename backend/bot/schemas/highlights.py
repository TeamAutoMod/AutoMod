# type: ignore
import discord

from typing import Union



def Highlights(obj: Union[discord.Interaction, discord.Message]) -> dict:
    return {
        "id": f"{obj.guild.id}",
        "highlights": {
            f"{obj.user.id if isinstance(obj, discord.Interaction) else obj.author.id}": []
        }
    }