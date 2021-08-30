from ....utils.Views import LinkView



async def run(plugin, ctx):
    view = LinkView(_guild=ctx.guild)
    await ctx.send(
        plugin.i18next.t(ctx.guild, "got_you", _emote="YES"), 
        view=view
    )
