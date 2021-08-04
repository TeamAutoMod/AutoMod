import traceback

from ....utils.MessageUtils import multiPage
from ..sub.HelpGenerator import getHelpForAllCommands, getHelpForCommand



async def run(plugin, ctx, query):
    if query is None:
        help_embed = await getHelpForAllCommands(plugin, ctx)
        await ctx.send(embed=help_embed)
    else:
        query = "".join(query.splitlines())

        help_message = await getHelpForCommand(plugin, ctx, query)
        if help_message is None:
            return await ctx.send(plugin.t(ctx.guild, "invalid_command", _emote="NO"))
        else:
            await ctx.send(embed=help_message)