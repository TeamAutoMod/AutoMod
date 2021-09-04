import discord
from discord.ext import commands

from typing import Union

from ..PluginBlueprint import PluginBlueprint
from .commands import (
    Config, 
    Setup, 
    SetupMuted, 
    SetupAutomod, 
    SetupRestrict,
    DMOnActions, 
    Persist, 
    ModLog, 
    MessageLog, 
    VoiceLog, 
    ServerLog, 
    Prefix
)



class ConfigPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator


    @commands.group()
    async def setup(
        self,
        ctx
    ):
        """setup_help"""
        if ctx.subcommand_passed is None:
            await Setup.run(self, ctx)


    @setup.command()
    async def muted(
        self, 
        ctx
    ):
        """setup_muted_help"""
        await SetupMuted.run(self, ctx)


    @setup.command()
    async def automod(
        self, 
        ctx
    ):
        """setup_automod_help"""
        await SetupAutomod.run(self, ctx)


    @setup.command()
    async def restrict(
        self,
        ctx
    ):
        """setup_restrict_help"""
        await SetupRestrict.run(self, ctx)


    @commands.command()
    async def config(
        self, 
        ctx
    ):
        """config_help"""
        await Config.run(self, ctx)


    @commands.command()
    async def modlog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """modlog_help"""
        await ModLog.run(self, ctx, channel)


    @commands.command()
    async def voicelog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """voicelog_help"""
        await VoiceLog.run(self, ctx, channel)


    @commands.command()
    async def serverlog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """serverlog_help"""
        await ServerLog.run(self, ctx, channel)

    
    @commands.command()
    async def messagelog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """messagelog_help"""
        await MessageLog.run(self, ctx, channel)


    @commands.command()
    async def dm_on_actions(
        self,
        ctx
    ):
        """dm_on_actions_help"""
        await DMOnActions.run(self, ctx) 


    @commands.command()
    async def persist(
        self,
        ctx
    ):
        """persist_help"""
        await Persist.run(self, ctx) 


    @commands.command()
    async def prefix(
        self,
        ctx,
        prefix: str
    ):
        """prefix_help"""
        await Prefix.run(self, ctx, prefix) 



def setup(bot):
    pass