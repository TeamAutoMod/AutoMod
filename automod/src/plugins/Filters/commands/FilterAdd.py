


async def run(plugin, ctx, name, warns, words):
    name = name.lower()
    filters = plugin.db.configs.get(ctx.guild.id, "filters")

    if len(name) > 30:
        return await ctx.send(plugin.t(ctx.guild, "name_too_long", _emote="WARN"))

    if name in filters:
        return await ctx.send(plugin.t(ctx.guild, "filter_exists", _emote="WARN"))
    
    if warns < 1:
        return await ctx.send(plugin.t(ctx.guild, "min_warns", _emote="WARN"))

    if warns > 100:
        return await ctx.send(plugin.t(ctx.guild, "max_warns", _emote="WARN"))

    new_filter = {
        "warns": warns,
        "words": words.split(" ")
    }
    filters[name] = new_filter
    plugin.db.configs.update(ctx.guild.id, "filters", filters)

    await ctx.send(plugin.t(ctx.guild, "filter_added", _emote="YES", name=name))