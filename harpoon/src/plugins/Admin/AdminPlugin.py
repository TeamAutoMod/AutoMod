import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from ..Types import DiscordUserID
from .commands import Shutdown, Load, Unload, Reload, Charinfo, Eval, Mutuals, Allow, Unallow



class AdminPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)

    
    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in self.bot.config["bot_admins"]


    @commands.command()
    async def shutdown(
        self, 
        ctx
    ):
        await Shutdown.run(self, ctx)


    @commands.command()
    async def load(
        self, 
        ctx,
        plugin: str
    ):
        await Load.run(self, ctx, plugin)


    @commands.command()
    async def unload(
        self, 
        ctx,
        plugin: str
    ):
        await Unload.run(self, ctx, plugin)


    @commands.command(name="reload")
    async def _reload(
        self, 
        ctx,
        plugin: str
    ):
        await Reload.run(self, ctx, plugin)


    @commands.command()
    async def charinfo(
        self,
        ctx,
        *,
        chars: str
    ):
        await Charinfo.run(self, ctx, chars)


    @commands.command()
    async def eval(
        self,
        ctx,
        *,
        cmd: str
    ):
        await Eval.run(self, ctx, cmd)


    @commands.command()
    async def mutuals(
        self, 
        ctx,
        user: DiscordUserID
    ):
        await Mutuals.run(self, ctx, user)


    @commands.command(aliases=["allow_server", "allow_guild"])
    async def allow(
        self,
        ctx,
        guild_id
    ):
        await Allow.run(self, ctx, guild_id)


    @commands.command(aliases=["unallow_server", "unallow_guild"])
    async def unallow(
        self,
        ctx,
        guild_id
    ):
        await Unallow.run(self, ctx, guild_id)
        



def setup(bot):
    pass