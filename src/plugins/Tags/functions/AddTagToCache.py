


async def addTagToCache(plugin, ctx, trigger, reply):
    try:
        plugin.cached_tags[ctx.guild.id].append({"trigger": trigger, "reply": reply})
    except KeyError:
        plugin.cached_tags[ctx.guild.id] = [{"trigger": trigger, "reply": reply}]