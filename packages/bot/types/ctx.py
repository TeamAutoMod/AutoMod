import discord
from discord.ext import commands

from typing import Optional, Union

from .embed import Embed



class Context(commands.Context):
    def __init__(
        self, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)


    async def send(
        self, 
        *args, 
        embed: Union[
            Embed, 
            None
        ] = None, 
        **kwargs
    ) -> Optional[
        discord.Message
    ]:
        if embed != None:
            e: dict = embed.to_dict()
            if e.get("fields", None) != None:
                for field in e.get("fields"):
                    field["value"] = field["value"][:1023]
                embed = Embed.from_dict(e)
        
        return await super().send(*args, embed=embed, **kwargs)