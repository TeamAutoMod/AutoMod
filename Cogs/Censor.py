import re
import asyncio
import datetime

import discord
from discord import DMChannel, Message, RawMessageUpdateEvent
from discord.ext import commands

from i18n import Translator
from Utils import Logging, PermCheckers, Utils
from Database import Connector, DBUtils

from Cogs.Base import BaseCog
from Utils.Constants import get_censor_pattern, ZALGO_RE


db = Connector.Database()


class Censor(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.guild is None or message.webhook_id is not None or message.channel is None or isinstance(message.channel, DMChannel) or message.author.bot is True or self.bot.user.id == message.author.id:
            return
        if DBUtils.get(db.configs, "guildID", f"{message.guild.id}", "automod") is False:
            return
        user = message.guild.get_member(message.author.id)
        if user is None:
            return
        await self.check_message(message.author, message.content, message.channel, message)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        channel = self.bot.get_channel(int(before.channel.id))
        if channel is None or isinstance(channel, DMChannel) or channel.guild is None:
            return
        if DBUtils.get(db.configs, "guildID", f"{channel.guild.id}", "automod") is False:
            return
        try:
            message = after
        except (discord.NotFound, discord.Forbidden):
            return
        else:
            target_id = message.author.id
        target = await Utils.get_member(self.bot, channel.guild, target_id)
        if target is not None and target_id != self.bot.user.id:
            await self.check_message(target, after.content, message.channel, message)


    async def check_message(self, target, content, channel, message):
        if PermCheckers.is_mod(target):
            return
        try:
            CENSOR_RE = get_censor_pattern(channel.guild.id)
        except Exception:
            return
        content = content.replace("//", "")

        try:
            found_zalgo = ZALGO_RE.search(content)
            if found_zalgo:
                self.bot.running_msg_deletions.add(message.id)
                await self.censor_zalgo(message, target, content, found_zalgo, channel)
                return
            else:
                pass
        except Exception:
            pass


        try:
            found_words = CENSOR_RE.findall(content.lower())
            if found_words:
                self.bot.running_msg_deletions.add(message.id)
                await self.censor_message(message, target, content, found_words, channel)
                return
            else:
                pass
        except Exception:
            pass


    async def censor_zalgo(self, message, target, content, found_zalgo, channel):
        if channel.permissions_for(channel.guild.me).manage_messages:
            try:
                await message.delete()
            except discord.NotFound:
                pass # guess someone was faster, but let's log it anyways
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(channel.guild.id, "memberLogChannel", Translator.translate(message.guild, "log_zalgo", on_time=on_time, user=target, user_id=target.id, moderator=self.bot.user, moderator_id=self.bot.user.id, channel=channel.mention, position=found_zalgo.start()))


    async def censor_message(self, message, target, content, found_words, channel):
        if channel.permissions_for(channel.guild.me).manage_messages:
            try:
                await message.delete()
            except discord.NotFound:
                pass
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(channel.guild.id, "memberLogChannel", Translator.translate(message.guild, "log_censor", on_time=on_time, user=target, user_id=target.id, moderator=self.bot.user, moderator_id=self.bot.user.id, channel=channel.mention, words=", ".join(found_words), content=content))
    


def setup(bot):
    bot.add_cog(Censor(bot))