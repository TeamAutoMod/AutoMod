import discord
from discord.ext import commands

import datetime
import asyncio
import logging; log = logging.getLogger()

from .warn import WarnPlugin
from .processor import LogProcessor, ActionProcessor
from ..types import DiscordUser, Duration, Embed
from ..views import ConfirmView
from ..schemas import Mute



ACTIONS = {
    "ban": {
        "action": "ban",
        "log": "banned"
    },
    "softban": {
        "action": "ban",
        "log": "softbanned"
    },
    "hackban": {
        "action": "ban",
        "log": "hackbanned"
    },
    "kick": {
        "action": "kick",
        "log": "kicked"
    },
}


class ModerationPlugin(WarnPlugin):
    """Plugin for all moderation commands"""
    def __init__(self, bot):
        super().__init__(bot)
        self.log_processor = LogProcessor(bot)
        self.action_processor = ActionProcessor(bot)
        self.bot.loop.create_task(self.handle_unmutes())


    async def handle_unmutes(self):
        while True:
            await asyncio.sleep(10)
            if len(list(self.bot.db.mutes.find({}))) > 0:
                for mute in self.bot.db.mutes.find():
                    if "until" in mute:
                        ending = mute["until"]
                    else:
                        ending = mute["ending"]

                    if ending < datetime.datetime.utcnow():
                        guild = self.bot.get_guild(int(mute["id"].split("-")[0]))
                        if guild != None:

                            t = guild.get_member(int(mute["id"].split("-")[1]))
                            if t == None:
                                t = "Unknown#0000"

                            await self.log_processor.execute(guild, "unmute", **{
                                "user": t,
                                "user_id": int(mute["id"].split("-")[1]),
                                "mod": guild.get_member(self.bot.user.id),
                                "mod_id": self.bot.user.id
                            })
                        self.bot.db.mutes.delete(mute["id"])

    
    async def clean_messages(self, ctx, amount, check, before=None, after=None):
        try:
            d = await ctx.channel.purge(
                limit=amount,
                check=check,
                before=before,
                after=after
            )
        except discord.Forbidden:
            raise
        except discord.NotFound:
            await asyncio.sleep(1); return self.locale.t(ctx.guild, "alr_cleaned", _emote="NO"), {}
        else:
            try:
                await ctx.message.delete()
            except discord.NotFound:
                pass
            finally:
               return self.locale.t(ctx.guild, "cleaned", _emote="YES", amount=len(d), plural="" if len(d) == 1 else "s"), {"delete_after": 5}


    async def kick_or_ban(self, action, ctx, user, reason, **extra_kwargs):
        if action != "hackban":
            if ctx.guild.get_member(user.id) == None:
                return await ctx.send(self.locale.t(ctx.guild, "not_in_server", _emote="NO"))
        if not await self.can_act(ctx.guild, ctx.author, user):
            return await ctx.send(self.locale.t(ctx.guild, "cant_act", _emote="NO"))
        try:
            func = getattr(ctx.guild, ACTIONS[action]["action"])
            await func(user=user, reason=reason)
        except Exception as ex:
            await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
        else:
            if action == "softban":
                try:
                    await ctx.guild.unban(user=user)
                except Exception as ex:
                    await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
                else:
                    self.bot.ignore_for_events.append(user.id)
                    await ctx.send(self.locale.t(ctx.guild, "softbanned", _emote="YES"))
            
            await self.log_processor.execute(ctx.guild, action, **{
                "user": user,
                "user_id": user.id,
                "mod": ctx.author,
                "mod_id": ctx.author.id,
                "reason": reason,
                "case": self.action_processor.new_case(action, ctx.message, ctx.author, user, reason)
            })
            await ctx.send(self.locale.t(ctx.guild, ACTIONS[action]["log"], _emote="YES"))


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: DiscordUser, *, reason: str = None):
        """ban_help"""
        if reason == None: self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await self.kick_or_ban("ban", ctx, user, reason, delete_message_days=1)
        else:
            await ctx.send(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))

    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: DiscordUser, *, reason: str = None):
        """unban_help"""
        if reason == None: self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await ctx.send(self.locale.t(ctx.guild, "not_banned", _emote="WARN"))
        else:
            try:
                await ctx.guild.unban(user=user, reason=reason)
            except Exception as ex:
                await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
            else:
                self.bot.ignore_for_events.append(user.id)
                await self.log_processor.execute(ctx.guild, "unban", **{
                    "user": user,
                    "user_id": user.id,
                    "mod": ctx.author,
                    "mod_id": ctx.author.id,
                    "reason": reason
                })

                await ctx.send(self.locale.t(ctx.guild, "unbanned", _emote="YES"))


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, user: DiscordUser, *, reason: str = None):
        """softban_help"""
        if reason == None: self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await self.kick_or_ban("softban", ctx, user, reason, delete_message_days=1)
        else:
            await ctx.send(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))


    @commands.command(aliases=["forceban"])
    @commands.has_permissions(ban_members=True)
    async def hackban(self, ctx, user: DiscordUser, *, reason: str = None):
        """hackban_help"""
        if reason == None: self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            return await ctx.send(self.locale.t(ctx.guild, "not_banned", _emote="NO"))
        else:
            await self.kick_or_ban("hackban", ctx, user, reason, delete_message_days=1)


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: DiscordUser, *, reason: str = None):
        """kick_help"""
        if reason == None: self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await self.kick_or_ban("kick", ctx, user, reason, delete_message_days=1)
        else:
            await ctx.send(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))


    @commands.command(aliases=["timeout"])
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member, length: Duration, *, reason: str = None):
        """mute_help"""
        if reason == None: self.locale.t(ctx.guild, "no_reason")
        if length.unit == None: length.unit = "m"

        if not await self.can_act(ctx.guild, ctx.author, user):
            return await ctx.send(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == False: 
                return await ctx.send(self.locale.t(ctx.guild, "no_timeout_perms", _emote="NO"))

        _id = f"{ctx.guild.id}-{user.id}"
        if self.db.mutes.exists(_id):

            async def confirm(i):
                until = (self.db.mutes.get(_id, "until") + datetime.timedelta(seconds=length.to_seconds(ctx)))
                self.db.mutes.update(_id, "until", until)

                await i.response.edit_message(
                    content=self.locale.t(ctx.guild, "mute_extended", _emote="YES", until=f"<t:{round(until.timestamp())}>"), 
                    embed=None, 
                    view=None
                )
                await self.log_processor.execute(ctx.guild, "mute_extended", **{
                    "mod": ctx.author, 
                    "mod_id": ctx.author.id,
                    "user": user,
                    "user_id": user.id,
                    "until": f"<t:{round(until.timestamp())}>",
                    "reason": reason
                })
                self.bot.handle_timeout(True, ctx.guild, user, until.isoformat())
                return

            async def cancel(i):
                e = Embed(
                    description=self.locale.t(ctx.guild, "aborting")
                )
                await i.response.edit_message(embed=e, view=None)

            async def timeout():
                if message is not None:
                    e = Embed(
                        description=self.locale.t(ctx.guild, "aborting")
                    )
                    await message.edit(embed=e, view=None)

            def check(i):
                return i.user.id == ctx.author.id and i.message.id == message.id

            e = Embed(
                description=self.locale.t(ctx.guild, "already_muted_description")
            )
            message = await ctx.send(embed=e, view=ConfirmView(ctx.guild.id, on_confirm=confirm, on_cancel=cancel, on_timeout=timeout,check=check))
        else:
            seconds = length.to_seconds(ctx)
            if seconds >= 1:
                until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))
                exc = self.bot.handle_timeout(True, ctx.guild, user, until.isoformat())
                if exc != "":
                    await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=exc))
                else:
                    self.db.mutes.insert(Mute(ctx.guild.id, user.id, until))

                    await self.log_processor.execute(ctx.guild, "mute", **{
                        "mod": ctx.author, 
                        "mod_id": ctx.author.id,
                        "user": user,
                        "user_id": user.id,
                        "until": f"<t:{round(until.timestamp())}>",
                        "case": self.action_processor.new_case("mute", ctx.message, ctx.author, user, reason),
                        "reason": reason
                    }) 

                    await ctx.send(self.locale.t(ctx.guild, "muted", _emote="YES"))
            else:
                raise commands.BadArgument("number_too_small")


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, user: discord.Member):
        """unmute_help"""
        _id = f"{ctx.guild.id}-{user.id}"
        if not self.db.mutes.exists(_id):
            return await ctx.send(self.locale.t(ctx.guild, "not_muted", _emote="NO"))

        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == False: 
                return await ctx.send(self.locale.t(ctx.guild, "no_timeout_perms", _emote="NO"))

        exc = self.bot.handle_timeout(False, ctx.guild, user, None)
        if exc != "":
            await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=exc))
        else:
            self.db.mutes.delete(_id)
            await self.log_processor.execute(ctx.guild, "manual_unmute", **{
                "mod": ctx.author, 
                "mod_id": ctx.author.id,
                "user": user,
                "user_id": user.id,
            }) 

            await ctx.send(self.locale.t(ctx.guild, "unmuted", _emote="YES"))


    @commands.group(aliases=["clear", "purge"])
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx):
        """clean_help"""
        if ctx.invoked_subcommand == None:
            cmd = self.bot.get_command("help")
            await cmd.__call__(
                ctx,
                query="clean"
            )


    @clean.command()
    @commands.has_permissions(manage_messages=True)
    async def all(self, ctx, amount: int = 10):
        """clean_all_help"""
        if amount < 1: return await ctx.send(self.locale.t(ctx.guild, "amount_too_small", _emote="NO"))
        if amount > 300: return await ctx.send(self.locale.t(ctx.guild, "amount_too_big", _emote="NO"))

        msg, kwargs = await self.clean_messages(
            ctx,
            amount,
            lambda m: True
        )
        await ctx.send(msg, **kwargs)


    @clean.command()
    @commands.has_permissions(manage_messages=True)
    async def user(self, ctx, user: discord.Member, amount: int = 10):
        """clean_user_help"""
        if amount < 1: return await ctx.send(self.locale.t(ctx.guild, "amount_too_small", _emote="NO"))
        if amount > 300: return await ctx.send(self.locale.t(ctx.guild, "amount_too_big", _emote="NO"))

        msg, kwargs = await self.clean_messages(
            ctx,
            amount,
            lambda m: m.author.id == user.id
        )
        await ctx.send(msg, **kwargs)




def setup(bot): bot.register_plugin(ModerationPlugin(bot))
