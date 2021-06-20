import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .events import OnMessageDelete, OnMessageEdit, OnVoiceStateUpdate, OnMemberJoin, OnMemberRemove, OnMemberUnban



class LogsPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_message_delete(
        self, 
        message
    ):
        await OnMessageDelete.run(self, message)


    @commands.Cog.listener()
    async def on_message_edit(
        self, 
        before,
        after
    ):
        await OnMessageEdit.run(self, before, after)


    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):
        await OnVoiceStateUpdate.run(self, member, before, after)


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):
        await OnMemberJoin.run(self, member)


    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):
        await OnMemberRemove.run(self, member)


    @commands.Cog.listener()
    async def on_member_unban(
        self,
        guild,
        user
    ):
        await OnMemberUnban.run(self, guild, user)



def setup(bot):
    pass