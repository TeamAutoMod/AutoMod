import asyncio
import time
import datetime
import logging
import traceback
from collections import defaultdict

import discord
from discord import Guild, TextChannel, Member, Message
from discord.ext import commands

from i18n import Translator
from Database import Connector, DBUtils
from Database.Schemas import new_infraction
from Cogs.Base import BaseCog
from Utils import Logging, PermCheckers


log = logging.getLogger(__name__)

db = Connector.Database()


class CooldownContentMapping(commands.CooldownMapping):
    def _bucket_key(self, message):
        return (message.channel.id, message.content)


class SpamChecker:
    """
    This checks the following things:
    1. If the same content has been sent 15 times within the last 17 seconds
    2. If a user has sent 10 messages within the last 12 seconds

    From experience these rquirements are just met when an actual spam is happening
    """
    def __init__(self):
        self.check_content = CooldownContentMapping.from_cooldown(15, 17.0, commands.BucketType.member)
        self.check_user = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)

    def is_spamming(self, msg):
        if msg.guild is None:
            return # we don't want to check in DMs
    
        c = msg.created_at.replace(tzinfo=datetime.timezone.utc).timestamp() # the current time as a timestamp object

        user_bucket = self.check_user.get_bucket(msg)
        if user_bucket.update_rate_limit(c):
            return True
        
        content_bucket = self.check_content.get_bucket(msg)
        if content_bucket.update_rate_limit(c):
            return True

        return False



class AntiSpam(BaseCog):
    def __init__(self, bot):
        super(AntiSpam, self).__init__(bot)

        self.spam_checker = defaultdict(SpamChecker)
        self.handling = []

    
    async def handle_spam(self, guild, member, msg):
        if DBUtils.get(db.configs, "guildId", f"{guild.id}", "antispam") is False:
            return # anti spam isn't enabled for this guild
        
        c = self.spam_checker[guild.id]
        if not c.is_spamming(msg):
            return
        
        self.handling.append(member.id)
        
        try:
            await guild.kick(user=member, reason="[AutoMod] Spam")
        except discord.HTTPException:
            log.info(f"[Anti Spam] Error while trying to kick {member} ({member.id}) from server {guild} via the anti spam system")
            self.handling.remove(member.id)
        else:
            log.info(f"[Anti Spam] Kicked {member} ({member.id}) from server {guild} via the anti spam system")
            self.handling.remove(member.id)

            case = DBUtils.new_case()
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
            mod = discord.utils.get(guild.members, id=self.bot.user.id)
            DBUtils.insert(db.inf, new_infraction(case, msg.guild.id, member, mod, timestamp, "Kick", "[AutoMod] Spam"))

            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(guild.id, "memberLogChannel", Translator.translate(guild, "log_spam", on_time=on_time, user=member, user_id=member.id, moderator=self.bot.user, moderator_id=self.bot.user.id, channel=msg.channel.mention))


    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        try:
            if not isinstance(message.author, discord.Member):
                return
            if message.author.discriminator == "0000":
                return
            
            if message.author.id == self.bot.user.id or message.guild is None:
                return # we don't want to delete our own messages or DMs
            
            if PermCheckers.is_mod(message.author):
                return # mods+ can bypass this event
            
            
            if message.author.id in self.handling:
                return # is already being handled

            await self.handle_spam(message.guild, message.author, message)
        except Exception:
            ex = traceback.format_exc()
            log.info(f"[Anti Spam] Error in on_messages listener: {ex}")
            pass
        

        



def setup(bot):
    bot.add_cog(AntiSpam(bot))