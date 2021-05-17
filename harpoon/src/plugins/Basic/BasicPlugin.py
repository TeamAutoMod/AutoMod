import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .commands import About, Ping, Help



class BasicPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)

    
    @commands.command()
    async def about(
        self, 
        ctx
    ):
        """about_help"""
        await About.run(self, ctx)


    @commands.command()
    async def ping(
        self, 
        ctx
    ):
        """ping_help"""
        await Ping.run(self, ctx)


    @commands.command()
    async def help(
        self, 
        ctx, 
        *, 
        query: str = None
    ):
        """help_help"""
        await Help.run(self, ctx, query)



def setup(bot):
    pass