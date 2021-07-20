import discord
from discord.ext import commands

<<<<<<< HEAD
import googletrans

from ..PluginBlueprint import PluginBlueprint
from .commands import About, Ping, Help, Server, Userinfo, Asciify, Translate
=======
from ..PluginBlueprint import PluginBlueprint
from .commands import About, Ping, Help, Server, Userinfo, Asciify
>>>>>>> f40ed3caff6b455cf03f56d37f925532425549d2

from ..Types import DiscordUser



class BasicPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
<<<<<<< HEAD
        self.google = googletrans.Translator()
=======
>>>>>>> f40ed3caff6b455cf03f56d37f925532425549d2

    
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


<<<<<<< HEAD
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def translate(
        self,
        ctx,
        *,
        text: str = None
    ):
        """translate_help"""
        await Translate.run(self, ctx, text)


=======
>>>>>>> f40ed3caff6b455cf03f56d37f925532425549d2
def setup(bot):
    pass