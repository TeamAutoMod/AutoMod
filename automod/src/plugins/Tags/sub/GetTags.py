


async def getTags(plugin, message):
    global tags
    tags = []
    try:
        tags = plugin.cached_tags[message.guild.id]
    except KeyError:
        _tags = [x for x in plugin.db.tags.find({}) if x["id"].split("-")[0] == str(message.guild.id)]
        tags = [{"trigger": "-".join(x["id"].split("-")[1:]), "reply": x["reply"]} for x in _tags]
    finally:
        return tags