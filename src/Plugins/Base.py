from discord.ext import commands

from Bot.AutoMod import AutoMod


class BasePlugin(commands.Cog):
    """Subclass of commands.Cog"""
    def __init__(self, bot):
        self.bot: AutoMod = bot