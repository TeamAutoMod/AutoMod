


async def run(plugin, ctx):
    param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
    plugin.bot.help_command.context = ctx
    usage = plugin.bot.help_command.get_command_signature(ctx.command)
    #arg = param._name
    await ctx.send(plugin.t(ctx.guild, "missing_arg", _emote="NO", usage=usage))