


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "persist", False)
    await ctx.send(plugin.translator.translate(ctx.guild, "disabled_module", _emote="YES", module="Persist"))