from ...Types import Embed



async def run(plugin, ctx, error):
    param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
    plugin.bot.help_command.context = ctx
    usage = plugin.bot.help_command.get_command_signature(ctx.command)
    
    await ctx.send(plugin.i18next.t(ctx.guild, "bad_argument", _emote="NO", param=param._name, error=error, usage=usage))