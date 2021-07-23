import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .events import (
    OnMemberRemove, 
    OnMemberJoin
)



class PersistPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):
        await OnMemberRemove.run(self, member)


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):
        await OnMemberJoin.run(self, member)



def setup(bot):
    pass