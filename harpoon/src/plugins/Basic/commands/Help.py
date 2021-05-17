import traceback

from ....utils.MessageUtils import multiPage
from ..functions.HelpGenerator import getHelpForAllCommands, getHelpForCommand



async def run(plugin, ctx, query):
    if query is None:
        pages = await getHelpForAllCommands(plugin, ctx)
        msg = await ctx.send(embed=pages[0])
        while True:
            res = await multiPage(plugin, ctx, msg, pages)
            if res is None:
                break
    else:
        query = "".join(query.splitlines())

        help_message = await getHelpForCommand(plugin, ctx, query)
        if help_message is None:
            return await ctx.send(plugin.t(ctx.guild, "invalid_command"))
        else:
            return await ctx.send(embed=help_message)