import discord
from discord.ext import commands

import logging; log = logging.getLogger()

from . import AutoModPlugin
from .processor import ActionProcessor, LogProcessor



class WarnPlugin(AutoModPlugin):
    """Plugin for warn commands. This isn't being added seperately, instead the mod plugin will subclass from this"""
    def __init__(self, bot):
        super().__init__(bot)
        self.action_processor = ActionProcessor(bot)
        self.log_processor = LogProcessor(bot)


    async def can_act(self, guild, mod, target):
        if not guild.chunked: await guild.chunk(cache=True)
        mod = guild.get_member(mod.id)
        target = guild.get_member(target.id)
        return mod.id != target.id \
            and target.id != guild.owner.id \
            and mod.top_role > target.top_role


    @commands.command()
    @AutoModPlugin.can("kick_members")
    async def warn(self, ctx, user: discord.Member, warns = None, *, reason: str = None):
        """warn_help"""
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")

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

        if not await self.can_act(ctx.guild, ctx.author, user):
            return await ctx.send(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

        exc = await self.action_processor.execute(ctx.message, ctx.author, user, warns, reason)
        if exc != None:
            await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=exc))
        else:
            await ctx.send(self.locale.t(ctx.guild, "warned", _emote="YES"))


    @commands.command(aliases=["pardon"])
    @AutoModPlugin.can("kick_members")
    async def unwarn(self, ctx, user: discord.Member, warns = None, *, reason: str = None):
        """unwarn_help"""
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")

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

        if not await self.can_act(ctx.guild, ctx.author, user):
            return await ctx.send(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

        _id = f"{ctx.guild.id}-{user.id}"
        if not self.db.warns.exists(_id):
            await ctx.send(self.locale.t(ctx.guild, "no_warns", _emote="NO"))
        else:
            cur = self.db.warns.get(_id, "warns")
            if cur < 1: 
                await ctx.send(self.locale.t(ctx.guild, "no_warns", _emote="NO"))
            else:
                new = (cur - warns) if (cur - warns) >= 0 else 0
                self.db.warns.update(_id, "warns", new)

                await self.log_processor.execute(ctx.guild, "unwarn", **{
                    "user": user,
                    "user_id": user.id,
                    "mod": ctx.author,
                    "mod_id": ctx.author.id,
                    "reason": reason,
                    "old_warns": cur,
                    "new_warns": new
                })
                await ctx.send(self.locale.t(ctx.guild, "unwarned", _emote="YES"))