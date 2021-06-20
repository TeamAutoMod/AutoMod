import discord
from discord.ext import commands

from Plugins.Base import BasePlugin
from Database import Connector, DBUtils
from i18n import Translator



class Archive(BasePlugin):
    def __init__(self, bot):
        super(Archive, self).__init__(bot)


    @commands.group()
    @commands.has_permissions(manage_messages=True)
    async def archive(self, ctx):
        """archive_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="archive")


    @archive.command()
    @commands.has_permissions(manage_messages=True)
    async def here(self, ctx, amount=100):
        if amount > 2000:
            return await ctx.send(Translator.translate(ctx.guild, "max_amount"))




def setup(bot):
    bot.add_cog(Archive(bot))