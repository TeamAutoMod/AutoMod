# type: ignore

import discord

from typing import Callable



class SelectModalBase(discord.ui.Modal):
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
        exc: Exception, 
        i: discord.Interaction
    ) -> None:
        await i.response.send_message(self.bot.locale.t(i.guild, "fail", exc=exc))


class ReactionRoleModal(SelectModalBase):
    def __init__(
        self, 
        bot, 
        guild: discord.Guild, 
        callback: Callable
    ) -> None:
        super().__init__(bot, "Reaction Roles", callback)
        self.guild = guild
    

        self.add_item(discord.ui.TextInput(
            label="Emoji",
            style=discord.TextStyle.short,
            placeholder="The emoji for the role",
            required=True,
            max_length=50
        ))


        # self.add_item(discord.ui.Select(
        #     placeholder="Select a role",
        #     min_values=1,
        #     max_values=1,
        #     options=[
        #         discord.SelectOption(
        #             label=x.name,
        #             value=x.mention
        #         ) for x in self.guild.roles
        #     ][:24]
        # ))