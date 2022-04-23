import discord
from discord.ui import View

from .buttons import ConfirmBtn, CancelBtn



class ConfirmView(View):
    def __init__(self, guild_id, on_confirm, on_cancel, on_timeout, check, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(ConfirmBtn())
        self.add_item(CancelBtn())

        self.guild_id = guild_id

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.timeout_callback = on_timeout
        self.check = check


    async def on_timeout(self):
        await self.timeout_callback()
    

    async def confirm_callback(self, interaction):
        if await self.exec_check(interaction):
            await self.on_confirm(interaction)
            self.stop()


    async def cancel_callback(self, interaction):
        if await self.exec_check(interaction):
            await self.on_cancel(interaction)
            self.stop()


    async def exec_check(self, interaction):
        if not self.check:
            return True
        if self.check(interaction):
            return True
        await self.refuse(interaction)
        return False


    async def refuse(self, interaction):
        interaction.response.send_message("Invalid interactor", ephermal=True)