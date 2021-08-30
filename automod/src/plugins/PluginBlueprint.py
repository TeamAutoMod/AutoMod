import discord
from discord.ext import commands

from functools import wraps

from ..utils.SlashCommand import SlashCommand



class PluginBlueprint(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.cache = bot.cache
        self.i18next = bot.i18next
        self.emotes = bot.emotes
        self.schemas = bot.schemas
        self.action_validator = bot.action_validator
        self.action_logger = bot.action_logger
        self.ignore_for_event = bot.ignore_for_event
        self.path = None


    def set_path(self, path):
        self.path = path


    def t(self, guild, key, _emote=None, **kwargs):
        return self.translator.translate(guild, key, _emote=_emote, **kwargs)