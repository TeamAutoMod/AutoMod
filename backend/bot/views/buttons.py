# type: ignore

import discord
from discord.ui import Button

from typing import Callable

from ..types import E



class ConfirmBtn(Button):
    def __init__(
        self, 
        bot
    ) -> None:
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", emoji=bot.emotes.get("YES"))


    async def callback(
        self, 
        interaction: discord.Interaction
    ) -> None:
        try:
            await self.view.confirm_callback(interaction)
        except discord.NotFound:
            await interaction.response.defer(ephemeral=True)
    

class CancelBtn(Button):
    def __init__(
        self, 
        bot
    ) -> None:
        super().__init__(style=discord.ButtonStyle.red, label="Cancel", emoji=bot.emotes.get("NO"))


    async def callback(
        self, 
        interaction: discord.Interaction
    ) -> None:
        try:
            await self.view.cancel_callback(interaction)
        except discord.NotFound:
            await interaction.response.defer(ephemeral=True)


class LinkBtn(Button):
    def __init__(
        self, 
        _url: str, 
        _label: str, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, style=discord.ButtonStyle.link, url=_url, label=_label, **kwargs)


class CallbackBtn(Button):
    def __init__(
        self, 
        label: str, 
        callback: Callable, 
        check: Callable,
        cid: str = None, 
        disabled: bool = False, 
        emoji: str = None, 
        style=discord.ButtonStyle.blurple
    ) -> None:
        super().__init__(style=style, label=label, custom_id=cid, disabled=disabled, emoji=emoji)
        self._callback = callback
        self.check = check


    async def callback(
        self, 
        interaction: discord.Interaction
    ) -> None:
        if self.check(interaction.user.id):
            await self._callback(interaction)
        else:
            await interaction.response.defer(ephemeral=True)


class DeleteBtn(Button):
    def __init__(
        self, 
        check: Callable,
        *args, 
        **kwargs,
    ) -> None:
        super().__init__(*args, label="", style=discord.ButtonStyle.red, emoji="🗑️", **kwargs)
        self.check = check


    async def callback(
        self, 
        interaction: discord.Interaction
    ) -> None:
        if self.check(interaction.user.id):
            try:
                await interaction.message.delete()
            except discord.NotFound:
                await interaction.response.defer(ephemeral=True)
        else:
            await interaction.response.defer(ephemeral=True)


class ActionedBtn(Button):
    def __init__(
        self, 
        bot,
        check: Callable,
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, label="Actioned", style=discord.ButtonStyle.grey, emoji=bot.emotes.get("YES"), **kwargs)
        self.check = check


    async def callback(
        self, 
        interaction: discord.Interaction
    ) -> None:
        if self.check(interaction.user.id):
            try:
                await interaction.message.delete()
            except discord.NotFound:
                await interaction.response.defer(ephemeral=True)
        else:
            await interaction.response.defer(ephemeral=True)


class DeleteHighlightBtn(Button):
    def __init__(self, bot, check: Callable, delete_func: Callable, func_args: dict, *args, **kwargs) -> None:
        super().__init__(
            *args, 
            label="Delete Highlight", 
            style=discord.ButtonStyle.red, 
            emoji=bot.emotes.get("TRASH"), 
            **kwargs
        )
        self.bot = bot
        self.check = check
        self.delete_func = delete_func
        self.func_args = func_args


    async def callback(self, i: discord.Interaction) -> None:
        if self.check(i.user.id):
            guild: discord.Guild = self.func_args.get("guild")
            try:
                self.delete_func(**self.func_args)
            except Exception as ex:
                await i.response.edit_message(embed=E(self.bot.locale.t(guild, "fail", _emote="NO", exc=ex), 0), view=None)
            else:
                await i.response.edit_message(embed=E(self.bot.locale.t(guild, "deleted_highlight", _emote="YES", phrase=self.func_args.get("old_highlight")), 1), view=None)
        else:
            await i.response.defer(ephemeral=True)