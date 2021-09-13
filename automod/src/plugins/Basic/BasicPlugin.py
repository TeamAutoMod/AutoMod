import discord
from discord.ext import commands

import googletrans

from ..PluginBlueprint import PluginBlueprint
from .commands import (
    About, 
    Ping, 
    Help, 
    Server, 
    Userinfo, 
    Avatar,
    Asciify, 
    Translate,
    Dashboard
)

from ..Types import DiscordUser



class BasicPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.google = googletrans.Translator()

    
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


    @commands.command(aliases=["av"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def avatar(
        self,
        ctx,
        user: DiscordUser = None
    ):
        """avatar_help"""
        await Avatar.run(self, ctx, user)



    # @commands.command()
    # @commands.guild_only()
    # @commands.has_permissions(manage_nicknames=True)
    # async def asciify(
    #     self,
    #     ctx,
    #     user: discord.Member
    # ):
    #     """asciify_help"""
    #     await Asciify.run(self, ctx, user)


    # @commands.command()
    # @commands.guild_only()
    # async def translate(
    #     self,
    #     ctx,
    #     *,
    #     text: str = None
    # ):
    #     """translate_help"""
    #     await Translate.run(self, ctx, text)


    # @commands.command()
    # @commands.guild_only()
    # async def dashboard(
    #     self,
    #     ctx,
    # ):
    #     """dashboard_help"""
    #     await Dashboard.run(self, ctx)


def setup(bot):
    pass