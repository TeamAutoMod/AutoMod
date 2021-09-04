from typing import Union
import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .events import (
    OnMessage, 
    OnMessageEdit, 
    OnMemberJoin
)
from .commands import (
    Caps, 
    Everyone, 
    Files, 
    Invite, 
    Zalgo, 
    Raid, 
    Lines, 
    Mentions, 
    Spam, 
    Ignore, 
    Unignore,
    RaidMode, 
    AllowedInvites, 
    AllowedInvitesAdd, 
    AllowedInvitesRemove
)
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


    @commands.group()
    async def automod(
        self,
        ctx
    ): 
        """automod_help"""
        if ctx.invoked_subcommand is None:
            _help = self.bot.get_command("help")
            await _help.__call__(ctx, query="automod")


    @automod.command()
    async def invite(
        self, 
        ctx,
        warns: str
    ):
        """invite_help"""
        await Invite.run(self, ctx, warns)


    @automod.command()
    async def everyone(
        self, 
        ctx,
        warns: str
    ):
        """everyone_help"""
        await Everyone.run(self, ctx, warns)


    @automod.command()
    async def caps(
        self, 
        ctx,
        warns: str
    ):
        """caps_help"""
        await Caps.run(self, ctx, warns)


    @automod.command()
    async def files(
        self, 
        ctx,
        warns: str
    ):
        """files_help"""
        await Files.run(self, ctx, warns)


    @automod.command()
    async def zalgo(
        self, 
        ctx,
        warns: str
    ):
        """zalgo_help"""
        await Zalgo.run(self, ctx, warns)


    @automod.command()
    async def mentions(
        self, 
        ctx,
        mentions: str
    ):
        """mentions_help"""
        await Mentions.run(self, ctx, mentions)


    @automod.command()
    async def lines(
        self, 
        ctx,
        lines: str
    ):
        """lines_help"""
        await Lines.run(self, ctx, lines)


    @automod.command()
    async def raid(
        self, 
        ctx,
        threshold: str
    ):
        """raid_help"""
        await Raid.run(self, ctx, threshold)


    @automod.command()
    async def spam(
        self, 
        ctx,
        warns: str
    ):
        """spam_help"""
        await Spam.run(self, ctx, warns)

    
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