import traceback

from ....utils.MessageUtils import multiPage
from ..functions.HelpGenerator import getHelpForAllCommands, getHelpForCommand



async def run(plugin, ctx, query):
    if query is None:
        help_embed = await getHelpForAllCommands(plugin, ctx)
        try:
            await ctx.author.send(embed=help_embed)
        except Exception:
            await ctx.send(embed=help_embed)
        else:
            await ctx.message.add_reaction(plugin.bot.emotes.get("YES"))
    else:
        query = "".join(query.splitlines())

        help_message = await getHelpForCommand(plugin, ctx, query)
        if help_message is None:
            return await ctx.send(plugin.t(ctx.guild, "invalid_command"))
        else:
            try:
                await ctx.author.send(embed=help_message)
            except Exception:
                await ctx.send(embed=help_message)
            else:
                await ctx.message.add_reaction(plugin.bot.emotes.get("YES"))