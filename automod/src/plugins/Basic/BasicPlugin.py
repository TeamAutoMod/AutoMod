import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .commands import About, Ping, Help, Server, Userinfo, Asciify

from ..Types import DiscordUser



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


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def server(
        self,
        ctx
    ):
        """server_help"""
        await Server.run(self, ctx)


    @commands.command(aliases=["whois"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def userinfo(
        self,
        ctx,
        user: DiscordUser = None
    ):
        """userinfo_help"""
        await Userinfo.run(self, ctx, user)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def asciify(
        self,
        ctx,
        user: discord.Member
    ):
        """asciify_help"""
        await Asciify.run(self, ctx, user)


def setup(bot):
    pass