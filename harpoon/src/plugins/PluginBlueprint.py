import discord
from discord.ext import commands



class PluginBlueprint(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.cache = bot.cache
        self.translator = bot.translator
        self.emotes = bot.emotes
        self.schemas = bot.schemas
        self.action_validator = bot.action_validator
        self.action_logger = bot.action_logger
        self.ignore_for_event = bot.ignore_for_event
        self.path = None


    def set_path(self, path):
        self.path = path