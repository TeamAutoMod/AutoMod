<<<<<<< HEAD
import discord
from discord.ui import Button



class ConfirmBtn(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm")
    

    async def callback(self, interaction):
        try:
            await self.view.confirm_callback(interaction)
        except discord.NotFound:
            await interaction.response.defer()
    

class CancelBtn(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Cancel")
    

    async def callback(self, interaction):
        await self.view.cancel_callback(interaction)  


class LinkBtn(Button):
    def __init__(self, _url, _label, *args, **kwargs):
        super().__init__(*args, style=discord.ButtonStyle.link, url=_url, label=_label, **kwargs)


class CallbackBtn(Button):
    def __init__(self, label, callback, cid=None, disabled=False, emoji=None, style=discord.ButtonStyle.blurple):
        super().__init__(style=style, label=label, custom_id=cid, disabled=disabled, emoji=emoji)
        self._callback = callback


    async def callback(self, interaction: discord.Interaction):
        await self._callback(interaction)


class DeleteBtn(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label="", style=discord.ButtonStyle.red, emoji="🗑️", **kwargs)


    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except discord.NotFound:
=======
import discord
from discord.ui import Button



class ConfirmBtn(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm")
    

    async def callback(self, interaction):
        try:
            await self.view.confirm_callback(interaction)
        except discord.NotFound:
            await interaction.response.defer()
    

class CancelBtn(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Cancel")
    

    async def callback(self, interaction):
        await self.view.cancel_callback(interaction)  


class LinkBtn(Button):
    def __init__(self, _url, _label, *args, **kwargs):
        super().__init__(*args, style=discord.ButtonStyle.link, url=_url, label=_label, **kwargs)


class CallbackBtn(Button):
    def __init__(self, label, callback, cid=None, disabled=False, emoji=None, style=discord.ButtonStyle.blurple):
        super().__init__(style=style, label=label, custom_id=cid, disabled=disabled, emoji=emoji)
        self._callback = callback


    async def callback(self, interaction: discord.Interaction):
        await self._callback(interaction)


class DeleteBtn(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label="", style=discord.ButtonStyle.red, emoji="🗑️", **kwargs)


    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except discord.NotFound:
>>>>>>> 049ddcde2a090ba7492f82b75ee62cc010bbc290
            await interaction.response.defer()