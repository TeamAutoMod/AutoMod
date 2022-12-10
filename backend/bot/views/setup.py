# type: ignore

import discord
from discord.ui import View, Select # pyright: reportMissingImports=false

from typing import List



class SetupView(View):
    def __init__(self, bot, embeds: List[discord.Embed], current_select: str = None, *args, **kwargs) -> None:
        self.bot = bot
        self._emotes = {
            "setup guide": self.bot.emotes.get("HELP"),
            "logging": self.bot.emotes.get("LOG"),
            "automoderator": self.bot.emotes.get("SWORDS"),
            "punishments": self.bot.emotes.get("PUNISHMENT")
        }
        super().__init__(
            *args,
            **kwargs
        )

        self.add_item(
            Select(
                placeholder="Select Feature",
                options=[
                    discord.SelectOption(
                        label=e.title,
                        value=e.title.lower(),
                        emoji=self._emotes[e.title.lower()],
                        default=False if current_select == None else True if current_select.lower() == e.title.lower() else False
                    ) for e in embeds[1:]
                ],
                custom_id="setup-select"
            )
        )