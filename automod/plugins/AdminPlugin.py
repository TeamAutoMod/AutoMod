import discord
from discord.ext import commands

import topgg
import logging
import ast
import traceback
import time
import psutil
import discordspy

from .PluginBlueprint import PluginBlueprint
from .Types import DiscordUserID, Embed
from utils.Utils import toStr, parseShardInfo



log = logging.getLogger(__name__)


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class AdminPlugin(PluginBlueprint):
    def __init__(self, bot): 
        super().__init__(bot)
        if not bot.config.dev:
            bot.topggpy = topgg.DBLClient(bot, bot.config.dbl_token, autopost=True, post_shard_count=True)

    
    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in self.bot.config.bot_admins


    @commands.Cog.listener()
    async def on_guild_join(
        self,
        guild
    ):
        log.info(f"Joined guild: {guild.name} ({guild.id})")
        if guild is None:
            return
        try:
            await guild.chunk(cache=True)
        except Exception:
            log.warn(f"Failed to chunk guild {guild.name} ({guild.id})")
            pass
        finally:
            self.cache.build_for_guild(guild)
            if not self.db.configs.exists(guild.id):
                self.db.configs.insert(self.schemas.GuildConfig(guild))


    @commands.Cog.listener()
    async def on_guild_remove(
        self,
        guild
    ):
        if guild is None:
            return
        self.cache.destroy(guild_id=guild.id)
        if self.db.configs.exists(guild.id):
            self.db.configs.delete(guild.id)


    @commands.Cog.listener()
    async def on_autopost_success(
        self
    ):
        log.info("Posted server count ({}) and shard count ({})".format(self.bot.topggpy.guild_count, self.bot.shard_count))


    # @commands.Cog.listener()
    # async def on_discords_server_post(
    #     self,   
    #     status
    # ):
    #     if status == 200:
    #         log.info(f"Posted server count ({self.discords.servers()}) on discords.com")
    #     else:
    #         log.info(f"Failed to post server count to discords.com - Status code {status}")
        


    @commands.command()
    async def shutdown(
        self, 
        ctx
    ):
        await ctx.send(f"{self.emotes.get('SLEEP')} Executing clean shutdown")
        await self.bot.utils.cleanShutdown()


    @commands.command()
    async def load(
        self, 
        ctx,
        _plugin: str
    ):
        _plugin_ = self.bot.get_cog(_plugin)
        if _plugin_ is None:
            return await ctx.send(self.i18next.t(ctx.guild, "plugin_not_found", _emote="WARN"))
        else:
            try:
                self.bot.load_extension(_plugin_.path)
            except Exception as ex:
                await ctx.send(self.i18next.t(ctx.guild, "plugin_load_failed", _emote="WARN", exc=ex))
            else:
                await ctx.send(self.i18next.t(ctx.guild, "plugin_loaded", _emote="YES", plugin=str(_plugin_)))


    @commands.command()
    async def unload(
        self, 
        ctx,
        _plugin: str
    ):
        _plugin_ = self.bot.get_cog(_plugin)
        if _plugin_ is None:
            return await ctx.send(self.i18next.t(ctx.guild, "plugin_not_found", _emote="WARN"))
        else:
            try:
                self.bot.unload_extension(_plugin_.path)
            except Exception as ex:
                await ctx.send(self.i18next.t(ctx.guild, "plugin_unload_failed", _emote="WARN", exc=ex))
            else:
                await ctx.send(self.i18next.t(ctx.guild, "plugin_unloaded", _emote="YES", plugin=str(_plugin_)))


    @commands.command()
    async def charinfo(
        self,
        ctx,
        *,
        chars: str
    ):
        msg = "\n".join(map(toStr, chars))
        await ctx.ensure_sending("```\n{}\n```".format(msg))


    @commands.command()
    async def eval(
        self,
        ctx,
        *,
        cmd: str
    ):
        try:
            t1 = time.perf_counter()
            fn_name = "_eval_expr"

            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)

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

            await ctx.message.add_reaction(self.bot.emotes.get("YES"))
            await ctx.send("*Executed in {}ms* \n```py\n{}\n```".format(round((t2 - t1) * 1000, 6), result))
        except Exception:
            ex = traceback.format_exc()
            await ctx.message.add_reaction(self.bot.emotes.get("NO"))
            await ctx.send("```py\n{}\n```".format(ex))


    @commands.command()
    async def mutuals(
        self, 
        ctx,
        user: DiscordUserID
    ):
        try:
            mutuals = []
            for g in self.bot.guilds:
                if g.get_member(user) is not None:
                    mutuals.append(g.name)
            
            await ctx.send(embed=Embed(title=self.i18next.t(ctx.guild, "mutual_guilds"), description="```\n{}\n```".format("\n".join(mutuals))))
        except Exception as ex:
            await ctx.send(ex)


    @commands.command(aliases=["block_server", "block_guild"])
    async def block(
        self,
        ctx,
        guild_id
    ):
        guild_id = int(guild_id) 
        blocked_guilds = self.bot.config.blocked_guilds
        if guild_id in blocked_guilds:
            return await ctx.send(self.i18next.t(ctx.guild, "already_blocked", _emote="WARN"))
        
        self.bot.modify_config.block_guild(guild_id)
        await ctx.send(self.i18next.t(ctx.guild, "blocked_guild", _emote="YES", guild_id=guild_id))


    @commands.command(aliases=["unblock_server", "unblock_guild"])
    async def unblock(
        self,
        ctx,
        guild_id
    ):
        guild_id = int(guild_id) 
        blocked_guilds = self.bot.config.blocked_guilds
        if guild_id not in blocked_guilds:
            return await ctx.send(self.i18next.t(ctx.guild, "not_blocked", _emote="WARN"))

        g = discord.utils.get(self.bot.guilds, id=guild_id)
        if g is not None:
            await g.leave()
        
        self.bot.modify_config.unblock_guild(guild_id)
        await ctx.send(self.i18next.t(ctx.guild, "unblocked_guild", _emote="YES", guild_id=guild_id))


    @commands.command()
    async def debug(
        self,
        ctx
    ):
        e = Embed()
        e.add_field(
            name="❯ AutoMod Statistics",
            value="• Last startup: ``{}`` \n• RAM usage: ``{}%`` \n• CPU usage: ``{}%``"\
                .format(
                    self.bot.get_uptime(), 
                    round(psutil.virtual_memory().percent, 2),
                    round(psutil.cpu_percent())
                )
        )
        shards = [parseShardInfo(self, x) for x in self.bot.shards.values()]
        e.add_field(
            name="❯ {} ({})".format(self.bot.user.name, self.bot.user.id),
            value="• Guilds: ``{}`` \n• Latency: ``{}ms`` \n• Total shards: ``{}`` \n• Shard Connectivity: \n```diff\n{}\n```"\
            .format(
                len(self.bot.guilds),
                round(self.bot.latency * 1000, 2), 
                len(self.bot.shards),
                "\n".join(shards)
            )
        )

        await ctx.send(embed=e)



    @commands.command()
    async def command_stats(
        self,
        ctx
    ):
        spaces = abs(7 - len(list(sorted(self.bot.command_stats.keys(), key=lambda x: len(x), reverse=True))[0])) + 1
        base = f"Command{' ' * spaces}| Uses \n{'=' * 25}"
        table = []
        for command, uses in self.bot.command_stats.items():
            _spaces = abs(7 + spaces - len(command))
            table.append(
                f"{command}{' ' * _spaces}| {uses}"
            )
        
        table = sorted(table, key=lambda x: int(x.split("| ")[-1]), reverse=True)
        table.insert(0, base)

        e = Embed(
            title="Command Stats",
            description="```py\n{}\n```".format("\n".join(table))
        )
        await ctx.send(embed=e)
        



def setup(bot):
    bot.add_cog(AdminPlugin(bot))