from ...Types import Embed



async def run(plugin, ctx):
    tags = ["-".join(x["id"].split("-")[1:]) for x in plugin.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]

    if len(tags) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_tags", _emote="NO"))

    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    e = Embed()
    e.add_field(
        name="❯ Tags",
        value=", ".join([f"``{prefix}{x}``" for x in tags])
    )
    await ctx.send(embed=e)