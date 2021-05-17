


async def run(plugin, ctx, error):
    plugin.bot.help_command.context = ctx
    usage = plugin.bot.help_command.get_command_signature(ctx.command)
    arg = error.type
    real_error = error.error
    await ctx.send(plugin.t(ctx.guild, "arg_parse_error", _emote="NO", arg=arg, error=real_error, usage=usage))