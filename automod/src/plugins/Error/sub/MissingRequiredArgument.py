from ...Types import Embed



async def run(plugin, ctx):
    param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
    plugin.bot.help_command.context = ctx
    usage = plugin.bot.help_command.get_command_signature(ctx.command)
    
    await ctx.send(plugin.i18next.t(ctx.guild, "missing_arg", _emote="NO", param=param._name, usage=usage))