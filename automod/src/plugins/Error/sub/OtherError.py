import traceback

from ...Types import Embed



async def run(plugin, ctx, error):
    e = Embed(
        color=0xff5c5c,
        title="❯ Command Error",
        description="```py\n{}\n```".format("".join(
            traceback.format_exception(
                etype=type(error), 
                value=error, 
                tb=error.__traceback__
            )
        ))
    )
    e.add_field(
        name="❯ Location",
        value="• Name: {} \n• ID: {}".format(
            ctx.guild.name or "None",
            ctx.guild.id or "None"
        )
    )
    await plugin.bot.utils.sendErrorLog(e)
