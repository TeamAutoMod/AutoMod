# type: ignore
import discord

from typing import Union, Dict



def Highlights(obj: Union[discord.Interaction, discord.Message]) -> Dict[str, Union[str, Dict[str, list]]]:
    return {
        "id": f"{obj.guild.id}",
        "highlights": {
            f"{obj.user.id if isinstance(obj, discord.Interaction) else obj.author.id}": []
        }
    }