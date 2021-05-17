import discord
from discord.ext import commands



class NotCachedError(commands.CheckFailure):
    pass



class PostParseError(commands.BadArgument):
    def __init__(self, type, error):
        super().__init__(None)
        self.type = type
        self.error = error