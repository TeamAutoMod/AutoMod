import asyncio



async def cacheTags(plugin):
    while len(plugin.cached_tags) < len(list(plugin.db.tags.find({}))):
        await asyncio.sleep(2)
        for e in plugin.db.tags.find({}):
            guild_id = int(e["id"].split("-")[0])
            trigger = e["id"].split("-")[1]
            reply = e["reply"]
            if not guild_id in plugin.cached_tags:
                plugin.cached_tags[guild_id] = [{"trigger": trigger, "reply": reply}]
            else:
                if not trigger in [x["trigger"] for x in plugin.cached_tags[guild_id]]:
                    plugin.cached_tags[guild_id].append({"trigger": trigger, "reply": reply})
                else:
                    pass