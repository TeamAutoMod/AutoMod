import traceback

from ..sub.HelpGenerator import getHelpForAllCommands, getHelpForCommand
from ....utils.Views import HelpView
from ...Types import Embed



async def run(plugin, ctx, query):
    if query is None:
        e = Embed(
            title=plugin.i18next.t(ctx.guild, "help_title"),
            description=plugin.i18next.t(ctx.guild, "help_description", prefix=plugin.bot.get_guild_prefix(ctx.guild))
        )
        e.set_image(
            url="https://cdn.discordapp.com/attachments/874097242598961152/883736333389004821/banner_.png"
        )
        view = HelpView(ctx.guild, plugin.bot, "None")
        await ctx.send(embed=e, view=view)
    else:
        query = "".join(query.splitlines())

        help_message = await getHelpForCommand(plugin, ctx, query)
        if help_message is None:
            return await ctx.send(plugin.i18next.t(ctx.guild, "invalid_command", _emote="NO"))
        else:
            await ctx.send(embed=help_message)