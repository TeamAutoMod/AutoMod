


async def removeTagFromCache(plugin, ctx, trigger):
    plugin.cached_tags[ctx.guild.id] = list(filter(lambda x: x["trigger"] != trigger, plugin.cached_tags[ctx.guild.id]))