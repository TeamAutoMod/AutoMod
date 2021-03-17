import asyncio
import time
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from i18n import Translator
from Cogs.Base import BaseCog
from Database import Connector, DBUtils
from Utils import Pages, Generators, Logging


class Basic(BaseCog):
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
            description=f"""
            **{Translator.translate(ctx.guild, "about")}**
            {Translator.translate(
                ctx.guild, 
                "about_text",
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                user_messages=user_messages,
                bot_messages=bot_messages,
                own_messages=own_messages,
                command_count=command_count,
                custom_command_count=custom_command_count,
                guilds=len(self.bot.guilds),
                total_users=total_users,
                unique_users=unique_users,
                version=self.bot.version
            )}
            """
        )
        e.add_field(name="Support", value="[Here](https://discord.gg/S9BEBux)")
        e.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=e)


    @commands.command()
    async def ping(self, ctx):
        "ping_help"
        t1 = time.perf_counter()
        message = await ctx.send("⏳ Pinging...")
        t2 = time.perf_counter()
        rest = round((t2 - t1) * 1000)
        latency = round(self.bot.latency * 1000, 2)
        await message.edit(
            content=f"🏓 Pong! Client Latency: {latency} ms | REST API ping: {rest} ms"
        )


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
            if not query in [_.name for _ in client.commands]:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_command"))
            
            help_message = Translator.translate(ctx.guild, f"{query.lower()}_help")
            if help_message is None:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_command"))
                
            self.bot.help_command.context = ctx
            try:
                usage = self.bot.help_command.get_command_signature(command = self.bot.get_command(query.lower()))
            except Exception:
                return await ctx.send(Translator.translate(ctx.guild, "invalid_command"))
                
            try:
                group = [x for x in self.bot.get_command(query.lower()).cog.walk_commands() if x.name == f"{query.lower()}"]
                commands = ["{}".format(Generators.generate_help(ctx, y)) for y in group[0].commands]
            except Exception:
                commands = []
                
            await ctx.send("```diff\n{}\n\n{}\n{}```".format(usage, help_message, "\n{}\n{}".format("Subcommands: " if len(commands) >= 1 else "", "\n".join(commands if len(commands) > 0 else ""))))




def setup(bot):
    bot.add_cog(Basic(bot))