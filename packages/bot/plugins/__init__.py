# type: ignore

import discord
from discord.ext import commands as _commands

from typing import TypeVar

from ..bot import ShardedBotInstance



T = TypeVar("T")


class AutoModPluginBlueprint(_commands.Cog):
    def __init__(
        self, 
        bot: ShardedBotInstance,
        requires_premium: bool = False
    ):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
        self.locale = bot.locale
        self._requires_premium = requires_premium


    def get_prefix(
        self, 
        guild: discord.Guild
    ) -> str:
        if guild == None:
            return self.bot.config.default_prefix
        else:
            p = self.db.configs.get(guild.id, "prefix")
            return p if p != None else self.bot.config.default_prefix
    

    def error(
        self,
        ctx: discord.Interaction,
        error: T
    ) -> None:
        self.bot.dispatch("command_error", ctx, error)


    def before_load(
        self, 
        *args, 
        **kwargs
    ) -> None:
        super().cog_load(*args, **kwargs)

    
    def after_load(
        self, 
        *args, 
        **kwargs
    ) -> None:
        super().cog_unload(*args, **kwargs)