from ...Types import Embed
from ..Types import arg_ex



async def run(plugin, ctx, error):
    plugin.bot.help_command.context = ctx
    usage = plugin.bot.help_command.get_command_signature(ctx.command)
    e = Embed(
        title="Invalid command argument",
        color=0xff5c5c
    )
    e.add_field(
        name="❯ Usage",
        value=f"``{usage}``"
    )
    e.add_field(
        name="❯ Arguments",
        value="\n".join(f"``{x.name}`` - *{arg_ex[x.name]}*" for x in list(ctx.command.params.values())[2:])
    )
    await ctx.send(embed=e)
