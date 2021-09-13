import discord
from discord.ext import commands

from collections import defaultdict

from ..PluginBlueprint import PluginBlueprint
from .events import (
    OnMessage
)
from .Types import SpamChecker



class AntispamPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.spam_checker = defaultdict(SpamChecker)
        self.is_being_handled = list()


    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):
        await OnMessage.run(self, message)



def setup(bot):
    pass