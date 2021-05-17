


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "automod", False)
    await ctx.send(plugin.translator.translate(ctx.guild, "disabled_module", _emote="YES", module="Automod"))