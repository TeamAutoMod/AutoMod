import asyncio
import time
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from i18n import Translator
from Plugins.Base import BasePlugin
from Database import Connector, DBUtils
from Utils import Pages, Generators, Logging


class Basic(BasePlugin):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def about(self, ctx):
        """about_help"""
        uptime = datetime.utcnow() - self.bot.uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        days, hours = divmod(hours, 24)
        minutes, seconds = divmod(remainder, 60)
        user_messages = str(self.bot.user_messages)
        bot_messages = str(self.bot.bot_messages)
        own_messages = str(self.bot.own_messages)
        total_users = str(sum(len(guild.members) for guild in self.bot.guilds))
        unique_users = str(len(self.bot.users))
        command_count = str(self.bot.command_count)
        custom_command_count = str(self.bot.custom_command_count)

        e = discord.Embed(
            color=discord.Color.blurple(),
            title=Translator.translate(ctx.guild, "about"),
            description="• [Support](https://discord.gg/S9BEBux) \n• [GitHub](https://github.com/xezzz/AutoMod)"
        )
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.add_field(
            name="Status",
            value=f"""```\n• Uptime: {days}d, {hours}h, {minutes}m & {seconds}s \n• Version: {self.bot.version} \n• Latency: {round(self.bot.latency * 1000)}ms \n• Timezone: UTC \n```""",
            inline=False
        )
        e.add_field(
            name="Stats",
            value=f"```\n• Guilds: {len(self.bot.guilds)} \n• Users: {total_users} ({unique_users} unique) \n• Bot Messages: {bot_messages} \n• Own Messages: {own_messages} \n• User Messages: {user_messages} \n• Commands Used: {command_count} (Custom: {custom_command_count}) \n```",
            inline=False
        )
        await ctx.send(embed=e)


    @commands.command()
    async def ping(self, ctx):
        "ping_help"
        t1 = time.perf_counter()
        message = await ctx.send("⏳ Pinging...")
        t2 = time.perf_counter()
        rest = round((t2 - t1) * 1000)
        latency = round(self.bot.latency * 1000, 2)
        shard_latency =  round([x for i, x in self.bot.shards.items() if i == ctx.guild.shard_id][0].latency * 1000, 2)

        e = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.blurple(),
            description="```• Client Latency: {}ms \n• REST API Ping: {}ms \n• Shard Latency: {}ms \n```".format(latency, rest, shard_latency)
        )
        await message.edit(content=None, embed=e)
        



    @commands.command()
    @commands.bot_has_permissions(external_emojis=True, add_reactions=True)
    async def help(self, ctx, *, query: str = None):
        """help_help"""
        if query is None:
            contents = await Generators.get_all_command_help_embed(ctx, self.bot)
            pages = len(contents)
            cur_page = 1
            message = await ctx.send(embed=contents[cur_page-1])

            await message.add_reaction("◀️") 
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        await message.edit(embed=contents[cur_page-1])
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        await message.edit(embed=contents[cur_page-1])
                        await message.remove_reaction(reaction, user)

                    else:
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break
        else:
            query = "".join(query.splitlines())

            cmd_help_embed = Generators.get_command_help_embed(self.bot, ctx, query)
            if cmd_help_embed is None:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_command"))
            else:
                return await ctx.send(embed=cmd_help_embed)
                




def setup(bot):
    bot.add_cog(Basic(bot))