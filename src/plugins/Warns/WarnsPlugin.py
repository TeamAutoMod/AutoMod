import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from ..Types import Duration, Reason, DiscordUser
from .commands import Punishment, Warn, Check, Unwarn



class WarnsPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def punishment(
        self, 
        ctx,
        warns: int,
        action: str,
        time: Duration = None
    ):
        """punishment_help"""
        await Punishment.run(self, ctx, warns, action, time)


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def warn(
        self,
        ctx,
        users: commands.Greedy[discord.Member],
        warns: int = None,
        *,
        reason: Reason = None
    ):
        """warn_help"""
        await Warn.run(self, ctx, users, warns, reason)


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def unwarn(
        self,
        ctx,
        users: commands.Greedy[discord.Member],
        warns: int = None,
        *,
        reason: Reason = None
    ):
        """unwarn_help"""
        await Unwarn.run(self, ctx, users, warns, reason)



    @commands.command(aliases=["warns"])
    @commands.has_guild_permissions(kick_members=True)
    async def check(
        self,
        ctx,
        user: DiscordUser
    ):
        """check_help"""
        await Check.run(self, ctx, user)




def setup(bot):
    pass