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
            title=Translator.translate(ctx.guild, "about")
        )
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.add_field(
            name="Status",
            value=f"""
<<<<<<< HEAD
            Uptime: **{days}d, {hours}h, {minutes}m & {seconds}s**
            Version: **{self.bot.version}**
            Latency: **{round(self.bot.latency * 1000)}ms**
            Timezone: **UTC**
=======
            ```
            • Uptime: **{days}d, {hours}h, {minutes}m & {seconds}s**
            • Version: **{self.bot.version}**
            • Latency: **{round(self.bot.latency * 1000)}**
            • Timezone: **UTC**
            ```
>>>>>>> 9944d09c307ffa06c86aeec2453c71055c88e73e
            """,
            inline=False
        )
        e.add_field(
            name="Stats",
            value=f"""
            ```
            • Guilds: **{len(self.bot.guilds)}**
            • Users: **{total_users} ({unique_users} unique)**
            • Bot Messages: **{bot_messages}**
            • Own Messages: **{own_messages}**
            • User Messages: **{user_messages}**
            • Commands Used: **{command_count} (Custom: {custom_command_count})**
            ```
            """,
            inline=False
        )

        e.add_field(name="Links", value="• [Support](https://discord.gg/S9BEBux) \n• [GitHub](https://github.com/xezzz/AutoMod)")
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
            contents = await Generators.generate_help_pages(ctx, self.bot)
            pages = len(contents)
            cur_page = 1
            message = await ctx.send(f"**{Translator.translate(ctx.guild, 'command_list')} {cur_page}/{pages}**:\n{contents[cur_page-1]}")

            await message.add_reaction("◀️") 
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        await message.edit(content=f"**{Translator.translate(ctx.guild, 'command_list')} {cur_page}/{pages}:**\n{contents[cur_page-1]}")
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        await message.edit(content=f"**{Translator.translate(ctx.guild, 'command_list')} {cur_page}/{pages}:**\n{contents[cur_page-1]}")
                        await message.remove_reaction(reaction, user)

                    else:
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break
        else:
            get_aliases = lambda t: [i for s in t for i in s] # [["1"], ["2"]] -> ["1", "2"]

            all_commands = [*[x.name for x in self.bot.commands], *get_aliases([y.aliases for y in self.bot.commands])]
            if not query in all_commands:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_command"))
            
            help_message = Translator.translate(ctx.guild, f"{self.bot.get_command(query).name.lower()}_help")
            if help_message is None:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_command"))
                
            self.bot.help_command.context = ctx
            try:
                usage = self.bot.help_command.get_command_signature(command=self.bot.get_command(query.lower()))
            except Exception:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_command"))
                
            try:
                query = self.bot.get_command(query).name # get the actual command name
                group = [x for x in self.bot.get_command(query.lower()).cog.walk_commands() if x.name == f"{query.lower()}"]
                commands = ["{}".format(Generators.generate_help(ctx, y)) for y in group[0].commands]
            except Exception:
                commands = []

            e = discord.Embed(color=discord.Color.blurple(), title="Command Help")
            e.add_field(name="Description", value=f"```\n{help_message}\n```", inline=False)
            e.add_field(name="Usage", value=f"```\n{usage}\n```", inline=False)
            e.add_field(name="Subcommands", value="{}".format("\n".join(commands if len(commands) > 0 else "None")), inline=False)
            await ctx.send(embed=e)
                
            #await ctx.send("```diff\n{}\n\n{}\n{}```".format(usage, help_message, "\n{}\n{}".format("Subcommands: " if len(commands) >= 1 else "", "\n".join(commands if len(commands) > 0 else ""))))




def setup(bot):
    bot.add_cog(Basic(bot))