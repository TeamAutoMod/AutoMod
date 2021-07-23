import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from ..Types import Reason, DiscordUser, Duration
from .commands import (
    Ban, 
    Softban, 
    Forceban, 
    Mute, 
    Unmute, 
    Unban, 
    Kick,
    Clean, 
    CleanBots, 
    CleanBetween, 
    CleanUser, 
    CleanUntil, 
    CleanLast,
    CyberNuke
)
from .functions.UnmuteTask import unmuteTask


class ModerationPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.loop.create_task(unmuteTask(self.bot))
        self.running_cybernukes = list()

    
    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def kick(
        self, 
        ctx, 
        users: commands.Greedy[discord.Member], 
        *, 
        reason: Reason = None
    ):
        """kick_help"""
        await Kick.run(self, ctx, users, reason)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(
        self, 
        ctx, 
        users: commands.Greedy[DiscordUser], 
        *, 
        reason: Reason = None
    ):
        """ban_help"""
        await Ban.run(self, ctx, users, reason)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def softban(
        self, 
        ctx, 
        users: commands.Greedy[DiscordUser], 
        *, 
        reason: Reason = None
    ):
        """softban_help"""
        await Softban.run(self, ctx, users, reason)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def forceban(
        self, 
        ctx, 
        users: commands.Greedy[DiscordUser], 
        *, 
        reason: Reason = None
    ):
        """forceban_help"""
        await Forceban.run(self, ctx, users, reason)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def mute(
        self, 
        ctx, 
        user: discord.Member,
        length: Duration, 
        *, 
        reason: Reason = None
    ):
        """mute_help"""
        await Mute.run(self, ctx, user, length, reason)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unmute(
        self, 
        ctx, 
        user: DiscordUser,
    ):
        """unmute_help"""
        await Unmute.run(self, ctx, user)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(
        self, 
        ctx, 
        user: DiscordUser,
        *,
        reason: Reason = None
    ):
        """unban_help"""
        await Unban.run(self, ctx, user, reason)



    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(
        self,
        ctx,
        amount: int = None
    ):
        """purge_help"""
        await Clean.run(self, ctx, amount)


    @commands.group()
    @commands.has_guild_permissions(manage_messages=True)
    async def clean(
        self,
        ctx,
    ):
        """clean_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="clean")
            

    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def bots(
        self,
        ctx,
        amount: int = None
    ):
        """clean_bots_help"""
        await CleanBots.run(self, ctx, amount)


    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def user(
        self,
        ctx,
        users: commands.Greedy[DiscordUser],
        amount: int = None
    ):
        """clean_user_help"""
        await CleanUser.run(self, ctx, users, amount)


    @clean.command(usage="clean last <duration>")
    @commands.has_guild_permissions(manage_messages=True)
    async def last(
        self,
        ctx,
        duration: Duration,
        excess = ""
    ):
        """clean_last_help"""
        await CleanLast.run(self, ctx, duration, excess)


    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def until(
        self,
        ctx,
        message: discord.Message
    ):
        """clean_until_help"""
        await CleanUntil.run(self, ctx, message)


    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def between(
        self,
        ctx,
        start: discord.Message,
        end: discord.Message
    ):
        """clean_between_help"""
        await CleanBetween.run(self, ctx, start, end)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def cybernuke(
        self, 
        ctx, 
        join: Duration,
        age: Duration
    ):
        """cybernuke_help"""
        await CyberNuke.run(self, ctx, join, age)


def setup(bot):
    pass