import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .events import (
    OnRawReactionAdd,
    OnRawReactionRemove
)
from .commands import (
    Starboard,
    StarboardChannel
)


class StarboardPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload: discord.RawReactionActionEvent
    ):
        await OnRawReactionAdd.run(self, payload)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self,
        payload: discord.RawReactionActionEvent
    ):
        await OnRawReactionRemove.run(self, payload)


    @commands.group()
    async def starboard(
        self,
        ctx
    ):
        """starboard_help"""
        if ctx.invoked_subcommand is None:
            await Starboard.run(self, ctx)


    @starboard.command()
    async def channel(
        self,
        ctx,
        channel: discord.TextChannel
    ):
        """starboard_channel_help"""
        await StarboardChannel.run(self, ctx, channel)



def setup(bot):
    pass