import discord
from discord.ext import commands

import logging; log = logging.getLogger()
import time
import traceback
import ast
import psutil
import datetime

from . import AutoModPlugin, ShardedBotInstance
from ..types import Embed
from ..views import DeleteView



class AdminPlugin(AutoModPlugin):
    """Plugin for all bot admin commands/events"""
    def __init__(self, bot: ShardedBotInstance) -> None:
        super().__init__(bot)

    
    def insert_returns(self, body: str) -> None:
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
        
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)


    def parse_shard_info(self, shard: discord.ShardInfo) -> str:
        guilds = len(list(filter(lambda x: x.shard_id == shard.id, self.bot.guilds)))
        if not shard.is_closed():
            text = "+ {}: CONNECTED ~ {} guilds".format(shard.id, guilds)
        else:
            text = "- {}: DISCONNECTED ~ {} guilds".format(shard.id, guilds)
        return text


    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: commands.Context, *, cmd: str) -> None:
        """
        eval_help
        examples:
        -eval 1+1
        """
        view = DeleteView()
        try:
            t1 = time.perf_counter()
            fn_name = "_eval_expr"

            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            self.insert_returns(body)

            env = {
                "this": ctx,
                "ctx": ctx,
                "db": self.bot.db,
                "bot": self.bot,
                "client": self.bot,
                "discord": discord,
                "commands": commands,
                "__import__": __import__
            }

            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))
            t2 = time.perf_counter()

            await ctx.send("*Executed in {}ms* \n```py\n{}\n```".format(round((t2 - t1) * 1000, 6), result), view=view)
        except Exception:
            ex = traceback.format_exc()
            await ctx.send("```py\n{}\n```".format(ex), view=view)


    @commands.is_owner()
    @commands.command()
    async def debug(self, ctx: commands.Context) -> None:
        """
        debug_help
        examples:
        -debug
        """
        e = Embed(ctx)
        d, h, m, s = self.bot.get_uptime(True)
        e.add_field(
            name="❯ AutoMod Statistics",
            value="> **• Last startup:** {} \n> **• RAM usage:** {}% \n> **• CPU usage:** {}%"\
                .format(
                    f"<t:{round((datetime.datetime.utcnow() - datetime.timedelta(days=d, hours=h, minutes=m, seconds=s)).timestamp())}>", 
                    round(psutil.virtual_memory().percent, 2),
                    round(psutil.cpu_percent())
                )
        )
        shards = [self.parse_shard_info(x) for x in self.bot.shards.values()]
        e.add_field(
            name="❯ {} ({})".format(self.bot.user.name, self.bot.user.id),
            value="> **• Guilds:** {} \n> **• Latency:** {}ms \n> **• Total shards:** {} \n> **• Shard Connectivity:** \n```diff\n{}\n```"\
            .format(
                len(self.bot.guilds),
                round(self.bot.latency * 1000, 2), 
                len(self.bot.shards),
                "\n".join(shards)
            )
        )

        await ctx.send(embed=e)


async def setup(bot) -> None: await bot.register_plugin(AdminPlugin(bot))