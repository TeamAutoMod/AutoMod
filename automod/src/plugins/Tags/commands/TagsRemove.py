from ..functions.RemoveTagFromCache import removeTagFromCache



async def run(plugin, ctx, trigger):
    trigger = trigger.lower()

    tags = ["-".join(x["id"].split("-")[1:]) for x in plugin.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]
    if len(tags) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_tags", _emote="NO"))

    _id = f"{ctx.guild.id}-{trigger}"
    if not plugin.db.tags.exists(_id):
        return await ctx.send(plugin.t(ctx.guild, "tag_doesnt_exist", _emote="NO"))

    plugin.db.tags.delete(_id)
    await removeTagFromCache(plugin, ctx, trigger)

    await ctx.send(plugin.t(ctx.guild, "tag_deleted", _emote="YES"))