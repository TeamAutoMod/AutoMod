


async def run(plugin, ctx):
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    await ctx.send(plugin.i18next.t(ctx.guild, "setup_commands", prefix=prefix))