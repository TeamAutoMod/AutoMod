# type: ignore

import discord
from discord.ui import View # pyright: reportMissingImports=false

from .buttons import LinkBtn



class ConfigView(View):
    def __init__(self, bot, *args, **kwargs) -> None:
        super().__init__(
            *args, 
            **kwargs
        )
        self.bot = bot
        self.add_item(LinkBtn(_url=f"{bot.config.support_invite}", _label="Support Server"))
