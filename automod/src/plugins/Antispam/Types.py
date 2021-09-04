import discord
from discord.ext import commands

import datetime



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