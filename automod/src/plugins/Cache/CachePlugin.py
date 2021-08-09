import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint

from .sub.RefillCache import refillCache



class CachePlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.loop.create_task(refillCache(self))



def setup(bot):
    bot.add_cog(CachePlugin(bot))