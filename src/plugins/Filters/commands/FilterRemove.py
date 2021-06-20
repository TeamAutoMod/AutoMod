


async def run(plugin, ctx, name):
    name = name.lower()
    filters = plugin.db.configs.get(ctx.guild.id, "filters")

    if len(filters) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_filters", _emote="WARN"))

    if name not in filters:
        return await ctx.send(plugin.t(ctx.guild, "filter_doesnt_exist", _emote="WARN"))
    
    del filters[name]
    plugin.db.configs.update(ctx.guild.id, "filters", filters)

    await ctx.send(plugin.t(ctx.guild, "filter_removed", _emote="YES", name=name))