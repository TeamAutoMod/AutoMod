from typing import Union
import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .events import OnMessage, OnMessageEdit, OnMemberJoin
from .commands import AntiCaps, AntiEveryone, AntiFiles, AntiInvite, AntiZalgo, AutoRaid, MaxLines, MaxMentions, AntiSpam, Ignore, Unignore, \
RaidMode, AllowedInvites, AllowedInvitesAdd, AllowedInvitesRemove
from ..Types import Reason



class AutomodPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.last_joiners = dict()
        self.raids = dict()


    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator


    @commands.Cog.listener()
    async def on_message(
        self, 
        message
    ):
        await OnMessage.run(self, message)

    
    @commands.Cog.listener()
    async def on_message_edit(
        self, 
        before, 
        after
    ):
        await OnMessageEdit.run(self, before, after)


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):
        await OnMemberJoin.run(self, member)


    @commands.command()
    async def antiinvite(
        self, 
        ctx,
        warns: int
    ):
        """antiinvite_help"""
        await AntiInvite.run(self, ctx, warns)


    @commands.command()
    async def antieveryone(
        self, 
        ctx,
        warns: int
    ):
        """antieveryone_help"""
        await AntiEveryone.run(self, ctx, warns)


    @commands.command()
    async def anticaps(
        self, 
        ctx,
        warns: int
    ):
        """anticaps_help"""
        await AntiCaps.run(self, ctx, warns)


    @commands.command()
    async def antifiles(
        self, 
        ctx,
        warns: int
    ):
        """antifiles_help"""
        await AntiFiles.run(self, ctx, warns)


    @commands.command()
    async def antizalgo(
        self, 
        ctx,
        warns: int
    ):
        """antizalgo_help"""
        await AntiZalgo.run(self, ctx, warns)


    @commands.command()
    async def maxmentions(
        self, 
        ctx,
        mentions: int
    ):
        """maxmentions_help"""
        await MaxMentions.run(self, ctx, mentions)


    @commands.command()
    async def maxlines(
        self, 
        ctx,
        lines: int
    ):
        """maxlines_help"""
        await MaxLines.run(self, ctx, lines)


    @commands.command()
    async def autoraid(
        self, 
        ctx,
        threshold: str
    ):
        """autoraid_help"""
        await AutoRaid.run(self, ctx, threshold)


    @commands.command()
    async def antispam(
        self, 
        ctx,
        warns: str
    ):
        """antispam_help"""
        await AntiSpam.run(self, ctx, warns)

    
    @commands.command()
    async def ignore(
        self, 
        ctx,
        role_or_channel: Union[discord.Role, discord.TextChannel] = None
    ):
        """ignore_help"""
        await Ignore.run(self, ctx, role_or_channel)


    @commands.command()
    async def unignore(
        self, 
        ctx,
        role_or_channel: Union[discord.Role, discord.TextChannel]
    ):
        """unignore_help"""
        await Unignore.run(self, ctx, role_or_channel)

    
    @commands.command()
    async def raidmode(
        self,
        ctx,
        state,
        *,
        reason: Reason = None
    ):
        """raidmode_help"""
        await RaidMode.run(self, ctx, state, reason)


    @commands.group()
    async def allowed_invites(
        self,
        ctx
    ):
        """allowed_invites_help"""
        if ctx.subcommand_passed is None:
            await AllowedInvites.run(self, ctx)

    
    @allowed_invites.command()
    async def add(
        self,
        ctx,
        guild_id: int
    ):
        """allowed_invites_add_help"""
        await AllowedInvitesAdd.run(self, ctx, guild_id)


    @allowed_invites.command()
    async def remove(
        self,
        ctx,
        guild_id: int
    ): 
        """allowed_invites_remove_help"""
        await AllowedInvitesRemove.run(self, ctx, guild_id)






def setup(bot):
    pass