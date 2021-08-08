import humanize
import datetime

from ...Types import Embed



async def run(plugin, ctx, tag):
    tag = tag.lower()
    tags = ["-".join(x["id"].split("-")[1:]) for x in plugin.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]
    if len(tags) < 1:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_tags", _emote="NO"))

    _id = f"{ctx.guild.id}-{tag}"
    if not plugin.db.tags.exists(_id):
        return await ctx.send(plugin.i18next.t(ctx.guild, "tag_doesnt_exist", _emote="NO"))

    entry = plugin.db.tags.get_doc(_id)
    e = Embed()
    e.add_field(
        name="❯ Name",
        value=f"``{tag}``"
    )

    user = await plugin.bot.utils.getUser(int(entry["author"]))
    e.add_field(
        name="❯ User",
        value=f"``{user if user is not None else 'Unknown#0000'}`` ({entry['author']})"
    )
    e.add_field(
        name="❯ Uses",
        value=f"{entry['uses']}"
    )
    e.add_field(
        name="❯ Created",
        value=f"``{entry['created'].strftime('%Y-%m-%d %H:%M:%S')}`` ({humanize.naturaldelta((datetime.datetime.utcnow() - entry['created']))} ago)"
    )

    if entry["last_edited"] is not None:
        e.add_field(
            name="❯ Last edited",
            value=f"``{entry['last_edited'].strftime('%Y-%m-%d %H:%M:%S')}`` ({humanize.naturaldelta((datetime.datetime.utcnow() - entry['last_edited']))} ago)"
        )
        editor = await plugin.bot.utils.getUser(int(entry["edited_by"]))
        e.add_field(
            name="❯ Last edited by",
            value=f"``{editor if editor is not None else 'Unknown#0000'}`` ({entry['edited_by']})"
        )
    
    await ctx.send(embed=e)
