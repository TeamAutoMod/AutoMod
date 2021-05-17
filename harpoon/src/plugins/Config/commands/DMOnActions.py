


async def run(plugin, ctx):
    state = plugin.db.configs.get(ctx.guild.id, "dm_on_actions")
    state = not state
    plugin.db.configs.update(ctx.guild.id, "dm_on_actions", state)
    if state is False:
        return await ctx.send(plugin.t(ctx.guild, "dm_on_actions_false", _emote="YES"))
    else:
        return await ctx.send(plugin.t(ctx.guild, "dm_on_actions_true", _emote="YES"))