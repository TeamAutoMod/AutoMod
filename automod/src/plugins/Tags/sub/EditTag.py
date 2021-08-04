import datetime

from .AddTagToCache import addTagToCache
from .RemoveTagFromCache import removeTagFromCache



async def editTag(plugin, ctx, tag, content):
    try:
        await removeTagFromCache(plugin, ctx, tag)
        await addTagToCache(plugin, ctx, tag, content)
    except Exception:
        pass
    finally:
        _id = f"{ctx.guild.id}-{tag}"
        plugin.db.tags.update(_id, "reply", f"{content}")
        plugin.db.tags.update(_id, "last_edited", datetime.datetime.utcnow())
        plugin.db.tags.update(_id, "edited_by", f"{ctx.message.author.id}")