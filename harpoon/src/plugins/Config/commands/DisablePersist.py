


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "persist", False)
    await ctx.send(plugin.t(ctx.guild, "disabled_module", _emote="YES", module="Persist"))