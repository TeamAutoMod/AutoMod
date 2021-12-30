import discord
from discord.ext import commands

import logging; log = logging.getLogger()

from . import AutoModPlugin
from ..schemas import GuildConfig



class AutomodPlugin(AutoModPlugin):
    """Plugin for all utility commands"""
    def __init__(self, bot):
        super().__init__(bot)

    @AutoModPlugin.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild == None: return



def setup(bot): bot.register_plugin(AutomodPlugin(bot))