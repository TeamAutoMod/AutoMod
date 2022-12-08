# type: ignore

import discord
from discord.ext import commands as _commands

from typing import Type

from ..bot import ShardedBotInstance



class AutoModPluginBlueprint(_commands.Cog):
    def __init__(self, bot: ShardedBotInstance, requires_premium: bool = False):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
        self.locale = bot.locale
        self._requires_premium = requires_premium
    

    def error(self, ctx: discord.Interaction, error: Type[Exception]) -> None:
        self.bot.dispatch("command_error", ctx, error)