# type: ignore

import discord
from discord.ext import commands

import logging; log = logging.getLogger()
import time
import traceback
import ast
import psutil
import datetime
from toolbox import S as Object

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, E
from ...views import DeleteView



class AdminPlugin(AutoModPluginBlueprint):
    """Plugin for all bot admin commands/events"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)

    
    def insert_returns(
        self, 
        body: str
    ) -> None:
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
        
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)


    def parse_shard_info(
        self, 
        shard: discord.ShardInfo
    ) -> str:
        guilds = len(list(filter(lambda x: x.shard_id == shard.id, self.bot.guilds)))
        if not shard.is_closed():
            text = "+ {}: CONNECTED ~ {} guilds".format(shard.id, guilds)
        else:
            text = "- {}: DISCONNECTED ~ {} guilds".format(shard.id, guilds)
        return text

    
    @AutoModPluginBlueprint.listener()
    async def on_member_udpate(
        self,
        b: discord.Member,
        a: discord.Member
    ) -> None:
        if a.roles != b.roles:
            r = b.guild.get_role(self.config.premium_role)
            if not r in b.roles and r in a.roles:
                print("PREMIUM")


    @commands.command()
    @commands.is_owner()
    async def eval(
        self, 
        ctx: commands.Context, 
        *, 
        cmd: str
    ) -> None:
        """
        eval_help
        examples:
        -eval 1+1
        """
        view = DeleteView(ctx.author.id)
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
                "Embed": Embed,
                "__import__": __import__
            }

            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))
            t2 = time.perf_counter()

            await ctx.send("*Executed in {}ms* \n```py\n{}\n```".format(round((t2 - t1) * 1000, 6), result), view=view)
        except Exception:
            ex = traceback.format_exc()
            await ctx.send("```py\n{}\n```".format(ex), view=view)


    @commands.command()
    @commands.is_owner()
    async def debug(
        self, 
        ctx: commands.Context
    ) -> None:
        """
        debug_help
        examples:
        -debug
        """
        e = Embed(ctx)
        d, h, m, s = self.bot.get_uptime(True)
        e.add_field(
            name="__AutoMod Statistics__",
            value="**• Last startup:** {} \n**• RAM usage:** {}% \n**• CPU usage:** {}%"\
                .format(
                    f"<t:{round((datetime.datetime.utcnow() - datetime.timedelta(days=d, hours=h, minutes=m, seconds=s)).timestamp())}>", 
                    round(psutil.virtual_memory().percent, 2),
                    round(psutil.cpu_percent())
                )
        )
        shards = [self.parse_shard_info(x) for x in self.bot.shards.values()]
        e.add_field(
            name="__{} ({})__".format(self.bot.user.name, self.bot.user.id),
            value="**• Guilds:** {} \n**• Latency:** {}ms \n**• Total shards:** {} \n**• Shard Connectivity:** \n```diff\n{}\n```"\
            .format(
                len(self.bot.guilds),
                round(self.bot.latency * 1000, 2), 
                len(self.bot.shards),
                "\n".join(shards)
            )
        )

        await ctx.send(embed=e)


    @commands.command()
    @commands.is_owner()
    async def mutuals(
        self,
        ctx: commands.Context,
        user: discord.User
    ) -> None:
        """
        mutuals_help
        examples:
        -mutuals paul#0009
        -mutuals 543056846601191508
        """
        guilds = [x for x in self.bot.guilds if x.get_member(user.id) != None]
        e = Embed(
            None,
            description="```\n{}\n```".format(
                "\n".join(
                    [
                        f"{x.id} | {len(x.members)} {' ' * abs(len(str(len(x.members))) - len(str(max([len(_.members) for _ in guilds]))))}| {x.name}" for x in guilds
                    ] if len(guilds) > 0 else "None"
                )
            )
        )
        await ctx.send(embed=e)


    @commands.command()
    @commands.is_owner()
    async def stats(
        self,
        ctx: commands.Context
    ) -> None:
        """
        stats_help
        examples:
        -stats
        """
        msg = []
        for i, (k, v) in enumerate(dict(
            sorted(
                self.bot.event_stats.items(), 
                key=lambda i: i[1],
                reverse=True
            )
        ).items()):
            if i == 0:
                msg.append(
                    f" EVENT{' ' * abs(len('EVENT') - max([len(x) for x, _ in self.bot.event_stats.items()]))} | COUNT" + \
                    f"\n{'-------' + '-' * abs(len('EVENT') - max([len(x) for x, _ in self.bot.event_stats.items()]))}|{'-' * 15}"
                )
            msg.append(f" {k}{' ' * abs(len(k) - max([len(x) for x, _ in self.bot.event_stats.items()]))} | {v}")
        
        await ctx.send("```js\n{}\n```".format(
            "\n".join(msg[0:10])
        ))

    
    @commands.group()
    @commands.is_owner()
    async def premium(
        self,
        ctx: commands.Context
    ) -> None:
        """
        premium_help
        examples:
        -premium
        -premium add 123456789
        -premium remove 123456789
        """
        if ctx.invoked_subcommand == None:
            if len(list(self.db.configs.find({"premium": True}))) < 1:
                await ctx.send(embed=E(self.locale.t(ctx.guild, "no_premiums", _emote="NO"), 0))
            else:
                e = Embed(
                    ctx,
                    title="Active premium servers"
                )
                for x in self.db.configs.find({"premium": True}):
                    data = Object(x)
                    e.add_field(
                        name=f"**{self.bot.get_guild(int(data.id))} ({data.id})**",
                        value=f"> ``{data.premium_type}``"
                    )
                await ctx.send(embed=e)


    @premium.command()
    @commands.is_owner()
    async def add(
        self,
        ctx: commands.Context,
        guild_id: int
    ) -> None:
        """
        premium_add_help
        examples:
        -premium add 123456789
        """
        if self.db.configs.get(guild_id, "premium") == True:
            return await ctx.send(embed=E(self.locale.t(ctx.guild, "premium_alr_enabled", _emote="NO"), 0))
        else:
            self.db.configs.multi_update(guild_id, {
                "premium": True,
                "premium_type": "lifetime"
            })
            await ctx.send(embed=E(self.locale.t(ctx.guild, "enabled_premium", _emote="YES"), 1))


    @premium.command()
    @commands.is_owner()
    async def remove(
        self,
        ctx: commands.Context,
        guild_id: int
    ) -> None:
        """
        premium_remove_help
        examples:
        -premium remove 123456789
        """
        if self.db.configs.get(guild_id, "premium") == False:
            return await ctx.send(embed=E(self.locale.t(ctx.guild, "premium_not_enabled", _emote="NO"), 0))
        else:
            self.db.configs.multi_update(guild_id, {
                "premium": False,
                "premium_type": ""
            })
            await ctx.send(embed=E(self.locale.t(ctx.guild, "disabled_premium", _emote="YES"), 1))


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(AdminPlugin(bot))