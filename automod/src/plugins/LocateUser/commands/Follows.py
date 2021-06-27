from ...Types import Embed



async def run(plugin, ctx):
    _id = f"{ctx.guild.id}-{ctx.author.id}"
    if not plugin.db.follows.exists(_id):
        return await ctx.send(plugin.t(ctx.guild, "no_follows", _emote="NO"))

    follows = [f"``{x}``" for x in plugin.db.follows.get(_id, "users")]
    if len(follows) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_follows", _emote="NO"))

    e = Embed()
    e.add_field(
        name="❯ Active alerts", 
        value=", ".join(follows)
    )
    
    await ctx.send(embed=e)