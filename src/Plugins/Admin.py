import os
import ast
import json
import traceback
import datetime
import logging
import unicodedata

import discord
from discord import Guild
from discord.ext import commands

import i18n
from Plugins.Base import BasePlugin
from Utils import Utils, Logging, Pages, Reload
from Utils.Constants import GREEN_TICK, RED_TICK
from Database.Connector import Database
from Database import DBUtils
from Utils.Converters import UserID



log = logging.getLogger(__name__)


class Admin(BasePlugin):
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
        if os.path.isfile(f"src/Plugins/{cog}.py") or os.path.isfile(f"./Plugins/src/{cog}.py"):
            try:
                self.bot.load_extension("Plugins.%s" % (cog))
            except Exception as ex:
                return await ctx.send(f"{RED_TICK} Error! {ex}")
            await ctx.send(f"**{cog}** has been loaded!")
        else:
            await ctx.send(f"{RED_TICK} I can't find a cog with that name.")


    @commands.command(hidden=True)
    async def unload(self, ctx, cog):
        if os.path.isfile(f"src/Plugins/{cog}.py") or os.path.isfile(f"./src/Plugins/{cog}.py"):
            self.bot.unload_extension("Plugins.%s" % (cog))
            await ctx.send(f"**{cog}** has been unloaded!")
        else:
            await ctx.send(f"{RED_TICK} I can't find a cog with that name.")


    @commands.command(hidden=True)
    async def reload(self, ctx, cog):
        if os.path.isfile(f"src/Plugins/{cog}.py") or os.path.isfile(f"./src/Plugins/{cog}.py"):
            try:
                self.bot.reload_extension("Plugins.%s" % (cog))
            except Exception as ex:
                return await ctx.send(f"{RED_TICK} Error! {ex}")
            await ctx.send(f"**{cog}** has been reloaded!")
        else:
            await ctx.send(f"{RED_TICK} I can't find a cog with that name.")



    @commands.command()
    async def charinfo(self, ctx, *, chars: str):
        def to_str(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, "Name not found")
            return f"`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <https://fileformat.info/info/unicode/char/{digit}>"
            
        msg = "\n".join(map(to_str, chars))
        if len(msg) > 2000:
            return await ctx.send("Output is too long to display!")
        await ctx.send(msg)

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
                "DBUtils": DBUtils,
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


    # @commands.command(hidden=True)
    # async def block_server(self, ctx, guild: Guild):
    #     with open("./blocked_guilds.json", "r", encoding="utf8", errors="ignore") as f:
    #         blocked = json.load(f)
    #     blocked[f"{guild.id}"] = {}
    #     blocked[f"{guild.id}"]["owner"] = f"{guild.owner.id}"
    #     await ctx.send(f"{GREEN_TICK} {guild.name} (``{guild.id}``) has been blocked")
    #     await guild.leave()
    #     await Logging.bot_log(self.bot, f"{guild.name} (``{guild.id}``) has been blocked by {ctx.author}")
    #     with open("./blocked_guilds.json", "w", encoding="utf8", errors="ignore") as f:
    #         json.dump(blocked, f)


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
            log.info("Reloading translator")
            await i18n.Translator.init_translator(langs)
            log.info("Reloaded translator")
            await ctx.send("<:greenTick:751915988143833118> Reloaded the translator & the i18n files!")
        except Exception as ex:
            await ctx.send(f"Error while reloading i18n stuff: \n{ex}")



    @commands.command()
    async def snowflake(self, ctx, arg: int):
        try:
            dt_object = datetime.datetime.fromtimestamp((round(arg / 4194304 + 1420070400000) / 1000))
            await ctx.send(f"{dt_object}")
        except Exception as ex:
            await ctx.send(f"There was an error trying to convert this snowflake to a datetime object: \n```\n{ex}\n```")



def setup(bot):
    bot.add_cog(Admin(bot))