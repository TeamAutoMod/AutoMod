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
from Cogs.Base import BaseCog


db = Connector.Database()



class Utility(BaseCog):
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
            e.add_field(
                name="**Username**",
                value=f"{user.name}#{user.discriminator}",
                inline=True
            )
            e.add_field(
                name="**ID**",
                value=user.id,
                inline=True
            )
            e.add_field(
                name="**Bot?**",
                value=user.bot,
                inline=True
            )
            e.add_field(
                name="**Mention**",
                value=user.mention,
                inline=True
            )
            e.add_field(
                name="**Avatar**",
                value="[Avatar]({})".format(user.avatar_url),
                inline=True
            )
            if member is not None:
                e.add_field(
                    name="**Nickname**",
                    value=member.nick,
                    inline=True
                )
                try:
                    roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
                    e.add_field(
                        name="**Roles**",
                        value=", ".join(roles) if len(roles) < 20 else f"{len(roles)} roles",
                        inline=False
                    )
                except Exception as e:
                    print(e)
                    e.add_field(
                        name="**Roles**",
                        value="No roles",
                        inline=False
                    )
                mutes = len([x for x in db.warns.find() if str(x["warnId"].split("-")[1]) == str(member.id)])
                e.add_field(
                    name="**Warns**",
                    value=mutes if mutes > 0 else "0 😇",
                    inline=True
                )
                
                joined = member.created_at.strftime("%d/%m/%Y")
                e.add_field(
                    name="**Joined**",
                    value=f"{joined} \n({(datetime.fromtimestamp(time.time()) - member.joined_at).days} days ago)",
                    inline=True
                )

            created = user.created_at.strftime("%d/%m/%Y")
            e.add_field(
                name="**Created**",
                value=f"{created} \n({(datetime.fromtimestamp(time.time()) - user.created_at).days} days ago)",
                inline=True
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