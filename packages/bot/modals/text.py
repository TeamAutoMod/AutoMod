import discord#
from discord.ui import Modal

from typing import Callable



class TextModalBase(Modal):
    def __init__(
        self, 
        bot, 
        title: str, 
        callback: Callable, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, title=title, **kwargs)
        self.bot = bot
        self.callback = callback


    async def on_submit(
        self, 
        i: discord.Interaction
    ) -> None:
        await self.callback(i)

    
    async def on_error(
        self, 
        i: discord.Interaction,
        exc: Exception
    ) -> None:
        await i.response.send_message(self.bot.locale.t(i.guild, "fail", _emote="NO", exc=exc))


class FilterModal(TextModalBase):
    def __init__(
        self, 
        bot, 
        title: str, 
        callback: Callable
    ) -> None:
        super().__init__(bot, title, callback)
    

    name = discord.ui.TextInput(
        custom_id="name",
        label="Name",
        style=discord.TextStyle.short,
        placeholder="Name of the filter",
        required=True,
        max_length=20
    )


    warns = discord.ui.TextInput(
        custom_id="warns",
        label="Warns",
        style=discord.TextStyle.long,
        placeholder="Warns given upon violation. Use 0 to just have the message deleted",
        required=True,
        max_length=2
    )


    words = discord.ui.TextInput(
        custom_id="words",
        label="Words",
        style=discord.TextStyle.long,
        placeholder="Words and phrases for this filter, seperated by commas",
        required=True,
        max_length=2000
    )


    channels = discord.ui.TextInput(
        custom_id="channels",
        label="Channels",
        style=discord.TextStyle.long,
        placeholder="IDs of channels this filter should be active in. Leave blank for server-wide enforcement",
        required=False,
        max_length=3000
    )