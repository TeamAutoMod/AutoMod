import discord
from discord.ext import commands

import topgg

from ..PluginBlueprint import PluginBlueprint
from ..Types import DiscordUserID
from .commands import Shutdown, Load, Unload, Reload, Charinfo, Eval, Mutuals, Block, Unblock, Debug
from .events import OnGuildJoin, OnGuildRemove, OnAutopostSuccess



class AdminPlugin(PluginBlueprint):
    def __init__(self, bot): 
        super().__init__(bot)
        bot.topggpy = topgg.DBLClient(bot, bot.config["dbl_token"], autopost=True, post_shard_count=True)

    
    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in self.bot.config["bot_admins"]


    @commands.Cog.listener()
    async def on_guild_join(
        self,
        guild
    ):
        await OnGuildJoin.run(self, guild)


    @commands.Cog.listener()
    async def on_guild_remove(
        self,
        guild
    ):
        await OnGuildRemove.run(self, guild)


    @commands.Cog.listener()
    async def on_autopost_success(
        self
    ):
        await OnAutopostSuccess.run(self)
        


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


    @commands.command(aliases=["block_server", "block_guild"])
    async def block(
        self,
        ctx,
        guild_id
    ):
        await Block.run(self, ctx, guild_id)


    @commands.command(aliases=["unblock_server", "unblock_guild"])
    async def unblock(
        self,
        ctx,
        guild_id
    ):
        await Unblock.run(self, ctx, guild_id)


    @commands.command()
    async def debug(
        self,
        ctx
    ):
        await Debug.run(self, ctx)
        



def setup(bot):
    pass