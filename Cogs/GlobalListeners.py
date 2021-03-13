import asyncio
import time
from datetime import datetime

import discord
from discord import DMChannel, TextChannel, Message, Member, Guild, User
from discord.ext import commands

from i18n import Translator
from Utils import Logging

from Cogs.Base import BaseCog
from Database import Connector, DBUtils



db = Connector.Database()


class GlobalListeners(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        c = before.channel
        channel_id = int(c.id)
        if isinstance(c, DMChannel):
            return
        if c is None or str(channel_id) == str(DBUtils.get(db.configs, "guildId", f"{c.guild.id}", "memberLogChannel")):
            return
        if before.author.id == self.bot.user.id:
            return
        if c.guild is None:
            return
        if DBUtils.get(db.configs, "guildId", f"{c.guild.id}", "messageLogging") is False:
            return
        
        ignored_users = DBUtils.get(db.configs, "guildId", f"{c.guild.id}", "ignored_users")
        if int(before.author.id) in ignored_users:
            return
        else:
            if before.content != after.content:
                on_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(c.guild.id, "messageLogChannel", Translator.translate(before.guild, "log_message_edit", user=before.author, user_id=before.author.id, channel=c.mention, on_time=on_time, before=before.content, after=after.content))
            else:
                pass


    @commands.Cog.listener()
    async def on_message_delete(self, message: Message):
        await asyncio.sleep(1) # sleep a bit, we don't log message deletions from the censor module
        if message.id in self.bot.running_msg_deletions:
            self.bot.running_msg_deletions.remove(message.id)
            return
        c = message.channel
        channel_id = c.id
        if isinstance(c, DMChannel):
            return
        if c is None or str(channel_id) == str(DBUtils.get(db.configs, "guildId", f"{c.guild.id}", "memberLogChannel")) or not isinstance(c, TextChannel):
            return
        if message.author.id == self.bot.user.id:
            return
        if c.guild is None:
            return
        if DBUtils.get(db.configs, "guildId", f"{c.guild.id}", "messageLogging") is False:
            return

        ignored_users = DBUtils.get(db.configs, "guildId", f"{c.guild.id}", "ignored_users")
        if message.author.id in ignored_users:
            return
        else:
            on_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(c.guild.id, "messageLogChannel", Translator.translate(message.guild, "log_message_deletion", user=message.author, user_id=message.author.id, channel=c.mention, on_time=on_time, content=message.content))
        

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if DBUtils.get(db.configs, "guildId", f"{member.guild.id}", "memberLogging") is True:
            created = (datetime.fromtimestamp(time.time()) - member.created_at).days
            try:
                on_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(member.guild.id, Translator.translate(member.guild, "joinLogChannel", "log_join", user=member, user_id=member.id, on_time=on_time, age=created))
            except Exception:
                pass

        msg = DBUtils.get(db.configs, "guildId", f"{member.guild.id}", "welcomeMessage")
        welcome_id = DBUtils.get(db.configs, "guildId", f"{member.guild.id}", "welcomeChannel")

        if msg is None or msg == "":
            return
        if welcome_id is None or msg == "":
            return
        
        try:
            welcome_channel = await self.bot.fetch_channel(int(welcome_id))
        except Exception:
            return
        
        members = len(member.guild.members) # the guilds member count after the member joined
        mention = member.mention # mentions the new member
        member = member.name # displays the new members name without the discrim
        
        try:
            await welcome_channel.send(str(msg).format(members=members, member=member, mention=mention))
        except Exception:
            return

    
    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        await asyncio.sleep(1) # sleep a bit, so we don't log an unban made with the bot
        if member.id in self.bot.running_removals:
            self.bot.running_removals.remove(member.id)
            return
        if DBUtils.get(db.configs, "guildId", f"{member.guild.id}", "memberLogging") is True:
            joined = (datetime.fromtimestamp(time.time()) - member.joined_at).days
            try:
                on_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(member.guild.id, Translator.translate(member.guild, "joinLogChannel", "log_leave", user=member, user_id=member.id, on_time=on_time, joined=joined))
            except Exception:
                pass
        else:
            return


    @commands.Cog.listener()
    async def on_member_unban(self, guild: Guild, user: User):
        await asyncio.sleep(1) # sleep a bit, so we don't log an unban made with the bot
        if user.id in self.bot.running_unbans:
            self.bot.running_unbans.remove(user.id)
            return
        else:
            on_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(guild.id, "memberLogChannel", Translator.translate(guild, "log_manual_unban", on_time=on_time, user=user, user_id=user.id))




def setup(bot):
    bot.add_cog(GlobalListeners(bot))