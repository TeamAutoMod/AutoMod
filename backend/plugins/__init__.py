import discord
from discord.ext import commands



class AutoModPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
        self.locale = bot.locale


    def get_prefix(self, guild):
        p = self.db.configs.get(guild.id, "prefix")
        return p if p != None else "+"