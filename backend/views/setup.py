import discord
from discord.ui import View, Select # pyright: reportMissingImports=false

from typing import List



class SetupView(View):
    def __init__(
        self, 
        bot, 
        embeds: List[
            discord.Embed
        ],
        *args, 
        **kwargs
    ) -> None:
        self.bot = bot
        super().__init__(*args, **kwargs)

        self.add_item(
            Select(
                placeholder="Select a feature",
                options=[
                    discord.SelectOption(
                        label=e.title,
                        value=e.title[2:].lower()
                    ) for e in embeds
                ],
                custom_id="setup-select"
            )
        )