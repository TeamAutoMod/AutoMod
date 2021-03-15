import os
import ast
import json
import traceback
import datetime
import logging

import discord
from discord import Guild
from discord.ext import commands

import i18n
from Cogs.Base import BaseCog
from Utils import Utils, Logging, Pages, Reload
from Utils.Constants import GREEN_TICK, RED_TICK
from Database.Connector import Database
from Utils.Converters import UserID



log = logging.getLogger(__name__)


class Admin(BaseCog):
    """No translation needed here"""
    def __init__(self, bot):
        super().__init__(bot)


    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in Utils.from_config("BOT_ADMINS")


    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        await ctx.send("😴 Executing clean shutdown")
        await Utils.clean_shutdown(self.bot, ctx.author.name)


    @commands.command(hidden=True)
    async def load(self, ctx, cog):
        if os.path.isfile(f"Cogs/{cog}.py") or os.path.isfile(f"./Cogs/{cog}.py"):
            self.bot.load_extension("Cogs.%s" % (cog))
            await ctx.send(f"**{cog}** has been loaded!")
            await Logging.bot_log(self.bot, f"**{cog}** has been loaded by {ctx.message.author.name}.", None)
        else:
            await ctx.send(f"{RED_TICK} I can't find a cog with that name.")


    @commands.command(hidden=True)
    async def unload(self, ctx, cog):
        if os.path.isfile(f"Cogs/{cog}.py") or os.path.isfile(f"./Cogs/{cog}.py"):
            self.bot.unload_extension("Cogs.%s" % (cog))
            await ctx.send(f"**{cog}** has been unloaded!")
            await Logging.bot_log(self.bot, f"**{cog}** has been unloaded by {ctx.message.author.name}.", None)
        else:
            await ctx.send(f"{RED_TICK} I can't find a cog with that name.")


    @commands.command(hidden=True)
    async def reload(self, ctx, cog):
        if os.path.isfile(f"Cogs/{cog}.py") or os.path.isfile(f"./Cogs/{cog}.py"):
            self.bot.reload_extension("Cogs.%s" % (cog))
            await ctx.send(f"**{cog}** has been reloaded!")
            await Logging.bot_log(self.bot, f"**{cog}** has been reloaded by {ctx.message.author.name}.", None)
        else:
            await ctx.send(f"{RED_TICK} I can't find a cog with that name.")


    @commands.command(aliases=["eval"], hidden=True)
    async def _eval(self, ctx, *, cmd):
        try:
            
            def insert_returns(body):
                if isinstance(body[-1], ast.Expr):
                    body[-1] = ast.Return(body[-1].value)
                    ast.fix_missing_locations(body[-1])
                
                if isinstance(body[-1], ast.If):
                    insert_returns(body[-1].body)
                    insert_returns(body[-1].orelse)

                if isinstance(body[-1], ast.With):
                    insert_returns(body[-1].body)
            
            fn_name = "_eval_expr"

            cmd = cmd.strip("` ")

            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)

            env = {
                "this": ctx.message,
                "db": Database(),
                "bot": ctx.bot,
                "discord": discord,
                "commands": commands,
                "client": self.bot,
                "ctx": ctx,
                "__import__": __import__
            }

            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))

            await ctx.message.add_reaction(GREEN_TICK)
            await ctx.send("```py\n{}\n```".format(result))
        except Exception:
            error = traceback.format_exc()
            await ctx.message.add_reaction(RED_TICK)
            await ctx.send("```py\n{}\n```".format(error))


    @commands.command(hidden=True)
    async def block_server(self, ctx, guild: Guild):
        with open("./blocked_guilds.json", "r", encoding="utf8", errors="ignore") as f:
            blocked = json.load(f)
        blocked[f"{guild.id}"] = {}
        blocked[f"{guild.id}"]["owner"] = f"{guild.owner.id}"
        await ctx.send(f"{GREEN_TICK} {guild.name} (``{guild.id}``) has been blocked")
        await guild.leave()
        await Logging.bot_log(self.bot, f"{guild.name} (``{guild.id}``) has been blocked by {ctx.author}")
        with open("./blocked_guilds.json", "w", encoding="utf8", errors="ignore") as f:
            json.dump(blocked, f)


    @commands.command(hidden=True)
    async def mutuals(self, ctx, user: UserID):
        try:
            mutuals = []
            for g in self.bot.guilds:
                if g.get_member(user) is not None:
                    mutuals.append(g)
            for p in Pages.paginate("\n".join(f"{guild.id} - {guild.name}" for guild in mutuals), prefix="```py\n", suffix="```"):
                await ctx.send(p)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    async def hot_reload(self, ctx):
        msg = await ctx.send("🔁 Initiating hot reload...")
        await Reload._reload(ctx.author.name, self.bot)
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.bot.last_reload = f"{now} UTC"
        await msg.edit(content=f"<:greenTick:751915988143833118> Hot reload completed, now running on version ``{self.bot.version}``")

        
    @commands.command()
    async def reload_i18n(self, ctx, langs = None):
        try:
            if langs is None:
                langs = Utils.from_config("SUPPORTED_LANGS")
            log.info("[Translator] Reloading translator")
            await i18n.Translator.init_translator(langs)
            log.info("[Translator] Reloaded translator")
            await ctx.send("<:greenTick:751915988143833118> Reloaded the translator & the i18n files!")
        except Exception as ex:
            await ctx.send(f"Error while reloading i18n stuff: \n{ex}")


def setup(bot):
    bot.add_cog(Admin(bot))