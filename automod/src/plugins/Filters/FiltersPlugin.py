import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .commands import (
    FilterAdd, 
    FilterRemove, 
    FilterHelp, 
    FilterList
)
from .events import (
    OnMessage
)



class FiltersPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.ban_members


    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):
        await OnMessage.run(self, message)


    @commands.group(name="filter")
    async def _filter(
        self, 
        ctx
    ):
        """filter_help"""
        if ctx.subcommand_passed is None:
            await FilterHelp.run(self, ctx)


    @_filter.command()
    async def add(
        self,
        ctx,
        name,
        warns: int,
        *,
        words
    ):
        """filter_add_help"""
        await FilterAdd.run(self, ctx, name, warns, words)


    @_filter.command()
    async def remove(
        self,
        ctx,
        name
    ):
        """filter_remove_help"""
        await FilterRemove.run(self, ctx, name)


    @_filter.command()
    async def show(
        self,
        ctx
    ):
        """filter_show_help"""
        await FilterList.run(self, ctx)


    




def setup(bot):
    pass