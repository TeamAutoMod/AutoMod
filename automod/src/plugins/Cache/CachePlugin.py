import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint

from .events import (
    OnGuildChannelCreate,
    OnGuildChannelDelete,
    OnGuildRoleCreate,
    OnGuildRoleDelete
)



class CachePlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_guild_channel_create(
        self,
        channel
    ):
        await OnGuildChannelCreate.run(self, channel)


    @commands.Cog.listener()
    async def on_guild_channel_delete(
        self,
        channel
    ):
        await OnGuildChannelDelete.run(self, channel)


    @commands.Cog.listener()
    async def on_guild_role_create(
        self,
        role
    ):
        await OnGuildRoleCreate.run(self, role)


    @commands.Cog.listener()
    async def on_guild_role_delete(
        self,
        role
    ):
        await OnGuildRoleDelete.run(self, role)



def setup(bot):
    bot.add_cog(CachePlugin(bot))