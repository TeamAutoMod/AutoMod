


async def run(plugin, ctx):
    state = plugin.db.configs.get(ctx.guild.id, "show_mod_in_dm")
    state = not state
    plugin.db.configs.update(ctx.guild.id, "show_mod_in_dm", state)
    if state is False:
        return await ctx.send(plugin.i18next.t(ctx.guild, "show_mod_in_dm_false", _emote="YES"))
    else:
        return await ctx.send(plugin.i18next.t(ctx.guild, "show_mod_in_dm_true", _emote="YES"))