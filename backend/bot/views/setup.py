# type: ignore

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
        current_select: str = None,
        *args, 
        **kwargs
    ) -> None:
        self.bot = bot
        super().__init__(*args, **kwargs)

        self.add_item(
            Select(
                placeholder="Select Feature",
                options=[
                    discord.SelectOption(
                        label=e.title,
                        value=e.title[2:].lower(),
                        default=False if current_select == None else True if current_select.lower() == e.title[2:].lower() else False
                    ) for e in embeds
                ],
                custom_id="setup-select"
            )
        )