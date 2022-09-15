# type: ignore

import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from typing import Union

from .. import AutoModPluginBlueprint, ShardedBotInstance
from .._processor import ActionProcessor, LogProcessor
from ...types import E



class WarnPlugin(AutoModPluginBlueprint):
    """Plugin for warn commands. This isn't being added seperately, instead the mod plugin will subclass from this"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self.action_processor = ActionProcessor(bot)
        self.log_processor = LogProcessor(bot)


    def can_act(
        self, 
        guild: discord.Guild, 
        mod: discord.Member, 
        target: Union[
            discord.Member, 
            discord.User
        ]
    ) -> bool:
        if mod.id == target.id: return False
        if mod.id == guild.owner_id: return True

        mod = guild.get_member(mod.id)
        target = guild.get_member(target.id)

        if mod != None and target != None:
            rid = self.bot.db.configs.get(guild.id, "mod_role")
            if rid != "":
                if int(rid) in [x.id for x in target.roles]: return False

            return mod.id != target.id \
                and mod.top_role > target.top_role \
                and target.id != guild.owner.id \
                and (
                    target.guild_permissions.ban_members == False 
                    or target.guild_permissions.kick_members == False 
                    or target.guild_permissions.manage_messages == False
                )
        else:
            return True


    @discord.app_commands.command(
        name="warn",
        description="🚩 Warns the user"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def warn(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member, 
        warns: int = 1, 
        reason: str = None
    ) -> None:
        """
        warn_help
        examples:
        -warn @paul#0009
        -warn @paul#0009 Warned you once now
        -warn @paul#0009 3 Warned you three times
        -warn 543056846601191508 
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        if not ctx.guild.chunked: await self.bot.chunk_guild(ctx.guild)

        if warns == None: warns = 1
        if warns < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_warns", _emote="NO"), 0))
        if warns > 100: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_warns", _emote="NO"), 0))

        if not self.can_act(ctx.guild, ctx.user, user):
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "cant_act", _emote="NO"), 0))

        exc = await self.action_processor.execute(ctx, ctx.user, user, warns, reason)
        if exc != None:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=exc), 0))
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "warned", _emote="YES", user=user, reason=reason), 1))


    @discord.app_commands.command(
        name="unwarn",
        description="😇 Unwarns the user"
    )
    @discord.app_commands.default_permissions(ban_members=True)
    async def unwarn(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member, 
        warns: int = 1, 
        reason: str = None
    ) -> None:
        """
        unwarn_help
        examples:
        -unwarn @paul#0009
        -unwarn @paul#0009 Removed one of your warns
        -unwarn @paul#0009 3 Removed three of your warns
        -unwarn 543056846601191508 
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        if not ctx.guild.chunked: await self.bot.chunk_guild(ctx.guild)

        if warns == None: warns = 1
        if warns < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_warns", _emote="NO"), 0))
        if warns > 100: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_warns", _emote="NO"), 0))

        if not self.can_act(ctx.guild, ctx.user, user):
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "cant_act", _emote="NO"), 0))

        _id = f"{ctx.guild.id}-{user.id}"
        if not self.db.warns.exists(_id):
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_warns", _emote="NO"), 0))
        else:
            cur = self.db.warns.get(_id, "warns")
            if cur < 1: 
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_warns", _emote="NO"), 0))
            else:
                new = max(0, cur - warns)
                self.db.warns.update(_id, "warns", new)

                await self.log_processor.execute(ctx.guild, "unwarn", **{
                    "user": user,
                    "user_id": user.id,
                    "mod": ctx.user,
                    "mod_id": ctx.user.id,
                    "reason": reason,
                    "old_warns": cur,
                    "new_warns": new,
                    "channel_id": ctx.channel.id,
                    "case": self.action_processor.new_case("unwarn", ctx, ctx.user, user, reason, warns_added=warns)
                })
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "unwarned", _emote="YES", user=user, reason=reason ), 1))