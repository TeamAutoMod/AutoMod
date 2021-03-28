import asyncio
import time
import os
import datetime
import traceback
import shlex
import argparse
import logging

import discord
from discord.ext import commands

from i18n import Translator
from Utils import Logging, Utils, PermCheckers
from Utils.Converters import DiscordUser, Duration, RangedInt
from Utils.Constants import RED_TICK, GREEN_TICK

from Cogs.Base import BaseCog
from Bot.Handlers import check_mutes
from Database import Connector, DBUtils
from Database.Schemas import warn_schema, mute_schema, new_infraction
from Bot.Handlers import PostParseError

log = logging.getLogger(__name__)


db = Connector.Database()


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class Moderation(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.loop.create_task(check_mutes(bot))



    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: DiscordUser, *, reason: str = None):
        """ban_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")
        
        member = await Utils.get_member(ctx.bot, ctx.guild, user.id)
        if member is not None:
            if await self.can_act(ctx, member, ctx.author):
                self.bot.running_removals.add(member.id)
                await self._ban(ctx, member, reason)

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, member, ctx.author, timestamp, "Ban", reason))
                
                await ctx.send(Translator.translate(ctx.guild, "user_banned", _emote="YES", user=member, user_id=member.id, reason=reason, case=case))
                on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_ban", _emote="ALERT", on_time=on_time, user=member, user_id=member.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))
            else:
                await ctx.send(Translator.translate(ctx.guild, "ban_not_allowed", _emote="NO", user=member.name))
        else:
            await ctx.send(Translator.translate(ctx.guild, "target_not_on_server", _emote="NO_MOUTH"))


    
    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: DiscordUser, *, reason: str = None):
        """kick_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")
        
        member = await Utils.get_member(ctx.bot, ctx.guild, user.id)
        if member is not None:
            if await self.can_act(ctx, member, ctx.author):
                self.bot.running_removals.add(member.id)
                await self._kick(ctx, member, reason)

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, member, ctx.author, timestamp, "Kick", reason))

                await ctx.send(Translator.translate(ctx.guild, "user_kicked", _emote="YES", user=member, user_id=member.id, reason=reason, case=case))
                on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_kick", _emote="SHOE", on_time=on_time, user=member, user_id=member.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))
            else:
                await ctx.send(Translator.translate(ctx.guild, "kick_not_allowed", _emote="NO", user=member.name))
        else:
            await ctx.send(Translator.translate(ctx.guild, "target_not_on_server", _emote="NO_MOUTH"))


    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def cleanban(self, ctx, user: DiscordUser, *, reason: str = None):
        """cleanban_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")
        
        member = await Utils.get_member(ctx.bot, ctx.guild, user.id)
        if member is not None:
            if await self.can_act(ctx, member, ctx.author):
                self.bot.running_removals.add(member.id)
                await self._ban(ctx, member, reason, 1)
                await self._unban(ctx, member, "Clean Ban")

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, member, ctx.author, timestamp, "Clean Ban", reason))

                await ctx.send(Translator.translate(ctx.guild, "user_cleanbanned", _emote="YES", user=member, user_id=member.id, reason=reason, case=case))
                on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_cleanban", _emote="ALERT", on_time=on_time, user=member, user_id=member.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))
            else:
                await ctx.send(Translator.translate(ctx.guild, "ban_not_allowed", user=member.name))
        else:
            await ctx.send(Translator.translate(ctx.guild, "target_not_on_server", _emote="NO_MOUTH"))

    
    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, user: DiscordUser, *, reason: str = None):
        """softban_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")
        
        member = await Utils.get_member(ctx.bot, ctx.guild, user.id)
        if member is not None:
            if await self.can_act(ctx, member, ctx.author):
                self.bot.running_removals.add(member.id)
                await self._ban(ctx, member, reason, 1)
                await self._unban(ctx, member, "Soft Ban")

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, member, ctx.author, timestamp, "Soft Ban", reason))

                await ctx.send(Translator.translate(ctx.guild, "user_softbanned", _emote="YES", user=member, user_id=member.id, reason=reason, case=case))
                on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_softban", _emote="ALERT", on_time=on_time, user=member, user_id=member.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))
            else:
                await ctx.send(Translator.translate(ctx.guild, "ban_not_allowed", _emote="NO", user=member.name))
        else:
            await ctx.send(Translator.translate(ctx.guild, "target_not_on_server", _emote="NO_MOUTH"))


    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def forceban(self, ctx, user: DiscordUser, *, reason: str = None):
        """forceban_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")
        
        try:
            member = await commands.MemberConverter().convert(ctx, str(user.id))
        except commands.BadArgument:
            try:
                await ctx.guild.fetch_ban(user)
            except discord.NotFound:
                await self._forceban(ctx, user, reason)

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, user, ctx.author, timestamp, "Force Ban", reason))

                await ctx.send(Translator.translate(ctx.guild, "user_forcebanned", _emote="YES", user=user, user_id=user.id, reason=reason, case=case))
                on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_forceban", _emote="ALERT", on_time=on_time, user=user, user_id=user.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))
            else:
                await ctx.send(Translator.translate(ctx.guild, "target_already_banned", _emote="NO_MOUTH"))
        else:
            await ctx.invoke(self.ban, user=user, reason=reason)



    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: DiscordUser, *, reason: str = None):
        """unban_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")
        
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await ctx.send(Translator.translate(ctx.guild, "not_banned", _emote="NO", user=user.name))
        else:
            self.bot.running_unbans.add(user.id)
            await self._unban(ctx, user, reason)

            case = DBUtils.new_case()
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
            DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, user, ctx.author, timestamp, "Unban", reason))

            await ctx.send(Translator.translate(ctx.guild, "user_unbanned", _emote="YES", user=user, user_id=user.id, reason=reason, case=case))
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_unban", _emote="ANGEL", on_time=on_time, user=user, user_id=user.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))



    def is_muted(self, guild, user):
        _ = DBUtils.get(
            db.mutes,
            "mute_id",
            f"{guild.id}-{user.id}",
            "ending"
        )
        if _ is None:
            return False
        else:
            return True


    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def mute(self, ctx, user: discord.Member, length: Duration, *, reason: str = ""):
        """mute_help"""
        if length.unit is None:
            parts = reason.split(" ")
            length.unit = parts[0]
            reason = " ".join(parts[1:])
        if reason == "":
            reason = Translator.translate(ctx.guild, "no_reason")
            
        mute_role_id = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "muteRole")
        if str(mute_role_id) == "" or mute_role_id == None:
            return await ctx.send(Translator.translate(ctx.guild, "no_mute_role", _emote="NO", prefix=ctx.prefix))
        else:
            role = ctx.guild.get_role(int(mute_role_id))
            if role is None:
                return await ctx.send(Translator.translate(ctx.guild, "no_mute_role", _emote="NO", prefix=ctx.prefix))
            if self.is_muted(ctx.guild, user):
                # user is already muted, should we extend their mute?
                confirm = await ctx.prompt(f"{user} is already muted. Do you want to extend their mute?", timeout=15)
                if not confirm:
                    return await ctx.send(Translator.translate(ctx.guild, "aborting"))

                until = (DBUtils.get(db.mutes, "mute_id", f"{ctx.guild.id}-{user.id}", "ending") + datetime.timedelta(seconds=length.to_seconds(ctx)))
                DBUtils.update(
                    db.mutes,
                    "mute_id",
                    f"{ctx.guild.id}-{user.id}",
                    "ending",
                    until
                )
                await ctx.send(Translator.translate(ctx.guild, "mute_extended", _emote="YES", user=user, user_id=user.id, length=length.length, unit=length.unit, reason=reason))
                on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_mute_extended", _emote="NO_MOUTH", on_time=on_time, user=user, user_id=user.id, moderator=ctx.author, moderator_id=ctx.author.id, length=length.length, unit=length.unit, reason=reason))
                if not role in user.roles:
                    try:
                        await user.add_roles(role)
                    except Exception:
                        return
                return
            else:
                if (ctx.author != user and user != ctx.bot.user and ctx.author.top_role > user.top_role) or ctx.guild.owner == ctx.author:
                    if ctx.guild.me.top_role.position > role.position:
                        seconds = length.to_seconds(ctx)
                        if seconds >= 1:
                            await user.add_roles(role)
                            until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))
                            DBUtils.insert(db.mutes, mute_schema(ctx.guild.id, user.id, until))
                            
                            case = DBUtils.new_case()
                            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                            DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, user, ctx.author, timestamp, "Mute", reason))
                            
                            await ctx.send(Translator.translate(ctx.guild, "user_muted", _emote="YES", user=user, user_id=user.id, length=length.length, unit=length.unit, reason=reason, case=case))
                            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                            await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_mute", _emote="NO_MOUTH", on_time=on_time, user=user, user_id=user.id, moderator=ctx.author, moderator_id=ctx.author.id, length=length.length, unit=length.unit, reason=reason, case=case))
                        else:
                            raise commands.BadArgument("number_too_small")
                    else:
                        await ctx.send(Translator.translate(ctx.guild, "role_too_high"))
                else:
                    await ctx.send(Translator.translate(ctx.guild, "mute_not_allowed", _emote="NO", user=user.name))
    


    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unmute(self, ctx, user: discord.Member):
        if not self.is_muted(ctx.guild, user):
            return await ctx.send(Translator.translate(ctx.guild, "not_muted", _emote="NO", user=user.name))
        DBUtils.delete(db.mutes, "mute_id", f"{ctx.guild.id}-{user.id}")
        await ctx.send(Translator.translate(ctx.guild, "mute_lifted", _emote="YES", user=user, user_id=user.id))
        
        # check if we can remove the role
        try:
            mute_role_id = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "muteRole")
            role = ctx.guild.get_role(int(mute_role_id))
            await user.remove_roles(role)
        except Exception:
            pass
        finally:
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_manual_unmute", _emote="ANGEL", on_time=on_time, user=user, user_id=user.id, moderator=ctx.author, moderator_id=ctx.author.id))





    @commands.guild_only()
    @commands.command(aliases=["multiban"], usage="<targets> [reason]")
    @commands.has_permissions(ban_members=True)
    async def mban(self, ctx, targets: commands.Greedy[DiscordUser], *, reason: str = None):
        """mban_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")

        if len(targets) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "no_ban_then", _emote="SALUTE"))

        if len(targets) > 15:
            return await ctx.send(Translator.translate(ctx.guild, "max_ban"))
            
        targets = list(set(targets))
        failing = 0
        to_ban = []
        for t in targets:
            member = ctx.guild.get_member(t.id)
            automod = ctx.guild.get_member(self.bot.user.id)
            if member is not None:
                if (member.top_role.position >= automod.top_role.position or member.top_role.position >= ctx.author.top_role.position or member.id == ctx.author.id or member.id == ctx.guild.owner.id):
                    failing += 1
                else:
                    to_ban.append(t)
            else:
                if await self.is_banned(ctx, t) is True:
                    failing += 1
                else:
                    to_ban.append(t)
        
        if failing >= len(targets):
            return await ctx.send(Translator.translate(ctx.guild, "cant_ban_anyone"))
            
        confirm = await ctx.prompt(f'This action will ban {len(to_ban)} member{"" if len(to_ban) == 1 else "s"}. Are you sure?')
        if not confirm:
            return await ctx.send(Translator.translate(ctx.guild, "aborting"))

        banned = 0
        for target in to_ban:
            try:
                await self._forceban(ctx, target, reason)
                self.bot.running_removals.add(target.id)

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, target, ctx.author, timestamp, "Ban", f"[Multi Ban] {reason}"))
            except discord.HTTPException:
                pass
            else:
                banned += 1
        
        await ctx.send(Translator.translate(ctx.guild, "mban_success", _emote="YES", users=banned, total=len(to_ban)))
        on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_mass_ban", _emote="ALERT", on_time=on_time, users=banned, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason))


    @commands.guild_only()
    @commands.command(aliases=["masskick"], usage="<targets> [reason]")
    @commands.has_permissions(kick_members=True)
    async def mkick(self, ctx, targets: commands.Greedy[DiscordUser] , *, reason: str = None):
        """mkick_help"""
        if reason is None:
            reason = Translator.translate(ctx.guild, "no_reason")

        if len(targets) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "no_kick_then", _emote="SALUTE"))

        if len(targets) > 15:
            return await ctx.send(Translator.translate(ctx.guild, "max_kick"))
            
        targets = list(set(targets))
        failing = 0
        to_kick = []
        for t in targets:
            member = ctx.guild.get_member(t.id)
            automod = ctx.guild.get_member(self.bot.user.id)
            if member is not None:
                if (member.top_role.position >= automod.top_role.position or member.top_role.position >= ctx.author.top_role.position or member.id == ctx.author.id or member.id == ctx.guild.owner.id):
                    failing += 1
                else:
                    to_kick.append(t)
            else:
                failing += 1
            
        if failing >= len(targets):
            return await ctx.send(Translator.translate(ctx.guild, "cant_kick_anyone"))
        
        confirm = await ctx.prompt(f'This action will ban {len(to_kick)} member{"" if len(to_kick) == 1 else "s"}. Are you sure?')
        if not confirm:
            return await ctx.send(Translator.translate(ctx.guild, "aborting"))
        
        kicked = 0
        for target in to_kick:
            try:
                await ctx.guild.kick(target, reason=reason)
                self.bot.running_removals.add(target.id)

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, target, ctx.author, timestamp, "Kick", f"[Multi Kick] {reason}"))
            except discord.HTTPException:
                pass
            else:
                kicked += 1
        
        await ctx.send(Translator.translate(ctx.guild, "mkick_success", _emote="YES", users=kicked, total=len(kicked)))
        on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_mass_kick", _emote="SHOE", on_time=on_time, users=kicked, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason))



    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: RangedInt(1, 200)):
        """purge_help"""
        await ctx.invoke(self.clean_all, amount)


    @commands.guild_only()
    @commands.group(aliases=["clear"])
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx):
        """clean_help"""
        if ctx.invoked_subcommand == self.clean:
            await ctx.invoke(self.bot.get_command("help"), qeury="clean")

    @commands.guild_only()
    @clean.command("user")
    @commands.has_permissions(manage_messages=True)
    async def clean_user(self, ctx, users: commands.Greedy[DiscordUser], amount: RangedInt(1, 500) = 50):
        """clean_user_help"""
        if len(users) == 0:
            return await ctx.send(Translator.translate(ctx.guild, "no_delete_then", _emote="THINK"))
        await self.perform_cleaning(ctx, amount, lambda x: any(x.author.id == u.id for u in users))
    

    @commands.guild_only()
    @clean.command("bots")
    @commands.has_permissions(manage_messages=True)
    async def clean_bots(self, ctx, amount: RangedInt(1, 200) = 50):
        """clean_bots_help"""
        await self.perform_cleaning(ctx, amount, lambda x: x.author.bot)
    

    @commands.guild_only()
    @clean.command("all")
    @commands.has_permissions(manage_messages=True)
    async def clean_all(self, ctx, amount: RangedInt(1, 200)):
        """clean_all_help"""
        await self.perform_cleaning(ctx, amount, lambda x: True)

    
    @commands.guild_only()
    @clean.command(name="last", usage="<duration>")
    @commands.has_permissions(manage_messages=True)
    async def clean_last(self, ctx: commands.Command, duration: Duration, excess = ""):
        """clean_last_help"""
        if duration.unit is None:
            duration.unit = excess
        until = datetime.datetime.utcfromtimestamp(time.time() - duration.to_seconds(ctx))
        await self.perform_cleaning(ctx, 500, lambda x: True, time=until)
    

    @commands.guild_only()
    @clean.command("until")
    @commands.has_permissions(manage_messages=True)
    async def clean_until(self, ctx, message: discord.Message):
        """clean_until_help"""
        try:
            await self.perform_cleaning(ctx, 500, lambda x: True, after=message)
        except Exception as ex:
            print(ex)


    @commands.guild_only()
    @clean.command("between")
    @commands.has_permissions(manage_messages=True)
    async def clean_between(self, ctx, start: discord.Message, end: discord.Message):
        """clean_between_help"""
        await self.perform_cleaning(ctx, 500, lambda x: True, before=end, after=start)

        
    




    async def _ban(self, ctx, user, reason, days=0):
        try:
            await ctx.guild.ban(user=user, reason=reason, delete_message_days=days)
        except Exception as e:
            return await ctx.send(Translator.translate(ctx.guild, "ban_failed", _emote="NO", error=e))



    async def _kick(self, ctx, user, reason):
        try:
            await ctx.guild.kick(user=user, reason=reason)
        except Exception as e:
            return await ctx.send(Translator.translate(ctx.guild, "kick_failed", _emote="NO", error=e))



    async def _unban(self, ctx, user, reason):
        try:
            await ctx.guild.unban(user=user, reason=reason)
        except Exception as e:
            return await ctx.send(Translator.translate(ctx.guild, "unban_failed", _emote="NO", error=e))



    async def _forceban(self, ctx, user, reason):
        if user.discriminator == "0000":
            return await ctx.send(Translator.translate(ctx.guild, "is_system_user", _emote="NO"))
        
        try:
            await ctx.guild.ban(user=user, reason=reason)
        except Exception as e:
            return await ctx.send(Translator.translate(ctx.guild, "ban_failed", _emote="NO", error=e))



    async def is_banned(self, ctx, user):
        try:
            await ctx.guild.fetch_ban(user)
            return True
        except Exception:
            return False


    async def perform_cleaning(self, ctx, limit, check, *, before=None, after=None, time=None):
        if ctx.channel.id in self.bot.cleans_running:
            return await ctx.send(Translator.translate(ctx.guild, "already_cleaning", _emote="NO"))
        if limit > 500:
            return await ctx.send(Translator.translate(ctx.guild, "too_many_messages", _emote="NO", limit=limit))
        
        if before is None:
            before = ctx.message
        else:
            if isinstance(before, discord.Message):
                before = before
            else:
                before = discord.Object(id=before)
        if after is not None:
            if isinstance(after, discord.Message):
                after = after
            else:
                after = discord.Object(id=after)
        
        # after is set to a discord Object (message), which won't work for the clean last command
        # therefore we have to change its type if a time is given
        if time is not None:
            after = time
        
        self.bot.cleans_running[ctx.channel.id] = set()
        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=check)
            await ctx.send(Translator.translate(ctx.guild, "clean_success", _emote="YES", deleted=len(deleted), plural="" if len(deleted) == 1 else "s"))
        except Exception as ex:
            await ctx.send(Translator.translate(ctx.guild, "cleaning_error", _emote="NO", error=ex))
            self.bot.loop.create_task(self.finish_purgings(ctx.channel.id))
        self.bot.loop.create_task(self.finish_purgings(ctx.channel.id))


    async def finish_purgings(self, channel_id):
        await asyncio.sleep(1) # we don't want to miss any delete events
        del self.bot.cleans_running[channel_id]



    async def can_act(self, ctx, target, moderator):
        automod = ctx.guild.get_member(self.bot.user.id)
        if target.top_role.position >= moderator.top_role.position or target.top_role.position >= automod.top_role.position or ctx.guild.owner.id == target.id or target.id == moderator.id or target.id == automod.id:
            return False
        try:
            await ctx.guild.fetch_ban(target)
            await ctx.send(Translator.translate(ctx.guild, "target_already_banned", _emote="NO_MOUTH"))
            return False
        except discord.NotFound:
            return True
        else:
            return True


    ######## complex moderation commands

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, *, args):
        """massban_help"""
        if not isinstance(ctx.author, discord.Member): # sometime discord just thinks the author isn't a guild member, wtf?
            try:
                author = await ctx.guild.fetch_member(ctx.author.id)
            except discord.HTTPException:
                return await ctx.send(Translator.translate(ctx.guild, "no_member_object"))
        else:
            author = ctx.author
        

        """Define arguments"""
        p = Arguments(add_help=False, allow_abbrev=False)
        p.add_argument("--channel", "-c")
        p.add_argument("--reason", "-r")

        p.add_argument("--search", type=int, default=100)
        p.add_argument("--regex")

        p.add_argument("--no-avatar", action="store_true")
        p.add_argument("--no-roles", action="store_true")

        p.add_argument("--created", type=int)
        p.add_argument("--joined", type=int)
        p.add_argument("--joined-before", type=str or int)
        p.add_argument("--joined-after", type=str or int)

        p.add_argument("--contains")
        p.add_argument("--starts")
        p.add_argument("--ends")
        p.add_argument("--match")

        p.add_argument("--show", action="store_true")

        p.add_argument("--embeds", action="store_const", const=lambda m: len(m.embeds))
        p.add_argument("--files", action="store_const", const=lambda m: len(m.attachments))

        p.add_argument("--after", type=int)
        p.add_argument("--before", type=int)

        try:
            args = p.parse_args(shlex.split(args))
        except Exception as ex:
            return await ctx.send(str(ex))

        targets = []

        if args.channel:
            channel = await commands.TextChannelConverter().convert(ctx, args.channel)

            before = args.before and discord.Object(id=args.before)
            after = args.after and discord.Object(id=args.after)

            pr = []
            if args.contains:
                pr.append(lambda m: args.contains.lower() in m.content.lower())
            if args.starts:
                pr.append(lambda m: m.content.startswith(args.starts))
            if args.ends:
                pr.append(lambda m: m.content.endswith(args.ends))
            if args.match:
                try:
                    _match = re.compile(args.match)
                except re.error as ex:
                    return await ctx.send(Translator.translate(ctx.guild, "invalid_regex", ex=ex))
                else:
                    pr.append(lambda m, x = _match: x.match(m.content))
            if args.embeds:
                pr.append(args.embeds)
            if args.files:
                pr.append(args.files)
            
            async for message in channel.history(limit=min(max(1, args.search), 2000), before=before, after=after):
                if all(_p(message) for _p in pr):
                    targets.append(message.author)
        else:
            if ctx.guild.chunked:
                targets = ctx.guild.members
            else:
                async with ctx.typing():
                    await ctx.guild.chunk(cache=True)
                targets = ctx.guild.members
            
        pr = [
            lambda m: isinstance(m, discord.Member) and can_execute(ctx, author, m),
            lambda m: not m.bot,
            lambda m: m.discriminator != "0000"
        ]

        converter = commands.MemberConverter()

        if args.regex:
            try:
                _regex = re.compile(args.regex)
            except re.error as ex:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_regex", ex=ex))
            else:
                pr.append(lambda m, x = _regex: x.match(m.name))
        
        if args.no_avatar:
            pr.append(lambda m: m.avatar is None)
        if args.no_roles:
            pr.append(lambda m: len(getattr(m, "roles", [])) <= 1)

        now = datetime.datetime.utcnow()
        if args.created:
            def created(member, *, offset=now - datetime.timedelta(minutes=args.created)):
                return member.created_at > offset
            pr.append(created)
        
        if args.joined:
            def joined(member, *, offset=now - datetime.timedelta(minutes=args.joined)):
                if isinstance(member, discord.User):
                    return True # in this case they already left the server
                return member.joined_at > offset
            pr.append(joined)
        
        if args.joined_after:
            _joined_after_member = await converter.convert(ctx, args.joined_after)
            def joined_after(member, *, _other=_joined_after_member):
                return member.joined_at and _other.joined_at and member.joined_at > _other.joined_at
            pr.append(joined_after)

        if args.joined_before:
            _joined_before_member = await converter.convert(ctx, args.joined_after)
            def joined_before(member, *, _other=_joined_before_member):
                return member.joined_at and _other.joined_at and member.joined_at < _other.joined_at
            pr.append(joined_before)
        
        targets = {m for m in targets if all(_p(m) for _p in pr)}
        if len(targets) == 0:
            return await ctx.send(Translator.translate(ctx.guild, "no_targets_found", _emote="NO"))
        
        if args.show:
            targets = sorted(targets, key=lambda m: m.joined_at or now)
            fmt = "\n".join(f"{m.id}\tJoined: {m.joined_at}\tCreated: {m.created_at}\n{m}" for m in targets)
            content = f"Time right now: {datetime.datetime.utcnow()}\nTotal targets: {len(targets)}\n{fmt}"
            f = discord.File(io.BytesIO(content.encode("utf-8")), filename="members.txt")
            return await ctx.send(file=f)

        if args.reason is None:
            return await ctx.send(Translator.translate(ctx.guild, "missing_reason_flag"))
        else:
            reason = await Reason().convert(ctx, args.reason)

        confirm = await ctx.prompt(f'This action will ban {len(targets)} member{"" if len(targets) == 1 else "s"}. Are you sure?')
        if not confirm:
            return await ctx.send(Translator.translate(ctx.guild, "aborting"))
        
        banned = 0
        for target in targets:
            try:
                await self._forceban(ctx, target, reason)
                self.bot.running_removals.add(target.id)

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, target, ctx.author, timestamp, "Ban", f"[Custom Ban] {reason}"))
            except discord.HTTPException:
                pass
            else:
                banned += 1
        
        await ctx.send(Translator.translate(ctx.guild, "mban_success", _emote="YES", users=banned, total=len(targets)))
        on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_mass_ban", _emote="ALERT", on_time=on_time, users=banned, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason))



    @clean.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def custom(self, ctx, *, args: str):
        """clean_custom_help"""
        try:
            p = Arguments(add_help=False, allow_abbrev=False)
            p.add_argument("--user", nargs="+")

            p.add_argument("--contains", nargs="+")
            p.add_argument("--starts", nargs="+")
            p.add_argument("--ends", nargs="+")

            p.add_argument("--or", action="store_true", dest="_or")
            p.add_argument("--not", action="store_true", dest="_not")

            p.add_argument("--emoji", action="store_true")

            p.add_argument("--bot", action="store_const", const=lambda m: m.author.bot)
            p.add_argument("--embeds", action="store_const", const=lambda m: len(m.embeds))
            p.add_argument("--files", action="store_const", const=lambda m: len(m.attachments))
            p.add_argument("--reactions", action="store_const", const=lambda m: len(m.reactions))

            p.add_argument("--search", type=int)
            p.add_argument("--after", type=int)
            p.add_argument("--before", type=int)

            try:
                args = p.parse_args(shlex.split(args))
            except Exception as ex:
                return await ctx.send(str(ex))
            
            pr = []
            if args.bot:
                pr.append(args.bot)
            
            if args.embeds:
                pr.append(args.embeds)

            if args.files:
                pr.append(args.files)

            if args.reactions:
                pr.append(args.reactions)

            if args.emoji:
                custom_emote = re.compile(r"<:(\w+):(\d+)>")
                pr.append(lambda m: custom_emote.search(m.content))
            
            if args.user:
                targets = []
                converter = commands.MemberConverter()
                for t in args.user:
                    try:
                        target = await converter.convert(ctx, t)
                        targets.append(target)
                    except Exception as ex:
                        return await ctx.send(str(ex))
                    
                pr.append(lambda m: m.author in targets)
            
            if args.contains:
                pr.append(lambda m: any(s in m.content for s in args.contains))
            
            if args.starts:
                pr.append(lambda m: any(m.content.startswith(s) for s in args.starts))

            if args.ends:
                pr.append(lambda m: any(m.content.endswith(s) for s in args.ends))
            
            o = all if not args._or else any
            def check(m):
                r = o(p(m) for p in pr)
                if args._not:
                    return not r
                return r
            
            if args.after:
                if args.search is None:
                    args.search = 2000
                
            if args.search is None:
                args.search = 100
            
            args.search = max(0, min(2000, args.search))

            def point(ctx, before=None, after=None):
                if before is None:
                    before = ctx.message
                else:
                    before = discord.Object(id=before)
                if after is not None:
                    after = discord.Object(id=after)
                return before, after
            
            before, after = point(ctx, args.before, args.after)
            if ctx.channel.id in self.bot.cleans_running:
                return await ctx.send(Translator.translate(ctx.guild, "already_cleaning", _emote="NO"))
            
            self.bot.cleans_running[ctx.channel.id] = set()
            _msg = await ctx.send(Translator.translate(ctx.guild, "working_on_action", _emote="LOAD"))
            try:
                deleted = await ctx.channel.purge(limit=args.search, check=check, before=before, after=after)
                del self.bot.cleans_running[ctx.channel.id]
                try:
                    await _msg.edit(content=Translator.translate(ctx.guild, "clean_success", _emote="YES", deleted=len(deleted), plural="" if len(deleted) == 1 else "s"))
                except discord.NotFound:
                    pass
            except Exception as e:
                del self.bot.cleans_running[ctx.channel.id]
                log.error(e)
                try:
                    await _msg.edit(content=Translator.translate(ctx.guild, "already_deleted", _emote="NO"))
                except discord.NotFound:
                    pass
        except Exception as _ex:
            log.error(f"[Commands] {_ex}")


    # TODO Add a permaban command (instantly bans a user after getting unbanned)
    # @commands.command()
    # @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    # async def permaban(self, ctx, user: DiscordUser, *, reason = None):
    #     pass




    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            g = member.guild
            if g is None:
                return
            mute = DBUtils.get(db.mutes, "mute_id", f"{g.id}-{member.id}", "ending")
            if not mute:
                return
            else:
                _id = DBUtils.get(db.configs, "guildId", f"{g.id}", "muteRole")
                if _id == "" == _id == None or _id == 0:
                    return # mute role isn't configured anymore?
                mute_role = discord.utils.get(g.roles, id=int(_id))
                if mute_role is None:
                    return # mute role got deleted
                else:
                    # trying to escape the mute? not with us!
                    try:
                        await member.add_roles(mute_role)

                        on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        await Logging.log_to_guild(g.id, "memberLogChannel", Translator.translate("log_reapplied_mute", _emote="WARN", on_time=on_time, user=member, user_id=member.id))
                    except Exception:
                        return
        except Exception:
            pass




def setup(bot):
    bot.add_cog(Moderation(bot))