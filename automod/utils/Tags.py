import datetime



def addTagToCache(plugin, ctx, trigger, reply):
    try:
        plugin.cached_tags[ctx.guild.id].append({"trigger": trigger, "reply": reply})
    except KeyError:
        plugin.cached_tags[ctx.guild.id] = [{"trigger": trigger, "reply": reply}]


def editTag(plugin, ctx, tag, content):
    try:
        removeTagFromCache(plugin, ctx, tag)
        addTagToCache(plugin, ctx, tag, content)
    except Exception:
        pass
    finally:
        _id = f"{ctx.guild.id}-{tag}"
        plugin.db.tags.update(_id, "reply", f"{content}")
        plugin.db.tags.update(_id, "last_edited", datetime.datetime.utcnow())
        plugin.db.tags.update(_id, "edited_by", f"{ctx.message.author.id}")


def getTags(plugin, message):
    global tags
    tags = []
    try:
        tags = plugin.cached_tags[message.guild.id]
    except KeyError:
        _tags = [x for x in plugin.db.tags.find({}) if x["id"].split("-")[0] == str(message.guild.id)]
        tags = [{"trigger": "-".join(x["id"].split("-")[1:]), "reply": x["reply"]} for x in _tags]
    finally:
        return tags


def removeTagFromCache(plugin, ctx, trigger):
    plugin.cached_tags[ctx.guild.id] = list(filter(lambda x: x["trigger"] != trigger, plugin.cached_tags[ctx.guild.id]))