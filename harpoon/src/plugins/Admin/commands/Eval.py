import discord
from discord.ext import commands

import ast
import traceback



def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


async def run(plugin, ctx, cmd):
    try:
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
            "db": plugin.bot.db,
            "bot": plugin.bot,
            "client": plugin.bot,
            "discord": discord,
            "commands": commands,
            "__import__": __import__
        }

        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))

        await ctx.message.add_reaction(plugin.bot.emotes.get("YES"))
        await ctx.send("```py\n{}\n```".format(result))
    except Exception:
        ex = traceback.format_exc()
        await ctx.message.add_reaction(plugin.bot.emotes.get("NO"))
        await ctx.send("```py\n{}\n```".format(ex))