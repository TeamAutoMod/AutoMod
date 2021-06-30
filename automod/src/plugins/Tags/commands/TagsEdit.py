import datetime

from ..functions.EditTag import editTag



async def run(plugin, ctx, tag, content):
    tag = tag.lower()
    tags = [x["id"].split("-")[1] for x in plugin.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]
    if len(tags) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_tags", _emote="NO"))

    _id = f"{ctx.guild.id}-{tag}"
    if not plugin.db.tags.exists(_id):
        return await ctx.send(plugin.t(ctx.guild, "tag_doesnt_exist", _emote="NO"))

    if len(content) > 1500:
        return await ctx.send(plugin.t(ctx.guild, "tag_content_too_long", _emote="NO"))

    await editTag(plugin, ctx, tag, content)

    await ctx.send(plugin.t(ctx.guild, "tag_edited", _emote="YES", tag=tag))