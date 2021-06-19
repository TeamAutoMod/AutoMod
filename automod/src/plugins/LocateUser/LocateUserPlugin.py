import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from ..Types import DiscordUserID
from .commands import Follow, FollowDelete, Follows, Where
from .events import OnVoiceStateUpdate



class LocateUserPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)

    
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.kick_members


    @commands.command(aliases=["f"])
    async def follow(
        self, 
        ctx,
        user_id: DiscordUserID
    ):
        """follow_help"""
        await Follow.run(self, ctx, user_id)


    @commands.group(aliases=["fs"])
    async def follows(
        self, 
        ctx
    ):
        """follows_help"""
        if ctx.subcommand_passed is None:
            await Follows.run(self, ctx)


    @follows.command(aliases=["d"])
    async def delete(
        self, 
        ctx,
        user_id: DiscordUserID
    ):
        """follows_delete_help"""
        await FollowDelete.run(self, ctx, user_id)


    @commands.command(aliases=["w"])
    async def where(
        self, 
        ctx,
        user: discord.Member
    ):
        """where_help"""
        await Where.run(self, ctx, user)


    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):
        await OnVoiceStateUpdate.run(self, member, before, after)




def setup(bot):
    pass