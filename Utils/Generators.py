import collections

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