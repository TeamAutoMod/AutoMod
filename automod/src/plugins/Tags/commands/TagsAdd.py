import datetime

from ..sub.AddTagToCache import addTagToCache



async def run(plugin, ctx, trigger, reply):
    trigger = trigger.lower()
    if len(trigger) > 20:
        return await ctx.send(plugin.t(ctx.guild, "trigger_too_long", _emote="NO"))

    if len(reply) > 700:
        return await ctx.send(plugin.t(ctx.guild, "reply_too_long", _emote="NO"))
    
    _id = f"{ctx.guild.id}-{trigger}"
    if plugin.db.tags.exists(_id):
        return await ctx.send(plugin.t(ctx.guild, "tag_already_exists", _emote="WARN"))

    plugin.db.tags.insert(plugin.schemas.Tag(_id, reply, ctx.author, datetime.datetime.utcnow()))
    await addTagToCache(plugin, ctx, trigger, reply)

    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    await ctx.send(plugin.t(ctx.guild, "tag_created", _emote="YES", prefix=prefix, tag=trigger))