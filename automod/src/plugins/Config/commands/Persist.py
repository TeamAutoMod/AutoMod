


async def run(plugin, ctx):
    state = plugin.db.configs.get(ctx.guild.id, "persist")
    state = not state
    plugin.db.configs.update(ctx.guild.id, "persist", state)
    if state is False:
        return await ctx.send(plugin.i18next.t(ctx.guild, "persist_False", _emote="YES"))
    else:
        return await ctx.send(plugin.i18next.t(ctx.guild, "persist_true", _emote="YES"))