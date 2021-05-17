import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .commands import Clean



class CleanPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.cleaning = list()


    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.manage_messages

    
    @commands.command(
        aliases=["purge", "clear"],
        usage="clean <amount> [-user] [-contains] [-starts] [-ends] [-or] [-not] [-emojis] [-bots] [-embeds] [-files] [-reactions] [-after] [-before]"
    )
    async def clean(
        self,
        ctx,
        amount: int,
        *,
        args: str = None
    ):
        """clean_help"""
        await Clean.run(self, ctx, amount, args)


def setup(bot):
    pass