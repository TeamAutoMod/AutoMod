import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint



class CachePlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_guild_channel_create(
        self,
        channel
    ):
        self.bot.cache.text_channels[channel.guild.id] = channel.guild.text_channels
        self.bot.cache.voice_channels[channel.guild.id] = channel.guild.voice_channels


    @commands.Cog.listener()
    async def on_guild_channel_delete(
        self,
        channel
    ):
        self.bot.cache.text_channels[channel.guild.id] = channel.guild.text_channels
        self.bot.cache.voice_channels[channel.guild.id] = channel.guild.voice_channels


    @commands.Cog.listener()
    async def on_guild_role_create(
        self,
        role
    ):
        self.bot.cache.roles[role.guild.id] = role.guild.roles


    @commands.Cog.listener()
    async def on_guild_role_delete(
        self,
        role
    ):
        self.bot.cache.roles[role.guild.id] = role.guild.roles



def setup(bot):
    bot.add_cog(CachePlugin(bot))