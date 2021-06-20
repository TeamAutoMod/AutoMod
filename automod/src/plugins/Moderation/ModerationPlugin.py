import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from ..Types import Reason, DiscordUser, Duration
from .commands import Ban, Softban, Forceban, Mute, Unmute, Unban, Kick, Clean
from .functions.UnmuteTask import unmuteTask


class ModerationPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.loop.create_task(unmuteTask(self.bot))

    
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
    async def clean(
        self,
        ctx,
        amount: int = None
    ):
        """clean_help"""
        await Clean.run(self, ctx, amount)





def setup(bot):
    pass