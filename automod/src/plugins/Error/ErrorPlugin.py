import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .events import (
    OnCommandError
)



class ErrorPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx,
        error
    ):
        await OnCommandError.run(self, ctx, error)





def setup(bot):
    pass