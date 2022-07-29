from multiprocessing import managers
import discord
from discord.ext import commands

import datetime
import asyncio
import logging; log = logging.getLogger()
import datetime
from typing import Union, Callable

from ..warn.plugin import WarnPlugin, ShardedBotInstance
from .._processor import LogProcessor, ActionProcessor, DMProcessor
from ...types import DiscordUser, Duration, Embed
from ...views import ConfirmView, ActionedView
from ...schemas import Mute, Tempban



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
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self.log_processor = LogProcessor(bot)
        self.action_processor = ActionProcessor(bot)
        self.dm_processor = DMProcessor(bot)
        for f in ["unmutes", "unbans"]: self.bot.loop.create_task((getattr(self, f"handle_{f}"))())


    async def handle_unmutes(
        self
    ) -> None:
        while True:
            await asyncio.sleep(10)
            if len(list(self.db.mutes.find({}))) > 0:
                for mute in self.db.mutes.find():
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
                                "mod_id": self.bot.user.id,
                                "reason": "Mute expired, automated by AutoMod"
                            })
                        self.db.mutes.delete(mute["id"])


    async def handle_unbans(
        self
    ) -> None:
        while True:
            await asyncio.sleep(10)
            if len(list(self.db.tbans.find({}))) > 0:
                for ban in self.db.tbans.find():
                    if "until" in ban:
                        ending = ban["until"]
                    else:
                        ending = ban["ending"]

                    if ending < datetime.datetime.utcnow():
                        guild = self.bot.get_guild(int(ban["id"].split("-")[0]))
                        if guild != None:

                            t = guild.get_member(int(ban["id"].split("-")[1]))
                            if t == None:
                                t = "Unknown#0000"
                            else:
                                try:
                                    await guild.unban(user=t, reason="Tempban expired, automated by AutoMod")
                                except Exception:
                                    pass
                                else:
                                    self.bot.ignore_for_events.append(t.id)
                                
                            await self.log_processor.execute(guild, "tempunban", **{
                                "user": t,
                                "user_id": int(ban["id"].split("-")[1]),
                                "mod": guild.get_member(self.bot.user.id),
                                "mod_id": self.bot.user.id,
                                "reason": "Tempban expired, automated by AutoMod"
                            })
                        self.db.tbans.delete(ban["id"])


    async def clean_messages(
        self, 
        ctx: discord.Interaction, 
        amount: int, 
        check: Callable, 
        before: Union[
            datetime.datetime, 
            discord.Message
        ] = None, 
        after: Union[
            datetime.datetime, 
            discord.Message
        ] = None
    ) -> Union[
        str, 
        Exception
    ]:
        try:
            d = await ctx.channel.purge(
                limit=amount,
                check=check,
                before=before if before != None else ctx.message,
                after=after
            )
        except discord.Forbidden as ex:
            return self.error(ctx, ex)
        except discord.NotFound:
            await asyncio.sleep(1); return self.locale.t(ctx.guild, "alr_cleaned", _emote="NO"), {}
        else:
            if len(d) < 1:
                return self.locale.t(ctx.guild, "no_messages_found", _emote="NO"), {}
            else:
                try:
                    await ctx.message.delete()
                except discord.NotFound:
                    pass
                finally:
                    return self.locale.t(ctx.guild, "cleaned", _emote="YES", amount=len(d), plural="" if len(d) == 1 else "s"), {}


    async def kick_or_ban(
        self, 
        action: str, 
        ctx: discord.Interaction, 
        user: Union[
            discord.Member, 
            discord.User
        ], 
        reason: str, 
        **extra_kwargs
    ) -> None:
        if not ctx.guild.chunked: await self.bot.chunk_guild(ctx.guild)

        if action != "hackban":
            if ctx.guild.get_member(user.id) == None:
                return await ctx.response.send_message(self.locale.t(ctx.guild, "not_in_server", _emote="NO"))

        if not self.can_act(ctx.guild, ctx.user, user):
            return await ctx.response.send_message(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

        try:
            func = getattr(ctx.guild, ACTIONS[action]["action"])
            await func(user=user, reason=reason)
        except Exception as ex:
            await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
        else:
            self.bot.ignore_for_events.append(user.id)
            self.dm_processor.execute(
                ctx,
                "ban",
                user,
                **{
                    "guild_name": ctx.guild.name,
                    "reason": reason,
                    "_emote": "HAMMER"
                }
            )
            if action == "softban":
                try:
                    await ctx.guild.unban(user=user)
                except Exception as ex:
                    await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
                else:
                    self.bot.ignore_for_events.append(user.id)
                    await ctx.response.send_message(self.locale.t(ctx.guild, "softbanned", _emote="YES", user=user))
            
            await self.log_processor.execute(ctx.guild, action, **{
                "user": user,
                "user_id": user.id,
                "mod": ctx.user,
                "mod_id": ctx.user.id,
                "reason": reason,
                "channel_id": ctx.channel.id,
                "case": self.action_processor.new_case(action, ctx, ctx.user, user, reason)
            })
            await ctx.response.send_message(self.locale.t(ctx.guild, ACTIONS[action]["log"], _emote="YES", user=user))


    @discord.app_commands.command(
        name="ban",
        description="Bans the user from the server"
    )
    @discord.app_commands.default_permissions(ban_members=True)
    async def ban(
        self, 
        ctx: discord.Interaction,
        user: discord.Member, 
        *, 
        reason: str = None
    ) -> None:
        """
        ban_help
        examples:
        -ban @paul#0009 test
        -ban 543056846601191508
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await self.kick_or_ban("ban", ctx, user, reason, delete_message_days=1)
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))

    
    @discord.app_commands.command(
        name="unban",
        description="Unbans the user from the server"
    )
    @discord.app_commands.default_permissions(ban_members=True)
    async def unban(
        self,
        ctx: discord.Interaction, 
        user: discord.User, 
        *, 
        reason: str = None
    ) -> None:
        """
        unban_help
        examples:
        -unban 543056846601191508
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
    
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await ctx.response.send_message(self.locale.t(ctx.guild, "not_banned", _emote="WARN"))
        else:
            try:
                await ctx.guild.unban(user=user, reason=reason)
            except Exception as ex:
                await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
            else:
                self.bot.ignore_for_events.append(user.id)
                await self.log_processor.execute(ctx.guild, "unban", **{
                    "user": user,
                    "user_id": user.id,
                    "mod": ctx.user,
                    "mod_id": ctx.user.id,
                    "reason": reason,
                    "channel_id": ctx.channel.id,
                    "case": self.action_processor.new_case("unban", ctx, ctx.user, user, reason)
                })

                await ctx.response.send_message(self.locale.t(ctx.guild, "unbanned", _emote="YES", user=user))
            finally:
                if self.db.tbans.exists(f"{ctx.guild.id}-{user.id}"):
                    self.db.tbans.delete(f"{ctx.guild.id}-{user.id}")


    @discord.app_commands.command(
        name="softban",
        description="Softbans the user from the server (ban & unban)"
    )
    @discord.app_commands.default_permissions(ban_members=True)
    async def softban(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member, 
        *, 
        reason: str = None
    ) -> None:
        """
        softban_help
        examples:
        -softban @paul#0009 test
        -softban 543056846601191508
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await self.kick_or_ban("softban", ctx, user, reason, delete_message_days=1)
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))


    @discord.app_commands.command(
        name="forceban",
        description="Bans the user from the server (even if they aren't in the server)"
    )
    @discord.app_commands.default_permissions(ban_members=True)
    async def hackban(
        self, 
        ctx: discord.Interaction, 
        user: discord.User,
        *, 
        reason: str = None
    ) -> None:
        """
        hackban_help
        examples:
        -hackban @paul#0009 test
        -hackban 543056846601191508
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await self.kick_or_ban("hackban", ctx, user, reason, delete_message_days=1)
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))


    @discord.app_commands.command(
        name="tempban",
        description="Temporarily bans the user from the server"
    )
    @discord.app_commands.describe(
        length="10m, 2h, 1d"
    )
    @discord.app_commands.default_permissions(ban_members=True)
    async def tempban(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member, 
        length: str, 
        *, 
        reason: str = None
    ) -> None:
        """
        tempban_help
        examples:
        -tempban @paul#0009 5d test
        -tempban 543056846601191508 7d
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")

        try:
            length = await Duration().convert(ctx, length)
        except Exception as ex:
            return self.error(ctx, ex)
        else:
            if length.unit == None: length.unit = "m"
            if not ctx.guild.chunked: await self.bot.chunk_guild(ctx.guild)

            if not self.can_act(ctx.guild, ctx.user, user):
                return await ctx.response.send_message(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

            try:
                seconds = length.to_seconds(ctx)
            except Exception as ex:
                return self.error(ctx, ex)

            try:
                await ctx.guild.fetch_ban(user)
            except discord.NotFound:
                _id = f"{ctx.guild.id}-{user.id}"
                if self.db.tbans.exists(_id):

                    async def confirm(i):
                        until = (self.db.tbans.get(_id, "until") + datetime.timedelta(seconds=seconds))
                        self.db.tbans.update(_id, "until", until)

                        await i.response.edit_message(
                            content=self.locale.t(ctx.guild, "tempban_extended", _emote="YES", user=user, until=f"<t:{round(until.timestamp())}>"), 
                            embed=None, 
                            view=None
                        )

                        self.dm_processor.execute(
                            ctx,
                            "tempban",
                            user,
                            **{
                                "guild_name": ctx.guild.name,
                                "until": f"<t:{round(until.timestamp())}>",
                                "reason": reason,
                                "_emote": "HAMMER"
                            }
                        )

                        await self.log_processor.execute(ctx.guild, "tempban_extended", **{
                            "mod": ctx.user, 
                            "mod_id": ctx.user.id,
                            "user": user,
                            "user_id": user.id,
                            "until": f"<t:{round(until.timestamp())}>",
                            "reason": reason,
                            "channel_id": ctx.channel.id,
                            "case": self.action_processor.new_case("tempban extended", ctx, ctx.user, user, reason, until=until)
                        })
                        return

                    async def cancel(i):
                        e = Embed(
                            ctx,
                            description=self.locale.t(ctx.guild, "aborting")
                        )
                        await i.response.edit_message(embed=e, view=None)

                    async def timeout():
                        e = Embed(
                            ctx,
                            description=self.locale.t(ctx.guild, "aborting")
                        )
                        try:
                            await ctx.followup.send(embed=e, view=None)
                        except Exception:
                            pass

                    def check(i):
                        return i.user.id == ctx.user.id

                    e = Embed(
                        ctx,
                        description=self.locale.t(ctx.guild, "already_tempbanned_description")
                    )
                    await ctx.response.send_message(embed=e, view=ConfirmView(self.bot, ctx.guild.id, on_confirm=confirm, on_cancel=cancel, on_timeout=timeout,check=check))
                else:
                    if seconds >= 1:
                        try:
                            await ctx.guild.ban(
                                user=user, 
                                reason=f"{reason} | {length}{length.unit}"
                            )
                        except Exception as ex:
                            await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
                        else:
                            self.bot.ignore_for_events.append(user.id)
                            until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))
                            self.db.tbans.insert(Tempban(ctx.guild.id, user.id, until))

                            self.dm_processor.execute(
                                ctx,
                                "tempban",
                                user,
                                **{
                                    "guild_name": ctx.guild.name,
                                    "until": f"<t:{round(until.timestamp())}>",
                                    "reason": reason,
                                    "_emote": "HAMMER"
                                }
                            )

                            await self.log_processor.execute(ctx.guild, "tempban", **{
                                "mod": ctx.user, 
                                "mod_id": ctx.user.id,
                                "user": user,
                                "user_id": user.id,
                                "until": f"<t:{round(until.timestamp())}>",
                                "channel_id": ctx.channel.id,
                                "case": self.action_processor.new_case("tempban", ctx, ctx.user, user, reason, until=until),
                                "reason": reason
                            }) 

                            await ctx.response.send_message(self.locale.t(ctx.guild, "tempbanned", _emote="YES", user=user, until=f"<t:{round(until.timestamp())}>"))
                    else:
                        return self.error(ctx, commands.BadArgument("Number too small"))
            else:
                await ctx.response.send_message(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))


    @discord.app_commands.command(
        name="kick",
        description="Kicks the user from the server"
    )
    @discord.app_commands.default_permissions(kick_members=True)
    async def kick(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member, 
        *, 
        reason: str = None
    ) -> None:
        """
        kick_help
        examples:
        -kick @paul#0009 test
        -kick 543056846601191508
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await self.kick_or_ban("kick", ctx, user, reason, delete_message_days=1)
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "alr_banned", _emote="WARN"))


    @discord.app_commands.command(
        name="mute",
        description="Temporarily mutes the user"
    )
    @discord.app_commands.describe(
        length="10m, 2h, 1d"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def mute(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member, 
        length: str, 
        *, 
        reason: str = None
    ) -> None:
        """
        mute_help
        examples:
        -mute @paul#0009 10m test
        -mute 543056846601191508 1h
        """
        if reason == None: reason = self.locale.t(ctx.guild, "no_reason")

        try:
            length = await Duration().convert(ctx, length)
        except Exception as ex:
            return self.error(ctx, ex)
        else:
            if length.unit == None: length.unit = "m"
            if not ctx.guild.chunked: await self.bot.chunk_guild(ctx.guild)

            if not self.can_act(ctx.guild, ctx.user, user):
                return await ctx.response.send_message(self.locale.t(ctx.guild, "cant_act", _emote="NO"))

            try:
                seconds = length.to_seconds(ctx)
            except Exception as ex:
                return self.error(ctx, ex)

            _id = f"{ctx.guild.id}-{user.id}"
            if self.db.mutes.exists(_id):

                async def confirm(i):
                    until = (self.db.mutes.get(_id, "until") + datetime.timedelta(seconds=seconds))
                    self.db.mutes.update(_id, "until", until)

                    await i.response.edit_message(
                        content=self.locale.t(ctx.guild, "mute_extended", _emote="YES", user=user, until=f"<t:{round(until.timestamp())}>"), 
                        embed=None, 
                        view=None
                    )

                    self.dm_processor.execute(
                        ctx,
                        "mute",
                        user,
                        **{
                            "guild_name": ctx.guild.name,
                            "until": f"<t:{round(until.timestamp())}>",
                            "reason": reason,
                            "_emote": "MUTE"
                        }
                    )

                    await self.log_processor.execute(ctx.guild, "mute_extended", **{
                        "mod": ctx.user, 
                        "mod_id": ctx.user.id,
                        "user": user,
                        "user_id": user.id,
                        "reason": reason,
                        "until": f"<t:{round(until.timestamp())}>",
                        "channel_id": ctx.channel.id,
                        "case": self.action_processor.new_case("mute extended", ctx, ctx.user, user, reason, until=until)
                    })
                    self.bot.handle_timeout(True, ctx.guild, user, until.isoformat())
                    return

                async def cancel(i):
                    e = Embed(
                    ctx,
                        description=self.locale.t(ctx.guild, "aborting")
                    )
                    await i.response.edit_message(embed=e, view=None)

                async def timeout():
                    e = Embed(
                        ctx,
                        description=self.locale.t(ctx.guild, "aborting")
                    )
                    try:
                        await ctx.followup.send(embed=e, view=None)
                    except Exception:
                        pass

                def check(i):
                    return i.user.id == ctx.user.id

                e = Embed(
                    ctx,
                    description=self.locale.t(ctx.guild, "already_muted_description")
                )
                message = await ctx.response.send_message(embed=e, view=ConfirmView(self.bot, ctx.guild.id, on_confirm=confirm, on_cancel=cancel, on_timeout=timeout,check=check))
            else:
                if seconds >= 1:
                    until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))
                    exc = self.bot.handle_timeout(True, ctx.guild, user, until.isoformat())
                    if exc != "":
                        await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=exc))
                    else:
                        self.db.mutes.insert(Mute(ctx.guild.id, user.id, until))

                        self.dm_processor.execute(
                            ctx,
                            "mute",
                            user,
                            **{
                                "guild_name": ctx.guild.name,
                                "until": f"<t:{round(until.timestamp())}>",
                                "reason": reason,
                                "_emote": "MUTE"
                            }
                        )

                        await self.log_processor.execute(ctx.guild, "mute", **{
                            "mod": ctx.user, 
                            "mod_id": ctx.user.id,
                            "user": user,
                            "user_id": user.id,
                            "reason": reason,
                            "until": f"<t:{round(until.timestamp())}>",
                            "channel_id": ctx.channel.id,
                            "case": self.action_processor.new_case("mute", ctx, ctx.user, user, reason, until=until)
                        }) 

                        await ctx.response.send_message(self.locale.t(ctx.guild, "muted", _emote="YES", user=user, until=f"<t:{round(until.timestamp())}>"))
                else:
                    return self.error(ctx, commands.BadArgument("Number too small"))


    @discord.app_commands.command(
        name="unmute",
        description="Unmutes the user"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def unmute(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member
    ) -> None:
        """
        unmute_help
        examples:
        -unmute @paul#0009
        -unmute 543056846601191508
        """
        _id = f"{ctx.guild.id}-{user.id}"
        if not self.db.mutes.exists(_id):
            return await ctx.response.send_message(self.locale.t(ctx.guild, "not_muted", _emote="NO"))

        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == False: 
                return await ctx.response.send_message(self.locale.t(ctx.guild, "no_timeout_perms", _emote="NO"))

        exc = self.bot.handle_timeout(False, ctx.guild, user, None)
        if exc != "":
            await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=exc))
        else:
            self.db.mutes.delete(_id)
            await self.log_processor.execute(ctx.guild, "manual_unmute", **{
                "mod": ctx.user, 
                "mod_id": ctx.user.id,
                "user": user,
                "user_id": user.id,
                "channel_id": ctx.channel.id,
                "case": self.action_processor.new_case("unmute", ctx, ctx.user, user, "Manual unmute")
            }) 

            await ctx.response.send_message(self.locale.t(ctx.guild, "unmuted", _emote="YES", user=user))


    clean = discord.app_commands.Group(
        name="clean",
        description="Purge deletes messages from the channel",
        default_permissions=discord.Permissions(manage_messages=True)
    )
    @clean.command(
        name="all",
        description="Deletes the specified amount of messages"
    )
    async def all(
        self, 
        ctx: discord.Interaction, 
        amount: int = 10
    ) -> None:
        """
        clean_all_help
        examples:
        -clean all 25
        """
        if amount < 1: return await ctx.response.send_message(self.locale.t(ctx.guild, "amount_too_small", _emote="NO"))
        if amount > 300: return await ctx.response.send_message(self.locale.t(ctx.guild, "amount_too_big", _emote="NO"))

        msg, kwargs = await self.clean_messages(
            ctx,
            amount,
            lambda _: True
        )
        await ctx.response.send_message(msg, **kwargs)


    @clean.command(
        name="user",
        description="Deletes the specified amount of messages from the user"
    )
    async def user(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member, 
        amount: int = 10
    ) -> None:
        """
        clean_user_help
        examples:
        -clean user @paul#0009 25
        -clean user 543056846601191508
        """
        if amount < 1: return await ctx.response.send_message(self.locale.t(ctx.guild, "amount_too_small", _emote="NO"))
        if amount > 300: return await ctx.response.send_message(self.locale.t(ctx.guild, "amount_too_big", _emote="NO"))

        msg, kwargs = await self.clean_messages(
            ctx,
            amount,
            lambda m: m.author.id == user.id
        )
        await ctx.response.send_message(msg, **kwargs)


    @clean.command(
        name="content",
        description="Deletes the specified amount of messages containing the given content"
    )
    async def content(
        self, 
        ctx: discord.Interaction, 
        *, 
        text: str
    ) -> None:
        """
        clean_content_help
        examples:
        -clean content bad words
        """
        msg, kwargs = await self.clean_messages(
            ctx,
            300,
            lambda m: text.lower() in m.content.lower()
        )
        await ctx.response.send_message(msg, **kwargs)


    async def report(
        self,
        i: discord.Interaction,
        msg: discord.Message
    ) -> None:
        if not self.can_act(
            msg.guild,
            i.user,
            msg.author
        ): return await i.response.send_message(
            embed=Embed(
                i,
                description=self.locale.t(msg.guild, "report_mod", _emote="NO")
            ),
            ephemeral=True
        )
        
        content = msg.content + " ".join([x.url for x in msg.attachments])
        e = Embed(
            i,
            color=0x2c2f33,
            description="{} **Message reported:** {} ({}) \n\n**Reporter:** {} ({}) \n**Link:** [Here]({})".format(
                self.bot.emotes.get("ALARM"),
                msg.author.mention,
                msg.author.id,
                i.user.mention,
                i.user.id,
                msg.jump_url,
            )
        )
        e.add_fields([
            {
                "name": "Channel",
                "value": f"{msg.channel.mention} ({msg.channel.id})",
                "inline": False
            },
            {
                "name": "Content",
                "value": "```\n{}\n```".format(
                    "None" if len(content) < 1 else content[:1024]
                ),
                "inline": False
            }
        ])
        e.add_view(ActionedView(self.bot))
        await self.log_processor.execute(msg.guild, "report", **{
            "_embed": e
        })

        await i.response.send_message(
            self.locale.t(msg.guild, "reported", _emote="YES", user=msg.author), 
            ephemeral=True
        )


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(ModerationPlugin(bot))