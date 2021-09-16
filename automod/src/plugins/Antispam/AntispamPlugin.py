import discord
from discord.ext import commands

from collections import defaultdict

from ..PluginBlueprint import PluginBlueprint
from .Types import SpamChecker
from ...utils import Permissions



class AntispamPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.spam_checker = defaultdict(SpamChecker)
        self.is_being_handled = list()


    @commands.Cog.listener()
    async def on_spam(
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
    pass