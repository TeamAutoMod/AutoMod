


async def run(plugin, ctx, name, warns, words):
    name = name.lower()
    filters = plugin.db.configs.get(ctx.guild.id, "filters")

    if len(name) > 30:
        return await ctx.send(plugin.i18next.t(ctx.guild, "name_too_long", _emote="NO"))

    if name in filters:
        return await ctx.send(plugin.i18next.t(ctx.guild, "filter_exists", _emote="WARN"))
    
    if warns < 1:
        return await ctx.send(plugin.i18next.t(ctx.guild, "min_warns", _emote="NO"))

    if warns > 100:
        return await ctx.send(plugin.i18next.t(ctx.guild, "max_warns", _emote="NO"))

    new_filter = {
        "warns": warns,
        "words": words.split(", ")
    }
    filters[name] = new_filter
    plugin.db.configs.update(ctx.guild.id, "filters", filters)

    await ctx.send(plugin.i18next.t(ctx.guild, "filter_added", _emote="YES", name=name))