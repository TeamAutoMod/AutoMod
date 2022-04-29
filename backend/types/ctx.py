import discord
from discord.ext import commands

from typing import Optional, Union

from .embed import Embed



class Context(commands.Context):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


    async def send(self, *args, embed: Union[Embed, None] = None, **kwargs) -> Optional[discord.Message]:
        if embed != None:
            embed: dict = embed.to_dict()
            if "fields" in embed:
                for field in embed["fields"]:
                    field["value"] = field["value"][:1023]
                embed = Embed.from_dict(embed)
        
        return await super().send(*args, embed=embed, **kwargs)