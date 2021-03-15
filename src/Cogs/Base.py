from discord.ext import commands

from Bot.AutoMod import AutoMod


class BaseCog(commands.Cog):
    """Subclass of commands.Cog"""
    def __init__(self, bot):
        self.bot: AutoMod = bot
