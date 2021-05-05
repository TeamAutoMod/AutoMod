import os
import asyncio
import time
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from i18n import Translator
from Utils import Logging, Utils, guild_info
from Utils.Converters import DiscordUser, Guild

from Database import Connector, DBUtils
from Plugins.Base import BasePlugin


db = Connector.Database()



class Utility(BasePlugin):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def jumbo(self, ctx, emoji: discord.Emoji):
        """jumbo_help"""
        await ctx.send(f"{emoji.url}")


    @commands.command(aliases=["info"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(embed_links=True)
    async def userinfo(self, ctx, user: DiscordUser = None):
        """userinfo_help"""
        try:
            if user is None:
                user = member = ctx.author
            else:
                member = None if ctx.guild is None else await Utils.get_member(self.bot, ctx.guild, user.id)
            
            e = discord.Embed(
                color=discord.Color.blurple()
            )

            e.set_thumbnail(url=user.avatar_url)

            created = user.created_at.strftime("%d/%m/%Y %H:%M")
            e.add_field(
                name="User Information",
                value=f"Name: **{user.name}#{user.discriminator}** \nUser ID: {user.id} \n**Created: ({(datetime.fromtimestamp(time.time()) - user.created_at).days} days ago** (``{created} UTC``) \nProfile: {user.mention} \n ",
                inline=False
            )

            if member is not None:
                try:
                    roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
                except Exception:
                    roles = ["No roles"]
                
                joined = member.joined_at.strftime("%d/%m/%Y %H:%M")
                e.add_field(
                    name="Member Information",
                    value=f"Joined: **{(datetime.fromtimestamp(time.time()) - member.joined_at).days} days ago** (``{joined} UTC``) \nRoles: {', '.join(roles) if len(roles) < 20 else f'{len(roles)} roles'} \n ",
                    inline=False
                )

                warns = len([x for x in db.warns.find() if str(x["warnId"].split("-")[1]) == str(member.id)])
                e.add_field(
                    name="Cases",
                    value="Total: **{}**".format(warns if warns >= 1 else "0 😇"),
                    inline=False
                )

            await ctx.send(embed=e)
        except Exception:
            ex = traceback.format_exc()
            print(ex)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def server(self, ctx, guild: Guild = None):
        """server_help"""
        if guild is None:
            guild = ctx.guild
        e = guild_info.guild_info_embed(guild)
        await ctx.send(embed=e)
        

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def avatar(self, ctx, user: DiscordUser = None):
        """avatar_help"""
        if user is None:
            user = ctx.author
        e = discord.Embed(
            color=discord.Color.blurple(),
            title="{}'s Avatar".format(user.name)
        )
        e.set_image(
            url=user.avatar_url
        )
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """cleanup_help"""
        strategy = Utils.basic_cleaning
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = Utils.complex_cleaning
        
        deleted = await strategy(ctx, search)
        await ctx.send(Translator.translate(ctx.guild, "clean_success", _emote="YES", deleted=deleted, plural="" if deleted == 1 else "s"))
        

def setup(bot):
    bot.add_cog(Utility(bot))