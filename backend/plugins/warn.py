import discord
from discord.ext import commands

import datetime
import logging; log = logging.getLogger()

from . import AutoModPlugin
from .processor import ActionProcessor, LogProcessor
from ..schemas import Case



class WarnPlugin(AutoModPlugin):
    """Plugin for warn commands. This isn't being added seperately, instead the mod plugin will subclass from this"""
    def __init__(self, bot):
        super().__init__(bot)
        self.action_processor = ActionProcessor(bot)
        self.log_processor = LogProcessor(bot)


    def can_act(self, guild, mod, target):
        mod = guild.get_member(mod.id)
        target = guild.get_member(target.id)

        if mod != None and target != None:
            rid = self.bot.db.configs.get(guild.id, "mod_role")
            if rid != "":
                if int(rid) in [x.id for x in target.roles]: return False

            return mod.id != target.id \
                and mod.top_role > target.top_role \
                and target.id != guild.owner.id \
                and (target.guild_permissions.kick_members == False or target.guild_permissions.kick_members == False)
        else:
            return True


    @commands.command()
    @AutoModPlugin.can("kick_members")
    async def warn(self, ctx, user: discord.Member, warns = None, *, reason: str = None):
        """
        warn_help
        examples:
        -warn @paul#0009
        -warn @paul#0009 Warned you once now
        -warn @paul#0009 3 Warned you three times
        -warn 543056846601191508 
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        if not ctx.guild.chunked: await ctx.guild.chunk(cache=True)

        if warns == None:
            warns = 1
        else:
            try:
                warns = int(warns)
            except ValueError:
                reason = " ".join(ctx.message.content.split(" ")[2:])
                warns = 1
        
        if warns < 1: return await ctx.send(self.locale.t(ctx.guild, "min_warns", _emote="NO"))
        if warns > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

        if not self.can_act(ctx.guild, ctx.author, user):
            return await ctx.send(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

        exc = await self.action_processor.execute(ctx.message, ctx.author, user, warns, reason)
        if exc != None:
            await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=exc))
        else:
            await ctx.send(self.locale.t(ctx.guild, "warned", _emote="YES"))


    @commands.command(aliases=["pardon"])
    @AutoModPlugin.can("kick_members")
    async def unwarn(self, ctx, user: discord.Member, warns = None, *, reason: str = None):
        """
        unwarn_help
        examples:
        -unwarn @paul#0009
        -unwarn @paul#0009 Removed one of your warns
        -unwarn @paul#0009 3 Removed three of your warns
        -unwarn 543056846601191508 
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        if not ctx.guild.chunked: await ctx.guild.chunk(cache=True)

        if warns == None:
            warns = 1
        else:
            try:
                warns = int(warns)
            except ValueError:
                reason = " ".join(ctx.message.content.split(" ")[2:])
                warns = 1

        if warns < 1: return await ctx.send(self.locale.t(ctx.guild, "min_warns", _emote="NO"))
        if warns > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

        if not self.can_act(ctx.guild, ctx.author, user):
            return await ctx.send(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

        _id = f"{ctx.guild.id}-{user.id}"
        if not self.db.warns.exists(_id):
            await ctx.send(self.locale.t(ctx.guild, "no_warns", _emote="NO"))
        else:
            cur = self.db.warns.get(_id, "warns")
            if cur < 1: 
                await ctx.send(self.locale.t(ctx.guild, "no_warns", _emote="NO"))
            else:
                new = max(0, cur - warns)
                self.db.warns.update(_id, "warns", new)

                await self.log_processor.execute(ctx.guild, "unwarn", **{
                    "user": user,
                    "user_id": user.id,
                    "mod": ctx.author,
                    "mod_id": ctx.author.id,
                    "reason": reason,
                    "old_warns": cur,
                    "new_warns": new,
                    "case": self.action_processor.new_case("unwarn", ctx.message, ctx.author, user, reason)
                })
                await ctx.send(self.locale.t(ctx.guild, "unwarned", _emote="YES"))