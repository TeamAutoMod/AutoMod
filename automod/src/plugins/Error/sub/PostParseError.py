from ...Types import Embed



async def run(plugin, ctx, error):
    plugin.bot.help_command.context = ctx
    usage = plugin.bot.help_command.get_command_signature(ctx.command)
    
    await ctx.send(plugin.i18next.t(ctx.guild, "bad_argument", _emote="NO", param=error.type, error=error.error, usage=usage))
