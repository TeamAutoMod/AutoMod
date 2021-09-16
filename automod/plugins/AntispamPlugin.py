import discord
from discord.ext import commands

from collections import defaultdict
import datetime

from .PluginBlueprint import PluginBlueprint
from utils import Permissions



class CooldownContentMapping(commands.CooldownMapping):
    def _bucket_key(self, message):
        return (message.channel.id, message.content)


class SpamChecker:
    def __init__(self):
        self.check_content = CooldownContentMapping.from_cooldown(15, 17.0, commands.BucketType.member)
        self.check_user = commands.CooldownMapping.from_cooldown(10, 10.0, commands.BucketType.user)

    def is_spamming(self, msg):
        if msg.guild is None:
            return
        
        c = msg.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()

        user_bucket = self.check_user.get_bucket(msg)
        if user_bucket.update_rate_limit(c):
            return True
        
        content_bucket = self.check_content.get_bucket(msg)
        if content_bucket.update_rate_limit(c):
            return True

        return False


class AntispamPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.spam_checker = defaultdict(SpamChecker)
        self.is_being_handled = list()


    @commands.Cog.listener()
    async def on_antispam_event(
        self,
        message
    ):
        if message.guild is None:
            return
        if self.db.configs.get(message.guild.id, "antispam") is False:
            return
    
        author = message.guild.get_member(message.author)
        if author is None:
            return
        if Permissions.is_mod(author) or message.author.discriminator == "0000" or message.author.id == self.bot.user.id:
            return

        if message.author.id in self.is_being_handled:
            return

        if not "spam" in self.db.configs.get(message.guild.id, "automod"):
            return

        if self.db.configs.get(message.guild.id, "automod")["spam"]["status"] is False:
            return
        
        c = self.spam_checker[message.guild.id]
        if not c.is_spamming(message):
            return
        
        self.is_being_handled.append(message.author.id)

        await self.action_validator.figure_it_out(
            message, 
            message.author,
            "spam",
            moderator=self.bot.user,
            moderator_id=self.bot.user.id,
            user=message.author,
            user_id=message.author.id,
            reason="Spamming messages"
        )
        self.is_being_handled.remove(message.author.id)



def setup(bot):
    bot.add_cog(AntispamPlugin(bot))