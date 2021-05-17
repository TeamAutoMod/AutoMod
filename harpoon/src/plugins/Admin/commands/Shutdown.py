


async def run(plugin, ctx):
    await ctx.send(f"{plugin.emotes.get('SLEEP')} Executing clean shutdown")
    await plugin.bot.utils.cleanShutdown()