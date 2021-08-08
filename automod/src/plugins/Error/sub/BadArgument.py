


def replace_lookalikes(text):
    for k, v in {"`": "ˋ"}.items():
        text = text.replace(k, v)
    return text


async def run(plugin, ctx, error):
    try:
        param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
    except Exception:
        return await ctx.send(f"{plugin.bot.emotes.get('NO')} There was an error trying to parse your given parameters.")
    plugin.bot.help_command.context = ctx
    usage = plugin.bot.help_command.get_command_signature(ctx.command)
    arg = param._name
    real_error = replace_lookalikes(str(error))
    await ctx.send(plugin.i18next.t(ctx.guild, "arg_parse_error", _emote="NO", arg=arg, error=real_error, usage=usage))
