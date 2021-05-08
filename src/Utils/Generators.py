import collections

import discord
from discord.ext.commands import CommandError, Context, GroupMixin, Group

from i18n import Translator
from Utils import Logging, Pages

from Database import Connector, DBUtils


db = Connector.Database()





async def generate_help_pages(ctx, bot):
    pages = []
    out = []
    valid_cogs = [c for c in bot.cogs if not str(c) in ["Admin", "AntiSpam", "Censor", "GlobalListeners"]]
    for cog in valid_cogs:
        commands = ["  {}{}{}".format(x.name, " "*abs(18 - len(x.name)), Translator.translate(ctx.guild, x.short_doc)) for x in bot.get_cog(cog).get_commands() if x.hidden is False]
        output = f"[ {cog} ]\n" + "\n".join(commands) + "\n"
        out.append(output)
    for page in Pages.paginate("{}".format("\n".join(out)), prefix="```ini\n", suffix=Translator.translate(ctx.guild, "help_suffix", prefix=DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "prefix"))):
        pages.append(page)
    return pages



def generate_help(ctx, command):
    help_message = Translator.translate(ctx.guild, command.short_doc)
    return "  {}{}{}".format(command.name, " "*abs(18 - len(command.name)), help_message)


def generate_command_help(bot, ctx, command):
    bot.help_command.context = ctx
    usage = ctx.bot.help_command.get_command_signature(command)
    help_message = Translator.translate(ctx.guild, f"{command.help}")
    
    e = discord.Embed(color=discord.Color.blurple(), title="Command Help")
    e.add_field(name="Description", value=f"```\n{help_message}\n```", inline=False)
    e.add_field(name="Usage", value=f"```\n{usage}\n```", inline=False)

    commands = []
    if isinstance(command, GroupMixin) and hasattr(command, "all_commands"):
        commands = [x.name for x in command.all_commands.values()]
    e.add_field(name="Subcommands", value="```\n{}\n```".format("\n".join(commands) if len(commands) > 0 else "None"), inline=False)

    return e



def get_command_help_embed(bot, ctx, query):
    t = bot
    layers = query.split(" ")
    while len(layers) > 0:
        layer = layers.pop(0)
        if hasattr(t, "all_commands") and layer in t.all_commands.keys():
            t = t.all_commands[layer]
        else:
            t = None
            break
    if t is not None and t is not bot.all_commands:
        return generate_command_help(bot, ctx, t)
    return None