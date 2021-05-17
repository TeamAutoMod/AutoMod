import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .events import OnMessage, OnMessageEdit



class AutomodPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_message(
        self, 
        message
    ):
        await OnMessage.run(self, message)

    
    @commands.Cog.listener()
    async def on_message_edit(
        self, 
        before, 
        after
    ):
        await OnMessageEdit.run(self, before, after)


def setup(bot):
    pass