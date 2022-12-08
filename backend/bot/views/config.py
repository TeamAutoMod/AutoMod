# type: ignore

import discord
from discord.ui import View # pyright: reportMissingImports=false

from .buttons import CallbackBtn
from ..types import Embed



class ConfigView(View):
    def __init__(self, bot, *args, **kwargs) -> None:
        super().__init__(
            *args, 
            **kwargs
        )
        self.bot = bot

        self.add_items()

    
    def add_items(self) -> None:
        for name in [
            "View Config",
            "Auto-Punishments",
            "Logging",
            "Join Role"
        ]:
            self.add_item(
                CallbackBtn(
                    label=name,
                    callback=self.show_help,
                    cid=name,
                    style=discord.ButtonStyle.grey
                )
            )


    async def show_help(self, i: discord.Interaction) -> None:
        e = Embed(
            i,
            title=self.bot.locale.t(i.guild, f"{i.data['custom_id']}_title"),
            description=self.bot.locale.t(i.guild, f"{i.data['custom_id']}_desc")
        )
        try:
            await i.response.send_message(embed=e)
        except Exception:
            pass
