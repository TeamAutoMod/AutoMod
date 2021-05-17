import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from ..Types import Reason, DiscordUser, Duration
from .commands import Warn, Ban, Softban, Cleanban, Forceban, Mute, Unmute, Massban, Masskick, Unban, Kick


class ModerationPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(
        self, 
        ctx, 
        user: discord.Member, 
        *, 
        reason: Reason = None
    ):
        """warn_help"""
        await Warn.run(self, ctx, user, reason)

    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def kick(
        self, 
        ctx, 
        user: discord.Member, 
        *, 
        reason: Reason = None
    ):
        """kick_help"""
        await Kick.run(self, ctx, user, reason)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, 
        ctx, 
        user: DiscordUser, 
        *, 
        reason: Reason = None
    ):
        """ban_help"""
        await Ban.run(self, ctx, user, reason)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(
        self, 
        ctx, 
        user: DiscordUser, 
        *, 
        reason: Reason = None
    ):
        """softban_help"""
        await Softban.run(self, ctx, user, reason)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def cleanban(
        self, 
        ctx, 
        user: DiscordUser, 
        *, 
        reason: Reason = None
    ):
        """cleanban_help"""
        await Cleanban.run(self, ctx, user, reason)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def forceban(
        self, 
        ctx, 
        user: DiscordUser, 
        *, 
        reason: Reason = None
    ):
        """forceban_help"""
        await Forceban.run(self, ctx, user, reason)


    @commands.command()
    @commands.has_permissions(ban_members=True)
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
    @commands.has_permissions(ban_members=True)
    async def unmute(
        self, 
        ctx, 
        user: DiscordUser,
    ):
        """unmute_help"""
        await Unmute.run(self, ctx, user)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(
        self, 
        ctx, 
        user: DiscordUser,
        *,
        reason: Reason = None
    ):
        """unban_help"""
        await Unban.run(self, ctx, user, reason)


    @commands.command(aliases=["mban"])
    @commands.has_permissions(ban_members=True)
    async def massban(
        self, 
        ctx, 
        targets: commands.Greedy[DiscordUser],
        *,
        reason: Reason = None
    ):
        """mban_help"""
        await Massban.run(self, ctx, targets, reason)


    @commands.command(aliases=["mkick"])
    @commands.has_permissions(kick_members=True)
    async def masskick(
        self, 
        ctx, 
        targets: commands.Greedy[DiscordUser],
        *,
        reason: Reason = None
    ):
        """mkick_help"""
        await Masskick.run(self, ctx, targets, reason)




def setup(bot):
    pass