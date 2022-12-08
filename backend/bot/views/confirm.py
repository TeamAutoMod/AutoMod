# type: ignore

import discord
from discord.ui import View

from types import LambdaType
from typing import Callable

from .buttons import ConfirmBtn, CancelBtn



class ConfirmView(View):
    def __init__(self, bot, guild_id: int, on_confirm: Callable, on_cancel: Callable, on_timeout: Callable, check: LambdaType, timeout: int = 30) -> None:
        super().__init__(
            timeout=timeout
        )
        self.add_item(ConfirmBtn(bot))
        self.add_item(CancelBtn(bot))

        self.guild_id = guild_id

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.timeout_callback = on_timeout
        self.check = check


    async def on_timeout(self) -> None:
        await self.timeout_callback()
    

    async def confirm_callback(self, i: discord.Interaction) -> None:
        if await self.exec_check(i):
            await self.on_confirm(i)
            self.stop()


    async def cancel_callback(self, i: discord.Interaction) -> None:
        if await self.exec_check(i):
            await self.on_cancel(i)
            self.stop()


    async def exec_check(self, i: discord.Interaction) -> None:
        if not self.check:
            return True
        if self.check(i):
            return True
        await self.refuse(i)
        return False


    async def refuse(self, i: discord.Interaction) -> None:
        i.response.send_message("Invalid interaction", ephemeral=True)